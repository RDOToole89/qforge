"""Engine API facade.

Stable entry points for running experiments and parameter sweeps.
"""

from __future__ import annotations
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.engine.context import AppContext
from src.engine.runner import run_raw
from src.engine.hashing import sha1_of
from src.engine.models import (
    ExperimentConfig,
    ExperimentResult,
    Provenance,
    SweepManifest,
    ArtifactRef,
)
from src.core.research_handler import ResearchExperimentHandler
from src.engine.events import (
    SimpleEventBus,
    make_event,
    RUN_START,
    RUN_END,
    SWEEP_START,
    SWEEP_END,
)
from src.engine.storage import LocalStorage


def _now_iso() -> str:
    return datetime.now().isoformat()


def run(
    config: ExperimentConfig | Dict[str, Any], ctx: Optional[AppContext] = None
) -> ExperimentResult:
    """Run a single experiment and return ExperimentResult (no saving yet).

    Phase 3: wrap legacy runner and research handler.
    """
    ctx = ctx or AppContext()
    cfg_model = (
        config if isinstance(config, ExperimentConfig) else ExperimentConfig(**config)
    )

    bus = SimpleEventBus()
    bus.publish(
        make_event(RUN_START, {"config": cfg_model.model_dump(exclude_none=True)})
    )
    circuit, raw = run_raw(cfg_model.model_dump())

    rh = ResearchExperimentHandler(results_dir=ctx.base_results_dir)
    analysis = rh.process_experiment_result(
        circuit=circuit,
        result=raw,
        experiment_config=cfg_model.model_dump(),
        experiment_id=cfg_model.state_type + "_engine",
    )

    metrics = analysis.get("research_metrics", {})
    prov = Provenance(
        schema_version="1.0.0",
        timestamp=_now_iso(),
        software_versions=analysis.get("provenance", {}).get("software_versions", {}),
        host_info=analysis.get("provenance", {}).get("host", {}),
        git_sha=analysis.get("provenance", {}).get("git_commit"),
        rng_seed=cfg_model.rng_seed,
        simulator_info=analysis.get("provenance", {}).get("backend", {}),
        transpilation_summary=analysis.get("provenance", {}).get("transpilation", {}),
    )

    cfg_hash = sha1_of(cfg_model.model_dump(exclude_none=True))[:8]

    # Save via storage for deterministic path; mirror legacy structure
    storage = LocalStorage(base_dir=ctx.base_results_dir)
    saved_path = storage.save_analysis(analysis)

    result = ExperimentResult(
        analysis=analysis,
        metrics=metrics,
        artifacts=[ArtifactRef(kind="other", path=saved_path, metadata={})],
        provenance=prov,
        config_hash=cfg_hash,
        timestamp=_now_iso(),
    )
    bus.publish(
        make_event(
            RUN_END,
            {"config_hash": cfg_hash, "artifacts": [a.path for a in result.artifacts]},
        )
    )
    return result


def sweep(
    manifest: SweepManifest | Dict[str, Any], ctx: Optional[AppContext] = None
) -> List[ExperimentResult]:
    """Run a sweep of experiments (simple cartesian expansion in Phase 3)."""
    ctx = ctx or AppContext()
    man = manifest if isinstance(manifest, SweepManifest) else SweepManifest(**manifest)

    base = man.base_config.model_dump() if man.base_config else {}
    results: List[ExperimentResult] = []

    # Simple expansion: iterate parameter_ranges keys in stable order
    keys = sorted((man.parameter_ranges or {}).keys())

    bus = SimpleEventBus()
    bus.publish(make_event(SWEEP_START, {"keys": keys}))

    def _expand(idx: int, acc: Dict[str, Any]):
        if idx == len(keys):
            cfg = {**base, **acc}
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
