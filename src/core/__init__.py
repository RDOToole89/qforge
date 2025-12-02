"""
Core quantum logic — public API

This package contains the reusable building blocks for the engine:
- State preparation primitives (GHZ, W, Bell, Cluster, Superposition, Custom)
- Noise model factory (depolarizing, amplitude/phase damping, bit/phase flip, thermal)
- Lightweight analysis utilities used across the stack

Notes
-----
* The **experiment runner/orchestration** lives in `src.engine.*` now.
  We intentionally do NOT export any runner here to avoid coupling and to
  keep this package focused on pure quantum primitives + utilities.

* Structured-decoherence **metrics** (registry, schema bridge, etc.)
  live under `src.analysis.metrics`. Import them from there when needed.
"""

# --- State preparation (canonical entry point) ---
# --- Reusable analysis utilities ---
# Information theory + bootstrap + null models (core utilities)
from .analysis.core import (
    MetricWithConfidence,
    bootstrap_confidence_interval,
    compute_metric_with_confidence,
    counts_to_probabilities,
    entropy,
    factorized_null_model,
    jensen_shannon_divergence,
    marginal_distribution,
    mutual_information,
    total_correlation,
)

# Correlation / geometry helpers (from core.correlations)
from .analysis.core.correlations import (
    get_topology_adjacency,
    mi_matrix,
)

# --- Noise models (canonical factory) ---
# Import explicitly from the factory to make the public surface unambiguous.
from .noise_models.noise_factory import create_noise_model
from .state_preparation import prepare_state

__all__ = [
    # State preparation
    "prepare_state",
    # Noise
    "create_noise_model",
    # Information theory utilities
    "entropy",
    "counts_to_probabilities",
    "marginal_distribution",
    "mutual_information",
    "total_correlation",
    "jensen_shannon_divergence",
    "bootstrap_confidence_interval",
    "compute_metric_with_confidence",
    "MetricWithConfidence",
    "factorized_null_model",
    # Correlation/geometry helpers
    "mi_matrix",
    "get_topology_adjacency",
]
