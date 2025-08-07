# src/analysis/__init__.py

"""
Quantum state analysis module.

This module provides comprehensive analysis tools for quantum states:
- Correlation analysis (pairwise, conditional, permutation-symmetric)
- Decoherence metrics (Fubini-Study distance)
- Symmetry analysis (SU(2), SU(3), parity)
- Clustering algorithms for qubit grouping
- Bloch sphere computations
- Error transition analysis
"""

from .correlations import (
    compute_pairwise_correlations,
    compute_conditional_correlations,
    compute_permutation_symmetric_correlations,
)
from .decoherence import compute_fubini_study_distance
from .symmetry import (
    compute_su2_symmetry,
    compute_su3_symmetry,
    compute_parity_distribution,
)
from .clustering import cluster_qubits
from .bloch import compute_bloch_vector
from .transitions import compute_error_transitions
from .information_theory import (
    compute_shannon_entropy,
    compute_kl_divergence,
    compute_total_variation_distance,
    compute_mutual_information,
    compute_qubit_wise_bias,
    compute_research_metrics,
)

__all__ = [
    # Correlations
    "compute_pairwise_correlations",
    "compute_conditional_correlations",
    "compute_permutation_symmetric_correlations",
    # Decoherence
    "compute_fubini_study_distance",
    # Symmetry
    "compute_su2_symmetry",
    "compute_su3_symmetry",
    "compute_parity_distribution",
    # Clustering
    "cluster_qubits",
    # Bloch sphere
    "compute_bloch_vector",
    # Transitions
    "compute_error_transitions",
    # Information Theory
    "compute_shannon_entropy",
    "compute_kl_divergence",
    "compute_total_variation_distance",
    "compute_mutual_information",
    "compute_qubit_wise_bias",
    "compute_research_metrics",
]
