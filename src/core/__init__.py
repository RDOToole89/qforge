"""
Core quantum logic module for structured decoherence research.

This module contains the essential quantum computing components:
- Experiment execution and circuit handling
- State preparation for entangled quantum states  
- Physics-compliant noise models
- Structured decoherence analysis metrics
"""

from .experiment_runner import ExperimentRunner
from .state_preparation import prepare_state
from .noise_models import create_noise_model
from .analysis import (
    # Core structured decoherence metrics
    compute_asymmetry_index,
    compute_pathway_concentration_ratio,
    compute_entanglement_error_correlation,
    compute_temporal_pathway_stability,
    compute_complexity_emergence_score,
    # Information theory utilities
    entropy,
    mutual_information,
    total_correlation,
)

__all__ = [
    "ExperimentRunner",
    "prepare_state", 
    "create_noise_model",
    # Structured decoherence metrics
    "compute_asymmetry_index",
    "compute_pathway_concentration_ratio",
    "compute_entanglement_error_correlation",
    "compute_temporal_pathway_stability",
    "compute_complexity_emergence_score",
    # Information theory
    "entropy",
    "mutual_information",
    "total_correlation",
]
