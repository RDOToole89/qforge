# src/state_preparation/__init__.py

"""
State preparation package for quantum experiments.

This package provides:
- BaseState: A template for state creation.
- GHZState, WState, ClusterState: Implementations of different quantum states.
- prepare_state: A factory function for creating states.
- STATE_CLASSES: Dictionary mapping state types to their classes.
"""

from .base_state import BaseState
from .bell_state import BellState
from .cluster_state import ClusterState
from .custom_state import CustomState
from .ghz_state import GHZState
from .state_constants import (
    STATE_CLASSES,
    get_state_class,
    get_state_info,
    validate_state_registry,
)
from .state_factory import (
    create_state_instance,
    get_available_states,
    prepare_state,
    prepare_state_for_hardware,
    validate_state_request,
)
from .superposition_state import SuperpositionState
from .w_state import WState

__all__ = [
    "BaseState",
    "GHZState",
    "WState",
    "ClusterState",
    "SuperpositionState",
    "BellState",
    "CustomState",
    "prepare_state",
    "create_state_instance",
    "get_available_states",
    "validate_state_request",
    "prepare_state_for_hardware",
    "STATE_CLASSES",
    "get_state_class",
    "get_state_info",
    "validate_state_registry",
]
