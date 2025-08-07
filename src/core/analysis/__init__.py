# src/analysis/__init__.py

"""
Quantum state analysis module.

This module provides comprehensive analysis tools for quantum states:
- Core analysis: correlations, information theory, Bloch sphere
- Dynamics analysis: decoherence, transitions, clustering
- Symmetry analysis: SU(2), SU(3), parity symmetries
"""

# Core analysis functions
from .core import (
    # Correlations
    compute_pairwise_correlations,
    compute_conditional_correlations,
    compute_permutation_symmetric_correlations,
    compute_adaptive_threshold,
    compute_correlations_for_hypergraph,
    # Information Theory
    compute_shannon_entropy,
    compute_kl_divergence,
    compute_total_variation_distance,
    compute_mutual_information,
    compute_qubit_wise_bias,
    compute_research_metrics,
    # Bloch sphere
    compute_bloch_vector,
    compute_bloch_vectors_for_all_qubits,
    compute_bloch_trajectories,
    analyze_bloch_purity,
    compute_bloch_distance,
    analyze_bloch_evolution,
)

# Dynamics analysis functions
from .dynamics import (
    # Decoherence
    compute_fubini_study_distance,
    compute_fubini_study_distances_over_time,
    analyze_decoherence_rate,
    # Transitions
    compute_error_transitions,
    analyze_transition_dynamics,
    find_dominant_transitions,
    compute_transition_entropy,
    # Clustering
    cluster_qubits,
    analyze_cluster_structure,
    find_optimal_clusters,
    analyze_decoherence_clusters,
    compute_cluster_decoherence_metrics,
)

# Symmetry analysis functions
from .symmetry import (
    compute_su2_symmetry,
    compute_su3_symmetry,
    compute_parity_distribution,
    analyze_symmetry_breaking,
    compute_permutation_invariance,
)

__all__ = [
    # Core Analysis
    "compute_pairwise_correlations",
    "compute_conditional_correlations",
    "compute_permutation_symmetric_correlations",
    "compute_adaptive_threshold",
    "compute_correlations_for_hypergraph",
    "compute_shannon_entropy",
    "compute_kl_divergence",
    "compute_total_variation_distance",
    "compute_mutual_information",
    "compute_qubit_wise_bias",
    "compute_research_metrics",
    "compute_bloch_vector",
    "compute_bloch_vectors_for_all_qubits",
    "compute_bloch_trajectories",
    "analyze_bloch_purity",
    "compute_bloch_distance",
    "analyze_bloch_evolution",
    # Dynamics Analysis
    "compute_fubini_study_distance",
    "compute_fubini_study_distances_over_time",
    "analyze_decoherence_rate",
    "compute_error_transitions",
    "analyze_transition_dynamics",
    "find_dominant_transitions",
    "compute_transition_entropy",
    "cluster_qubits",
    "analyze_cluster_structure",
    "find_optimal_clusters",
    "analyze_decoherence_clusters",
    "compute_cluster_decoherence_metrics",
    # Symmetry Analysis
    "compute_su2_symmetry",
    "compute_su3_symmetry",
    "compute_parity_distribution",
    "analyze_symmetry_breaking",
    "compute_permutation_invariance",
]
