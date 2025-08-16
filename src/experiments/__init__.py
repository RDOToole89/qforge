"""
Experiment management module for the Quantum Experiment Framework.

This module provides comprehensive experiment management including
preset experiments, plugin system, and version-agnostic schema validation.
"""

from .manager import ExperimentManager, get_experiment_manager
from .validation import (
    SchemaValidator,
    create_validator,
    validate_experiment,
    create_experiment
)
from .presets import load_preset_experiments
from .plugins import load_plugins

__all__ = [
    # Core functionality
    "ExperimentManager",
    "get_experiment_manager",
    
    # Version-agnostic validation system
    "SchemaValidator", 
    "create_validator",
    "validate_experiment",
    "create_experiment",
    
    # Preset and plugin system
    "load_preset_experiments",
    "load_plugins",
]
