"""Engine API facade.

Stable, **documented** entry points for running single experiments and parameter sweeps.

# What this module is
This is the *one* module your CLI/Service/UI should call to execute experiments.
It orchestrates:
    (1) config validation (Pydantic) ➜
    (2) circuit execution via the engine runner ➜
    (3) result canonicalization (counts) ➜
    (4) typed analysis assembly (ExperimentAnalysis) ➜
    (5) optional research metrics computation ➜
    (6) provenance + storage (persist analysis JSON) ➜
    (7) optional visualization (histogram) ➜
    (8) packaged ExperimentResult (and list thereof for sweeps)

# Why it exists
It provides a single, stable API surface decoupled from lower-level pieces
(Qiskit runner, metrics registry, renderers, storage implementation).
This keeps your research code, CLI, and future UI small and consistent.

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
- The `structured_decoherence_metrics` field is only present if
  `enable_research_metrics=True` in the config and counts were extracted.

"""

from __future__ import annotations

from typing import Optional, List, Dict, Any, Iterator
from datetime import datetime
import logging
import os
from collections import Counter

from qiskit import QuantumCircuit

# App plumbing
from src.engine.context import AppContext
from src.engine.runner import run_raw
from src.engine.hashing import sha1_of

# Typed models (top-level exports) …
from src.engine.models import (
    ExperimentConfig,
    ExperimentResult,
    Provenance,
    SweepManifest,
    ArtifactRef,
)

# … and result sub-types (declared in results.py)
from src.engine.models.results import (
    ExperimentAnalysis,
    ExperimentMetadata,
    CircuitStatistics,
    MeasurementResults,
)

# Research integration (counts canonicalization + research metrics)
from src.engine.analysis import compute_research_metrics, extract_counts_from_result

# Event bus (optional, cheap)
from src.engine.events import (
    SimpleEventBus,
    make_event,
    RUN_START,
    RUN_END,
    SWEEP_START,
    SWEEP_END,
)

# Storage adapter
from src.engine.storage import LocalStorage

# Optional visualization (gracefully skipped if not installed)
try:
    from src.engine.visualization import create_default_service
except Exception:
    create_default_service = None  # type: ignore

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public API: single experiment
# ---------------------------------------------------------------------------


def run(
    config: ExperimentConfig | Dict[str, Any],
    ctx: Optional[AppContext] = None,
) -> ExperimentResult:
    """Run a single experiment and return a validated `ExperimentResult`.

    High-level orchestration (single shot):
    1) Validate/normalize config (Pydantic).
    2) Execute circuit (engine runner -> Qiskit backend).
    3) Extract canonical counts (MSB-left, fixed width).
    4) Assemble a *typed* ExperimentAnalysis (metadata, circuit stats, measurements).
    5) Optionally compute structured-decoherence research metrics.
    6) Build provenance and persist the analysis JSON to disk.
    7) Optionally render a histogram and attach as `ArtifactRef`.
    8) Package everything into an ExperimentResult (Pydantic-validated).

    Parameters
    ----------
    config : ExperimentConfig | Dict[str, Any]
        Either a fully-typed ExperimentConfig or a plain dict (will be parsed).
    ctx : Optional[AppContext]
        Execution context (base results directory, env). A default is created if omitted.

    Returns
    -------
    ExperimentResult
        Complete, validated result object with typed `analysis`, optional
        `structured_decoherence_metrics`, `provenance`, and `artifacts`.

    Notes
    -----
    - Rendering is optional and non-fatal. If visualization deps are missing,
      or the viz layer cannot handle the payload, we warn and continue.
    - The returned `ExperimentResult.analysis` is a Pydantic object, not a dict.
      If you need a dict (for JSON), call `.model_dump()`.
    """
    ctx = ctx or AppContext()
    cfg_model = (
        config if isinstance(config, ExperimentConfig) else ExperimentConfig(**config)
    )

    # Publish start event (useful for progress bars / logs)
    bus = SimpleEventBus()
    bus.publish(
        make_event(RUN_START, {"config": cfg_model.model_dump(exclude_none=True)})
    )

    # 1) Execute experiment via runner
    circuit, raw = run_raw(cfg_model.model_dump())

    # 2) Canonicalize counts (MSB-left, fixed bit-width)
    counts = extract_counts_from_result(raw, num_qubits=cfg_model.num_qubits)

    # 3) Assemble typed analysis block
    analysis = _build_experiment_analysis(circuit=circuit, counts=counts, cfg=cfg_model)

    # 4) Optional: compute structured-decoherence research metrics
    structured_decoherence_metrics = None
    if cfg_model.enable_research_metrics and counts:
        structured_decoherence_metrics = compute_research_metrics(counts, cfg_model)

    # 5) Build provenance
    prov = _build_provenance(cfg_model)

    # 6) Persist analysis to disk (deterministic path via config hash)
    cfg_hash = sha1_of(cfg_model.model_dump(exclude_none=True))[:8]
    storage = LocalStorage(base_dir=ctx.base_results_dir)
    saved_path = storage.save_analysis(analysis.model_dump())

    artifacts: List[ArtifactRef] = [
        ArtifactRef(kind="analysis", path=saved_path, metadata={})
    ]

    # 7) Optional histogram rendering (only if requested + available)
    if (
        cfg_model.visualization_type == "histogram"
        and create_default_service is not None
        and counts
    ):
        try:
            service = create_default_service()
            # The viz layer accepts dicts; convert typed analysis/metrics if present.
            viz_payload = {
                "analysis": analysis.model_dump(),
                "structured_decoherence_metrics": (
                    structured_decoherence_metrics.model_dump()
                    if structured_decoherence_metrics
                    else None
                ),
            }
            # Save alongside the analysis file for easy discovery.
            hist_path = os.path.join(
                os.path.dirname(saved_path), f"histogram_{cfg_hash}.png"
            )
            # Render using "render_or_none" if available; otherwise call render directly.
            try:
                artifact = service.render_or_none("histogram", viz_payload, hist_path)  # type: ignore[attr-defined]
            except AttributeError:
                # Older VisualizationService without render_or_none
                artifact = service.render("histogram", viz_payload, hist_path)  # type: ignore[assignment]
            if artifact:
                artifacts.append(artifact)
        except Exception as e:
            logger.warning(f"Histogram rendering skipped: {e}")

    # 8) Package final typed result
    result = ExperimentResult(
        analysis=analysis,
        structured_decoherence_metrics=structured_decoherence_metrics,
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
    manifest: SweepManifest | Dict[str, Any],
    ctx: Optional[AppContext] = None,
) -> List[ExperimentResult]:
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

    Returns
    -------
    List[ExperimentResult]
        A flat list of results, one per realized configuration (× runs).

    See also
    --------
    iter_experiment_configs : yields the concrete `ExperimentConfig`s used.
    """
    ctx = ctx or AppContext()
    man = manifest if isinstance(manifest, SweepManifest) else SweepManifest(**manifest)

    base = man.base_config.model_dump(exclude_none=True) if man.base_config else {}
    results: List[ExperimentResult] = []
    keys = sorted((man.parameter_ranges or {}).keys())

    bus = SimpleEventBus()
    bus.publish(
        make_event(
            SWEEP_START, {"keys": keys, "total": _product_len(man.parameter_ranges)}
        )
    )

    # Cartesian expansion (depth-first), honoring stable key order
    def _expand(idx: int, acc: Dict[str, Any]) -> None:
        if idx == len(keys):
            # Merge: base + override + accumulated parameter choices
            cfg = {**base, **(man.override or {}), **acc}
            results.append(run(cfg, ctx))
            return
        key = keys[idx]
        for value in man.parameter_ranges[key]:
            acc[key] = value
            _expand(idx + 1, acc)
        acc.pop(key, None)

    _expand(0, {})
    bus.publish(make_event(SWEEP_END, {"count": len(results)}))
    return results


# ---------------------------------------------------------------------------
# Public helper: iterate realized ExperimentConfigs (useful “sweep driver” core)
# ---------------------------------------------------------------------------


def iter_experiment_configs(
    manifest: SweepManifest | Dict[str, Any],
) -> Iterator[ExperimentConfig]:
    """Yield concrete `ExperimentConfig` instances for a Cartesian sweep.

    This is a pure generator that expands the sweep and yields fully-typed
    ExperimentConfigs. It is useful if you want to:
      * Run on a custom scheduler/pool (e.g., multiprocessing, Slurm).
      * Distribute runs across machines.
      * Add custom pre/post hooks around each config.

    Example
    -------
    >>> for cfg in iter_experiment_configs(manifest):
    ...     submit_to_pool(lambda: run(cfg))

    Parameters
    ----------
    manifest : SweepManifest | Dict[str, Any]
        Sweep specification (typed or dict).

    Yields
    ------
    ExperimentConfig
        Fully-typed configuration for each parameter combination (× runs).
    """
    man = manifest if isinstance(manifest, SweepManifest) else SweepManifest(**manifest)
    base = man.base_config.model_dump(exclude_none=True) if man.base_config else {}
    keys = sorted((man.parameter_ranges or {}).keys())

    def _expand(idx: int, acc: Dict[str, Any]) -> None:
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


def _product_len(d: Dict[str, List[Any]]) -> int:
    total = 1
    for v in (d or {}).values():
        total *= len(v)
    return total


def _build_experiment_analysis(
    *,
    circuit: QuantumCircuit,
    counts: Dict[str, int],
    cfg: ExperimentConfig,
) -> ExperimentAnalysis:
    """Construct a strongly-typed `ExperimentAnalysis` from circuit + counts + config.

    This method fills:
      - ExperimentMetadata: id, timestamp, engine version, research type
      - CircuitStatistics: depth, gate counts, two-qubit counts
      - MeasurementResults: raw counts, total shots, unique outcomes, probabilities

    It intentionally leaves optional advanced sections (IT metrics, correlations,
    validation) as None to keep responsibilities separated (other subsystems can
    populate them later if/when needed).
    """
    # ----- metadata -----
    meta = ExperimentMetadata(
        experiment_id=f"{cfg.state_type}_{cfg.num_qubits}",
        timestamp=_now_iso(),
        framework_version="engine-1.0",  # TODO: inject your real engine version
        research_type=cfg.research_type,
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
            outcome_probabilities
            if outcome_probabilities
            else {("0" * cfg.num_qubits): 1.0}
        ),
        density_matrix=None,
        fidelity=None,
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


def _build_provenance(cfg: ExperimentConfig) -> Provenance:
    """Fill a minimal, valid `Provenance` block (extend as you capture more).

    Recommended future enrichments:
      - software_versions: qiskit, numpy, your engine version, OS/CPU
      - simulator_info: AerSimulator options, target backend name
      - transpilation_summary: pass manager, optimization level, coupling map
      - execution_time_seconds / memory_usage_mb: measured via timers/profilers
      - git_sha: inject from CI to lock exact code version
    """
    return Provenance(
        schema_version="1.0.0",
        timestamp=_now_iso(),
        software_versions={},
        host_info={},
        git_sha=None,
        rng_seed=cfg.rng_seed,
        simulator_info={},
        transpilation_summary={},
        execution_time_seconds=None,
        memory_usage_mb=None,
    )
