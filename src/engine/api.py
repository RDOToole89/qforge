"""Engine API facade.

Stable, **documented** entry points for running single experiments and parameter sweeps.

# What this module is
This is the *one* module your CLI/Service/UI should call to execute experiments.
It orchestrates:
    (1) config validation (Pydantic) ➜
    (2) circuit execution via the engine runner ➜
    (3) result canonicalization (counts) ➜
    (4) typed analysis assembly (ExperimentAnalysis) ➜
    (5) optional analysis metrics computation ➜
    (6) provenance + storage (persist analysis JSON) ➜
    (7) optional visualization (histogram) ➜
    (8) packaged ExperimentResult (and list thereof for sweeps)

# Why it exists
It provides a single, stable API surface decoupled from lower-level pieces
(Qiskit runner, metrics registry, renderers, storage implementation).
This keeps your experiment code, CLI, and future UI small and consistent.

# Key functions
- run(config, ctx=None) -> ExperimentResult
    Execute *one* experiment from an ExperimentConfig (or dict).
- sweep(manifest, ctx=None) -> List[ExperimentResult]
    Execute a Cartesian parameter sweep (simple driver).
- iter_experiment_configs(manifest) -> Iterator[ExperimentConfig]
    Generator that yields concrete ExperimentConfig instances for each
    parameter combination (useful for custom drivers, parallelization, etc.).

# Optional features
- Histogram rendering is **optional**. It will only run if:
    (a) config.visualization_type == "histogram", and
    (b) the visualization package is importable, and
    (c) counts exist.
  Otherwise it is silently skipped and the rest of the pipeline is unaffected.

# Event hooks
We publish RUN_START/RUN_END and SWEEP_START/SWEEP_END via a SimpleEventBus
so you can attach logging, telemetry, or progress UIs without changing logic.

# Invariants / Contracts
- Always returns a typed ExperimentResult (Pydantic validated).
- The `analysis` field is a fully-typed ExperimentAnalysis, not a loose dict.
- The `metrics_bundle` field is only present if `config.metrics` requested
  metrics and counts were extracted.

"""

from __future__ import annotations

import logging
from collections import Counter
from collections.abc import Iterator
from datetime import datetime
from typing import Any

from qiskit import QuantumCircuit

# Version helper
from src.engine._version_util import get_version

# Analysis integration (counts canonicalization + metrics bundle)
from src.engine.analysis import compute_metrics_bundle, extract_counts_from_result

# App plumbing
from src.engine.execution.context import AppContext
from src.engine.execution.runner import run_raw
from src.engine.fidelity import extract_simulation_data

# Event bus (optional, cheap)
from src.engine.infrastructure.events import (
    ALL,
    RUN_END,
    RUN_START,
    SWEEP_END,
    SWEEP_START,
    SimpleEventBus,
    make_event,
)
from src.engine.infrastructure.logging import event_log_handler

# Typed models
from src.engine.models import (
    ArtifactRef,
    CircuitStatistics,
    ExperimentAnalysis,
    ExperimentConfig,
    ExperimentMetadata,
    ExperimentResult,
    MeasurementResults,
    SweepManifest,
)
from src.engine.persistence.hashing import sha1_of

# Storage adapter
from src.engine.persistence.storage import LocalStorage
from src.engine.provenance import build_provenance
from src.engine.viz_pipeline import render_visualizations

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public API: single experiment
# ---------------------------------------------------------------------------


def run(
    config: ExperimentConfig | dict[str, Any],
    ctx: AppContext | None = None,
    _hardware_session: Any = None,
) -> ExperimentResult:
    """Run a single experiment and return a validated `ExperimentResult`.

    High-level orchestration (single shot):
    1) Validate/normalize config (Pydantic).
    2) Execute circuit (engine runner -> Qiskit backend).
    3) Extract canonical counts (MSB-left, fixed width).
    4) Assemble a *typed* ExperimentAnalysis (metadata, circuit stats, measurements).
    5) Optionally compute analysis metrics (per `config.metrics`).
    6) Build provenance and persist the analysis JSON to disk.
    7) Optionally render a histogram and attach as `ArtifactRef`.
    8) Package everything into an ExperimentResult (Pydantic-validated).

    Parameters
    ----------
    config : ExperimentConfig | Dict[str, Any]
        Either a fully-typed ExperimentConfig or a plain dict (will be parsed).
    ctx : Optional[AppContext]
        Execution context (base results directory, env). A default is created if omitted.

    Returns:
    -------
    ExperimentResult
        Complete, validated result object with typed `analysis`, optional
        `metrics_bundle`, `provenance`, and `artifacts`.

    Notes:
    -----
    - Rendering is optional and non-fatal. If visualization deps are missing,
      or the viz layer cannot handle the payload, we warn and continue.
    - The returned `ExperimentResult.analysis` is a Pydantic object, not a dict.
      If you need a dict (for JSON), call `.model_dump()`.
    """
    ctx = ctx or AppContext()
    cfg_model = config if isinstance(config, ExperimentConfig) else ExperimentConfig(**config)

    # Publish start event (useful for progress bars / logs)
    bus = SimpleEventBus()
    bus.subscribe(ALL, event_log_handler)
    bus.publish(make_event(RUN_START, {"config": cfg_model.model_dump(exclude_none=True)}))

    # 1) Execute experiment via runner
    import time as _time

    _t0 = _time.monotonic()
    raw_config = cfg_model.model_dump()
    if _hardware_session is not None:
        raw_config["_hardware_session"] = _hardware_session
    circuit, raw = run_raw(raw_config)
    _exec_seconds = _time.monotonic() - _t0

    # 2) Canonicalize counts (MSB-left, fixed bit-width)
    counts = extract_counts_from_result(raw, num_qubits=cfg_model.num_qubits)

    # 2b) Extract simulation-specific data (statevector, density matrix, fidelity)
    sim_density_matrix, sim_statevector, sim_fidelity = extract_simulation_data(
        raw, cfg_model.sim_mode, cfg_model.state_type, cfg_model.num_qubits
    )

    # 3) Assemble typed analysis block
    analysis = _build_experiment_analysis(
        circuit=circuit,
        counts=counts,
        cfg=cfg_model,
        density_matrix=sim_density_matrix,
        statevector=sim_statevector,
        fidelity=sim_fidelity,
    )

    # 4) Optional: compute analysis metrics
    metrics_bundle = None
    if cfg_model.metrics is not None and counts:
        metrics_bundle = compute_metrics_bundle(counts, cfg_model)

    # 5) Build provenance (enrich with hardware metadata if applicable)
    hardware_metadata = None
    if cfg_model.sim_mode == "hardware" and isinstance(raw, dict):
        hw_result = raw.get("hardware_result")
        if hw_result is not None:
            hardware_metadata = {"hardware_result": hw_result}

    prov = build_provenance(
        cfg_model,
        execution_time_seconds=round(_exec_seconds, 4),
        hardware_metadata=hardware_metadata,
    )

    # 6) Persist analysis to disk (deterministic path via config hash)
    cfg_hash = sha1_of(cfg_model.model_dump(exclude_none=True))[:8]
    storage = LocalStorage(base_dir=ctx.base_results_dir)
    saved_path = storage.save_analysis(analysis.model_dump())

    artifacts: list[ArtifactRef] = [ArtifactRef(kind="analysis", path=saved_path, metadata={})]

    # 7) Visualization (multi-type, multi-format)
    artifacts.extend(render_visualizations(cfg_model, analysis, metrics_bundle, saved_path))

    # 8) Package final typed result
    result = ExperimentResult(
        analysis=analysis,
        metrics_bundle=metrics_bundle,
        provenance=prov,
        artifacts=artifacts,
        config_hash=cfg_hash,
        timestamp=_now_iso(),
        status="completed",
    )

    # Publish end event
    bus.publish(
        make_event(
            RUN_END,
            {"config_hash": cfg_hash, "artifacts": [a.path for a in artifacts]},
        )
    )
    return result


# ---------------------------------------------------------------------------
# Public API: parameter sweep (simple Cartesian driver)
# ---------------------------------------------------------------------------


def sweep(
    manifest: SweepManifest | dict[str, Any],
    ctx: AppContext | None = None,
) -> list[ExperimentResult]:
    """Run a parameter sweep and return a list of `ExperimentResult`.

    This is a **simple** Cartesian sweep driver:
    - Expands `parameter_ranges` in a stable (sorted key) order.
    - Merges each combination over the `base_config` plus `override`.
    - Runs experiments sequentially via `run()` and aggregates results.

    Parameters
    ----------
    manifest : SweepManifest | Dict[str, Any]
        Sweep specification: base config (or preset), parameter ranges,
        runs per config, optional overrides, etc.
    ctx : Optional[AppContext]
        Execution context. A default is created if omitted.

    Returns:
    -------
    List[ExperimentResult]
        A flat list of results, one per realized configuration (× runs).

    See Also:
    --------
    iter_experiment_configs : yields the concrete `ExperimentConfig`s used.
    """
    ctx = ctx or AppContext()
    man = manifest if isinstance(manifest, SweepManifest) else SweepManifest(**manifest)

    base = man.base_config.model_dump(exclude_none=True) if man.base_config else {}
    results: list[ExperimentResult] = []
    keys = sorted((man.parameter_ranges or {}).keys())

    bus = SimpleEventBus()
    bus.subscribe(ALL, event_log_handler)
    total = _product_len(man.parameter_ranges)
    bus.publish(make_event(SWEEP_START, {"keys": keys, "total": total}))

    # Determine if this is a hardware sweep that should use Sessions
    _use_hw_session = base.get("sim_mode") == "hardware" and base.get("hardware_session", False)

    hw_session = None

    # Cartesian expansion (depth-first), honoring stable key order
    def _expand(idx: int, acc: dict[str, Any]) -> None:
        if idx == len(keys):
            # Merge: base + override + accumulated parameter choices
            i = len(results)
            bus.publish_progress(fraction=i / total, message=f"Running {i + 1}/{total}")
            cfg = {**base, **(man.override or {}), **acc}
            results.append(run(cfg, ctx, _hardware_session=hw_session))
            return
        key = keys[idx]
        for value in man.parameter_ranges[key]:
            acc[key] = value
            _expand(idx + 1, acc)
        acc.pop(key, None)

    if _use_hw_session:
        from src.engine.execution.hardware import create_session, resolve_backend

        backend = resolve_backend(
            backend_name=base.get("backend_name"),
            min_qubits=int(base.get("num_qubits", 1)),
        )
        hw_session = create_session(backend)
        with hw_session:
            _expand(0, {})
    else:
        _expand(0, {})

    bus.publish(make_event(SWEEP_END, {"count": len(results)}))
    return results


# ---------------------------------------------------------------------------
# Public helper: iterate realized ExperimentConfigs (useful “sweep driver” core)
# ---------------------------------------------------------------------------


def iter_experiment_configs(
    manifest: SweepManifest | dict[str, Any],
) -> Iterator[ExperimentConfig]:
    """Yield concrete `ExperimentConfig` instances for a Cartesian sweep.

    This is a pure generator that expands the sweep and yields fully-typed
    ExperimentConfigs. It is useful if you want to:
      * Run on a custom scheduler/pool (e.g., multiprocessing, Slurm).
      * Distribute runs across machines.
      * Add custom pre/post hooks around each config.

    Example:
    -------
    >>> for cfg in iter_experiment_configs(manifest):
    ...     submit_to_pool(lambda: run(cfg))

    Parameters
    ----------
    manifest : SweepManifest | Dict[str, Any]
        Sweep specification (typed or dict).

    Yields:
    ------
    ExperimentConfig
        Fully-typed configuration for each parameter combination (× runs).
    """
    man = manifest if isinstance(manifest, SweepManifest) else SweepManifest(**manifest)
    base = man.base_config.model_dump(exclude_none=True) if man.base_config else {}
    keys = sorted((man.parameter_ranges or {}).keys())

    def _expand(idx: int, acc: dict[str, Any]) -> Iterator[ExperimentConfig]:
        if idx == len(keys):
            merged = {**base, **(man.override or {}), **acc}
            # Yield N copies if runs_per_config > 1 (vary rng_seed if set)
            for r in range(man.runs_per_config):
                cfg_dict = dict(merged)
                if man.rng_seed is not None:
                    cfg_dict["rng_seed"] = int(man.rng_seed) + r
                yield ExperimentConfig(**cfg_dict)
            return
        key = keys[idx]
        for value in man.parameter_ranges[key]:
            acc[key] = value
            yield from _expand(idx + 1, acc)
        acc.pop(key, None)

    yield from _expand(0, {})


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    return datetime.now().isoformat()


def _product_len(d: dict[str, list[Any]]) -> int:
    total = 1
    for v in (d or {}).values():
        total *= len(v)
    return total


def _build_experiment_analysis(
    *,
    circuit: QuantumCircuit,
    counts: dict[str, int],
    cfg: ExperimentConfig,
    density_matrix: list[list[list[float]]] | None = None,
    statevector: list[list[float]] | None = None,
    fidelity: float | None = None,
) -> ExperimentAnalysis:
    """Construct a strongly-typed `ExperimentAnalysis` from circuit + counts + config.

    This method fills:
      - ExperimentMetadata: id, timestamp, engine version, experiment type
      - CircuitStatistics: depth, gate counts, two-qubit counts
      - MeasurementResults: raw counts, total shots, unique outcomes, probabilities,
        plus optional density_matrix, statevector, fidelity from non-qasm modes.

    It intentionally leaves optional advanced sections (IT metrics, correlations,
    validation) as None to keep responsibilities separated (other subsystems can
    populate them later if/when needed).
    """
    # ----- metadata -----
    meta = ExperimentMetadata(
        experiment_id=f"{cfg.state_type}_{cfg.num_qubits}",
        timestamp=_now_iso(),
        framework_version=get_version(),
        experiment_type=cfg.experiment_type,
        experiment_description=None,
    )

    # ----- parameters (raw cfg as dict for transparency) -----
    params = cfg.model_dump(exclude_none=True)

    # ----- circuit statistics -----
    # Qiskit changed Instruction containers over versions; handle both.
    try:
        gate_names = [inst.operation.name for inst in circuit.data]  # qiskit >= 0.45
        two_qubit_gates = sum(1 for inst in circuit.data if len(inst.qubits) == 2)
    except Exception:
        gate_names = [inst[0].name for inst in circuit.data]  # older qiskit
        two_qubit_gates = sum(1 for inst in circuit.data if len(inst[1]) == 2)

    gate_types = dict(Counter(gate_names))

    cstats = CircuitStatistics(
        depth=circuit.depth(),
        num_gates=len(circuit.data),
        num_qubits=circuit.num_qubits,
        gate_types=gate_types,
        two_qubit_gate_count=two_qubit_gates,
        connectivity_graph=None,  # optional; fill if you compute elsewhere
    )

    # ----- measurement results -----
    total_shots = int(sum(counts.values())) if counts else 0
    unique_outcomes = int(len(counts)) if counts else 0
    outcome_probabilities = (
        {k: v / total_shots for k, v in counts.items()} if total_shots > 0 else {}
    )

    # Pydantic fields require >=1 for shots/outcomes; ensure non-empty fallbacks.
    mres = MeasurementResults(
        raw_counts=counts if counts else {("0" * cfg.num_qubits): 0},
        total_shots=total_shots or 1,
        unique_outcomes=unique_outcomes or 1,
        outcome_probabilities=(
            outcome_probabilities if outcome_probabilities else {("0" * cfg.num_qubits): 1.0}
        ),
        density_matrix=density_matrix,
        statevector=statevector,
        fidelity=fidelity,
    )

    return ExperimentAnalysis(
        experiment_metadata=meta,
        experiment_parameters=params,
        circuit_statistics=cstats,
        measurement_results=mres,
        information_theory_metrics=None,
        correlation_analysis=None,
        statistical_validation=None,
    )
