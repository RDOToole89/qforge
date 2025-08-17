"""
Core quantum analysis functions.

This module provides fundamental quantum state analysis functions:
- Correlation analysis (pairwise, conditional, permutation-symmetric)
- Information theory metrics (Shannon entropy, KL divergence, etc.)
- Bloch sphere computations and analysis
"""

from .correlations import (
    compute_pairwise_correlations,
    compute_conditional_correlations,
    compute_permutation_symmetric_correlations,
    compute_adaptive_threshold,
    compute_correlations_for_hypergraph,
)
from .information_theory import (
    entropy,
    counts_to_probabilities,
    marginal_distribution,
    mutual_information,
    total_correlation,
    jensen_shannon_divergence,
)
from .bloch import (
    compute_bloch_vector,
    compute_bloch_vectors_for_all_qubits,
    compute_bloch_trajectories,
    analyze_bloch_purity,
    compute_bloch_distance,
    analyze_bloch_evolution,
)

__all__ = [
    # Correlations
    "compute_pairwise_correlations",
    "compute_conditional_correlations",
    "compute_permutation_symmetric_correlations",
    "compute_adaptive_threshold",
    "compute_correlations_for_hypergraph",
    # Information Theory
    "entropy",
    "counts_to_probabilities",
    "marginal_distribution",
    "mutual_information",
    "total_correlation",
    "jensen_shannon_divergence",
    # Bloch sphere
    "compute_bloch_vector",
    "compute_bloch_vectors_for_all_qubits",
    "compute_bloch_trajectories",
    "analyze_bloch_purity",
    "compute_bloch_distance",
    "analyze_bloch_evolution",
]
