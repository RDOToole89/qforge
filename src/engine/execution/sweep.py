# src/engine/execution/sweep.py
"""
Parameter Sweep Driver (engine-native).

What this is
------------
A small, focused driver that:
  1) Expands a `SweepManifest` into concrete `ExperimentConfig`s
  2) Runs each config via the engine's `EngineExperimentRunner`
  3) Canonicalizes counts and assembles typed `ExperimentResult`s
  4) (Optional) Computes research metrics per run
  5) (Optional) Persists each run's analysis JSON (deterministic paths)
  6) (Optional) Renders per-run histograms (png)
  7) Builds a typed `SweepResult` with a minimal aggregated analysis
  8) (Optional) Persists a sweep-level summary JSON

Why this exists
---------------
It gives you a ready-to-use sweep executor without pulling in the higher-level
`engine.api.sweep` orchestration. Use it directly from scripts, batch jobs,
or notebooks when you need a compact, explicit sweep loop.

Key entry point
---------------
- run_sweep(manifest, enable_histograms=False, storage_dir=None, output_dir=None, save_summary=True)

Notes
-----
- This module has no hard dependency on the visualization package; histograms
  are generated with a local matplotlib import if `enable_histograms=True` and
  `output_dir` is provided.
- Persistence (per-run analysis JSON and sweep summary JSON) is optional and
  driven by `storage_dir` and `save_summary`. If you pass `storage_dir`,
  each run’s typed analysis is saved using the engine `LocalStorage` rules.
- All results are returned as *typed* Pydantic models.

Example
-------
>>> from src.engine.models.config import ExperimentConfig
>>> from src.engine.models.sweep import SweepManifest
>>> base = ExperimentConfig(num_qubits=3, state_type="GHZ", shots=1024, visualization_type="histogram")
>>> mf = SweepManifest(
...     base_config=base,
...     parameter_ranges={"error_rate": [0.0, 0.02, 0.05], "noise_enabled": [False, True]},
...     runs_per_config=2,
... )
>>> sweep_res = run_sweep(mf, enable_histograms=True, storage_dir="results", output_dir="results")
>>> len(sweep_res.experiment_results)
"""

from __future__ import annotations

import hashlib
import logging
from collections.abc import Iterable
from copy import deepcopy
from datetime import datetime
from itertools import product
from pathlib import Path

import numpy as np

from src.engine.analysis import compute_metrics_bundle, extract_counts_from_result

# Engine-native runner (no legacy deps)
from src.engine.execution.runner import EngineExperimentRunner
from src.engine.models.config import ExperimentConfig
from src.engine.models.results import (
    CircuitStatistics,
    ExperimentAnalysis,
    ExperimentMetadata,
    ExperimentResult,
    MeasurementResults,
    Provenance,
)
from src.engine.models.storage import ArtifactRef
from src.engine.models.sweep import (
    OutcomeStatistics,
    ParameterAnalysis,
    ParameterEffect,
    StatisticalSummary,
    SweepExecutionMetadata,
    SweepManifest,
    SweepResult,
)

# Optional persistence
from src.engine.persistence.storage import LocalStorage

logger = logging.getLogger(__name__)

# -------- helpers -----------------------------------------------------------


def _hash_config(cfg: ExperimentConfig) -> str:
    """Short, deterministic hash of an ExperimentConfig (12 hex chars)."""
    blob = cfg.model_dump_json(by_alias=True, exclude_none=True, sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:12]


def _probs_from_counts(counts: dict[str, int]) -> dict[str, float]:
    total = float(sum(counts.values())) or 1.0
    return {k: v / total for k, v in counts.items()}


def _iter_experiment_configs(manifest: SweepManifest) -> Iterable[ExperimentConfig]:
    """
    Cartesian expansion of a SweepManifest into concrete ExperimentConfigs.
    - Honors `base_config`
    - Applies `override`
    - Applies each combination in `parameter_ranges` in a stable order
    - Duplicates per `runs_per_config`, varying rng_seed if manifest.rng_seed is set
    """
    base = manifest.base_config
    assert base is not None, "SweepManifest.base_config is required."

    keys = list(manifest.parameter_ranges.keys())
    vals = [manifest.parameter_ranges[k] for k in keys]

    run_idx = 0
    for combo in product(*vals):
        combo_overrides = dict(zip(keys, combo))

        cfg_dict = base.model_dump(exclude_none=False)
        if manifest.override:
            cfg_dict.update(manifest.override)
        cfg_dict.update(combo_overrides)

        for _ in range(manifest.runs_per_config):
            run_cfg = deepcopy(cfg_dict)
            if manifest.rng_seed is not None:
                run_cfg["rng_seed"] = int(manifest.rng_seed) + run_idx
            run_idx += 1
            yield ExperimentConfig(**run_cfg)


def _maybe_save_histogram(
    counts: dict[str, int],
    exp_id: str,
    output_dir: str | None,
    title: str | None = None,
) -> ArtifactRef | None:
    """Create and save a histogram PNG for counts if possible; otherwise no-op."""
    if not counts:
        return None
    if not output_dir:
        # explicit no-op unless a directory is provided
        logger.debug("Histogram requested but no output_dir provided; skipping.")
        return None

    try:
        import matplotlib.pyplot as plt  # keep dependency optional
    except Exception as e:
        logger.warning(f"matplotlib not available; skipping histogram for {exp_id}: {e}")
        return None

    try:
        out_base = Path(output_dir)
        out_path = out_base / "visualizations"
        out_path.mkdir(parents=True, exist_ok=True)
        file_path = out_path / f"{exp_id}.png"

        # Sort by frequency descending for readability
        items = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
        labels = [k for k, _ in items]
        values = [v for _, v in items]

        plt.figure(figsize=(10, 4))
        plt.bar(range(len(values)), values)
        plt.xticks(range(len(labels)), labels, rotation=90)
        plt.xlabel("Bitstring")
        plt.ylabel("Counts")
        plt.title(title or f"Outcome Histogram — {exp_id}")
        plt.tight_layout()
        plt.savefig(file_path, dpi=150)
        plt.close()

        return ArtifactRef(
            kind="histogram",
            path=str(file_path),
            metadata={"bins": len(values)},
            mime_type="image/png",
            title=title or "Outcome Histogram",
            description="Histogram of measurement counts (sorted by frequency)",
            public=False,
            publication_ready=False,
        )
    except Exception as e:
        logger.warning(f"Failed to write histogram for {exp_id}: {e}")
        return None


def _primary_metric_value(exp_result: ExperimentResult) -> float:
    """
    Extract a single scalar per experiment for sweep summaries.
    Preference order:
      - structure_score (if present in metrics_bundle)
      - first metric value (fallback)
      - 0.0 (no metrics)
    """
    bundle = exp_result.metrics_bundle
    if not bundle or not bundle.metrics:
        return 0.0
    entry = bundle.get("structure_score")
    if entry is not None:
        return entry.value
    first = next(iter(bundle.metrics.values()))
    return first.value


# -------- main API ----------------------------------------------------------


def run_sweep(
    manifest: SweepManifest,
    *,
    enable_histograms: bool = False,
    output_dir: str | None = None,
    storage_dir: str | None = None,
    save_summary: bool = True,
) -> SweepResult:
    """
    Execute a parameter sweep and return a typed `SweepResult`.

    Parameters
    ----------
    manifest : SweepManifest
        Sweep specification (base_config, parameter_ranges, runs_per_config, etc.).
    enable_histograms : bool, optional
        If True, generate a PNG histogram per run **when** the run's
        ExperimentConfig.visualization_type == 'histogram'.
    output_dir : Optional[str], optional
        Directory to write histograms (if enabled). If None, histograms are skipped.
    storage_dir : Optional[str], optional
        If provided, *persist each run's analysis JSON* using LocalStorage
        and attach an `ArtifactRef(kind="analysis")` to the ExperimentResult.
        Files are stored under date-stamped directories per `LocalStorage.save_analysis`.
    save_summary : bool, optional
        If True and `storage_dir` is provided, a sweep-level summary JSON is written
        to `<storage_dir>/sweeps/<YYYYMMDD>/<HHMMSS>_sweep_summary.json`.

    Returns
    -------
    SweepResult
        Typed sweep result containing all `ExperimentResult`s plus a minimal
        aggregated analysis and execution metadata.

    Notes
    -----
    - This function runs sequentially. If you need concurrency, pair
      `_iter_experiment_configs()` with your pool/executor and call the engine's
      single-run API for each config.
    """
    start_t = datetime.now().isoformat()
    results: list[ExperimentResult] = []
    errors: dict[str, int] = {}

    runner = EngineExperimentRunner(experiment_id="sweep")
    storage = LocalStorage(base_dir=storage_dir) if storage_dir else None

    for cfg in _iter_experiment_configs(manifest):
        try:
            circuit, qres = runner.run_experiment(
                num_qubits=cfg.num_qubits,
                state_type=cfg.state_type,
                noise_type=cfg.noise_type,
                noise_enabled=cfg.noise_enabled,
                shots=cfg.shots,
                sim_mode=cfg.sim_mode,
                error_rate=cfg.error_rate,
                z_prob=cfg.z_prob,
                i_prob=cfg.i_prob,
                t1=cfg.t1,
                t2=cfg.t2,
                custom_params=cfg.custom_params,
                rng_seed=cfg.rng_seed,
            )

            # Canonicalize to MSB-left, fixed width = cfg.num_qubits
            counts = extract_counts_from_result(qres, num_qubits=cfg.num_qubits)

            if not counts:
                # Skip this run but keep the sweep going (no counts)
                logger.warning(
                    "No counts extracted; skipping run. cfg_hash=%s params=%s",
                    _hash_config(cfg),
                    {
                        "state_type": cfg.state_type,
                        "num_qubits": cfg.num_qubits,
                        "shots": cfg.shots,
                    },
                )
                continue

            probs = _probs_from_counts(counts)

            # ---- build ExperimentResult (typed)

            # Circuit statistics (robust to Qiskit minor API diffs)
            try:
                gate_counts = dict(circuit.count_ops())
                twoq = sum(v for k, v in gate_counts.items() if k.upper() in {"CX", "CZ", "CP"})
                num_gates = int(len(circuit.data))
            except Exception:
                gate_counts, twoq, num_gates = {}, 0, 0

            circ_stats = CircuitStatistics(
                depth=int(circuit.depth() or 0),
                num_gates=num_gates,
                num_qubits=circuit.num_qubits,
                gate_types={k: int(v) for k, v in gate_counts.items()},
                two_qubit_gate_count=twoq,
            )

            meas = MeasurementResults(
                raw_counts=counts if counts else {("0" * cfg.num_qubits): 0},
                total_shots=int(sum(counts.values()) or 1),
                unique_outcomes=int(len(counts) or 1),
                outcome_probabilities=probs if probs else {("0" * cfg.num_qubits): 1.0},
            )

            exp_id = f"exp-{_hash_config(cfg)}"
            meta = ExperimentMetadata(
                experiment_id=exp_id,
                timestamp=datetime.now().isoformat(),
                framework_version="engine-1.0",
                research_type=cfg.research_type,
            )

            analysis = ExperimentAnalysis(
                experiment_metadata=meta,
                experiment_parameters=cfg.model_dump(exclude_none=True),
                circuit_statistics=circ_stats,
                measurement_results=meas,
            )

            prov = Provenance(
                timestamp=datetime.now().isoformat(),
                software_versions={"engine": "1.0"},
                host_info={},
                simulator_info={"backend": "AerSimulator", "shots": cfg.shots},
                transpilation_summary={},
            )

            metrics_bundle = compute_metrics_bundle(counts, cfg) if cfg.metrics else None

            artifacts: list[ArtifactRef] = []

            # Optional: persist analysis JSON per run
            if storage is not None:
                try:
                    saved_path = storage.save_analysis(analysis.model_dump())
                    artifacts.append(ArtifactRef(kind="analysis", path=saved_path, metadata={}))
                except Exception as e:
                    logger.warning(f"Failed to persist analysis for {exp_id}: {e}")

            # Optional: per-run histogram
            if enable_histograms and cfg.visualization_type == "histogram":
                art = _maybe_save_histogram(
                    counts=counts,
                    exp_id=exp_id,
                    output_dir=output_dir,
                    title=f"{cfg.state_type} ({cfg.num_qubits} qubits)",
                )
                if art:
                    artifacts.append(art)

            exp_result = ExperimentResult(
                analysis=analysis,
                metrics_bundle=metrics_bundle,
                research_metadata=None,
                provenance=prov,
                artifacts=artifacts,
                config_hash=_hash_config(cfg),
            )
            results.append(exp_result)

        except Exception as e:
            key = type(e).__name__
            errors[key] = errors.get(key, 0) + 1
            logger.exception(f"Experiment failed for config: {cfg}. Error: {e}")

    end_t = datetime.now().isoformat()

    # ---- lightweight aggregation for SweepResult

    vals = np.array([_primary_metric_value(r) for r in results], dtype=float)
    if vals.size > 0:
        mean = float(vals.mean())
        std = float(vals.std(ddof=1)) if vals.size > 1 else 0.0
        ci95 = 1.96 * (std / np.sqrt(max(1, vals.size))) if vals.size > 1 else 0.0
        outcome_stats = OutcomeStatistics(
            metric_name="primary_metric",
            mean=mean,
            std=std,
            min_value=float(vals.min()),
            max_value=float(vals.max()),
            skewness=None,
            kurtosis=None,
            ci_95_lower=float(mean - ci95),
            ci_95_upper=float(mean + ci95),
        )
    else:
        outcome_stats = OutcomeStatistics(
            metric_name="primary_metric",
            mean=0.0,
            std=0.0,
            min_value=0.0,
            max_value=0.0,
            skewness=None,
            kurtosis=None,
            ci_95_lower=0.0,
            ci_95_upper=0.0,
        )

    # Stub main-effects so the structure is valid; you can replace with ANOVA later
    main_effects: dict[str, ParameterEffect] = {}
    for pname in manifest.parameter_ranges.keys():
        main_effects[pname] = ParameterEffect(
            parameter_name=pname,
            effect_size=0.0,
            significance=1.0,
            direction="unclear",
            strength="weak",
            correlation_coefficient=None,
            trend_analysis=None,
        )

    param_analysis = ParameterAnalysis(
        main_effects=main_effects,
        interaction_effects=None,
        sensitivity_ranking=list(manifest.parameter_ranges.keys()),
        optimal_regions=None,
    )

    stat_summary = StatisticalSummary(
        total_experiments=len(results) + sum(errors.values()),
        successful_experiments=len(results),
        outcome_statistics={"primary_metric": outcome_stats},
        convergence_achieved=True if len(results) >= 3 else False,
        confidence_intervals={
            "primary_metric": [outcome_stats.ci_95_lower, outcome_stats.ci_95_upper]
        },
        data_quality_score=1.0 if len(results) else 0.0,
    )

    exec_meta = SweepExecutionMetadata(
        start_time=start_t,
        end_time=end_t,
        total_duration_seconds=None,
        parallel_execution_used=False,
        max_concurrent_achieved=None,
        peak_memory_mb=None,
        total_cpu_time_seconds=None,
        failed_experiments=sum(errors.values()),
        error_summary=errors,
    )

    sweep_result = SweepResult(
        manifest=manifest,
        experiment_results=results,
        parameter_analysis=param_analysis,
        statistical_summary=stat_summary,
        research_insights=None,
        execution_metadata=exec_meta,
    )

    # Optional: write a sweep-level summary JSON for quick indexing
    if save_summary and storage is not None:
        try:
            date_dir = datetime.now().strftime("%Y%m%d")
            time_str = datetime.now().strftime("%H%M%S")
            summary = {
                "created": end_t,
                "total": len(results),
                "failed": int(sum(errors.values())),
                "parameters": list(manifest.parameter_ranges.keys()),
                "experiment_ids": [r.analysis.experiment_metadata.experiment_id for r in results],
                "artifacts": [a.path for r in results for a in r.artifacts],
                "primary_metric_mean": outcome_stats.mean,
                "primary_metric_ci95": [
                    outcome_stats.ci_95_lower,
                    outcome_stats.ci_95_upper,
                ],
            }
            rel = f"sweeps/{date_dir}/{time_str}_sweep_summary.json"
            _ = storage.save_json(rel, summary)
        except Exception as e:
            logger.warning(f"Failed to save sweep summary: {e}")

    return sweep_result
