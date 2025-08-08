"""Engine API facade.

Stable entry points for running experiments and parameter sweeps.
"""
from __future__ import annotations
from typing import Optional, List

# Placeholders; real types will come from engine.models in Phase 2
ExperimentConfig = dict
ExperimentResult = dict
SweepManifest = dict


def run(config: ExperimentConfig, ctx: Optional[dict] = None) -> ExperimentResult:
    """Run a single experiment.

    Phase 0 stub: delegates to existing path (wired in Phase 3).
    """
    raise NotImplementedError("engine.api.run not wired yet (Phase 3)")


def sweep(manifest: SweepManifest, ctx: Optional[dict] = None) -> List[ExperimentResult]:
    """Run a sweep of experiments.

    Phase 0 stub: delegates to existing path (wired in Phase 3).
    """
    raise NotImplementedError("engine.api.sweep not wired yet (Phase 3)")
