"""Quantum Experiment Engine.

The engine layer orchestrates experiment execution, manages IO operations,
and provides the public API for running experiments.

Structure:
- execution/    : Experiment runners, context, and parameter sweeps
- persistence/  : Result storage and config hashing
- infrastructure/: Event bus and cross-cutting concerns
- models/       : Pydantic schemas for configs and results
- analysis/     : Analysis metrics integration
- visualization/: Plotting and rendering

Public API:
- run(config) -> ExperimentResult
- sweep(manifest) -> List[ExperimentResult]
"""

from .api import run, sweep

__all__ = ["run", "sweep"]
