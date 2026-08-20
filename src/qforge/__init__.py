"""QForge — a general-purpose quantum experiment engine built on Qiskit."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

try:
    from ._version import version as __version__
except ImportError:  # pragma: no cover - missing only in raw checkouts
    __version__ = "0.0.0.dev"

from qforge.engine.api import iter_experiment_configs, run, sweep
from qforge.engine.models import ExperimentConfig, ExperimentResult, SweepManifest

if TYPE_CHECKING:
    from qforge.experiments import get_experiment, list_experiments

__all__ = [
    "ExperimentConfig",
    "ExperimentResult",
    "SweepManifest",
    "__version__",
    "get_experiment",
    "iter_experiment_configs",
    "list_experiments",
    "run",
    "sweep",
]


def __getattr__(name: str) -> Any:
    """Lazily expose the experiment registry so `from qforge import run` stays lean."""
    if name in {"get_experiment", "list_experiments"}:
        from qforge.experiments import get_experiment, list_experiments

        exports = {
            "get_experiment": get_experiment,
            "list_experiments": list_experiments,
        }
        return exports[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
