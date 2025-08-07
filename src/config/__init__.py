# src/config/__init__.py

"""
Configuration module for the Quantum Experiment Framework.

This module provides centralized configuration management including
settings, constants, and parameter handling.
"""

from .settings import (
    settings,
    get_defaults,
    get_logging_config,
    get_plugin_config,
    validate_settings,
)
from .constants import (
    VALID_NOISE_TYPES,
    VALID_STATE_TYPES,
    VALID_SIM_MODES,
    NOISE_SHORTCUTS,
    STATE_SHORTCUTS,
    SINGLE_QUBIT_NOISE_TYPES,
    MAX_CORRELATION_ORDER,
    MIN_OCCURRENCES_THRESHOLD,
    DEFAULT_CLUSTERING_THRESHOLD,
    DEFAULT_NODE_COLOR,
    DEFAULT_EDGE_COLOR,
    DEFAULT_PLOT_STYLE,
)

__all__ = [
    # Settings
    "settings",
    "get_defaults",
    "get_logging_config",
    "get_plugin_config",
    "validate_settings",
    # Constants
    "VALID_NOISE_TYPES",
    "VALID_STATE_TYPES",
    "VALID_SIM_MODES",
    "NOISE_SHORTCUTS",
    "STATE_SHORTCUTS",
    "SINGLE_QUBIT_NOISE_TYPES",
    "MAX_CORRELATION_ORDER",
    "MIN_OCCURRENCES_THRESHOLD",
    "DEFAULT_CLUSTERING_THRESHOLD",
    "DEFAULT_NODE_COLOR",
    "DEFAULT_EDGE_COLOR",
    "DEFAULT_PLOT_STYLE",
]
