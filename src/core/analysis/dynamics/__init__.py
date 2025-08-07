"""
Dynamics analysis for quantum states.

This module provides time-dependent analysis functions:
- Decoherence analysis (Fubini-Study distance, decoherence rates)
- Error transition analysis (state-to-state transitions)
- Clustering analysis for decoherence dynamics
"""

from .decoherence import (
    compute_fubini_study_distance,
    compute_fubini_study_distances_over_time,
    analyze_decoherence_rate,
)
from .transitions import (
    compute_error_transitions,
    analyze_transition_dynamics,
    find_dominant_transitions,
    compute_transition_entropy,
)
from .clustering import (
    cluster_qubits,
    analyze_cluster_structure,
    find_optimal_clusters,
    analyze_decoherence_clusters,
    compute_cluster_decoherence_metrics,
)

__all__ = [
    # Decoherence
    "compute_fubini_study_distance",
    "compute_fubini_study_distances_over_time",
    "analyze_decoherence_rate",
    # Transitions
    "compute_error_transitions",
    "analyze_transition_dynamics",
    "find_dominant_transitions",
    "compute_transition_entropy",
    # Clustering
    "cluster_qubits",
    "analyze_cluster_structure",
    "find_optimal_clusters",
    "analyze_decoherence_clusters",
    "compute_cluster_decoherence_metrics",
]
