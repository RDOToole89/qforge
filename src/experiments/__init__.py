"""
Experiment management module for the Quantum Experiment Framework.

This module provides comprehensive experiment management including
preset experiments, plugin system, and experiment validation.
"""

from .manager import ExperimentManager, get_experiment_manager
from .validator import ExperimentValidator
from .presets import load_preset_experiments
from .plugins import load_plugins

__all__ = [
    "ExperimentManager",
    "get_experiment_manager",
    "ExperimentValidator",
    "load_preset_experiments",
    "load_plugins",
]
