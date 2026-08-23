# src/analysis/__init__.py

"""Measurement-outcome analysis module.

Analysis framework for quantifying structure in quantum measurement outcome
distributions: distribution asymmetry, concentration, correlation analysis,
and statistical validation.

Core Components:
- Metrics: Asymmetry Index, Pathway Concentration, Entanglement-Error Correlation
- Core utilities: Information theory, bootstrap confidence, null models
- Integration: Schema-compliant output
"""

# Core information theory functions
from .core import (
    counts_to_probabilities,
    # Information Theory
    entropy,
    jensen_shannon_divergence,
    marginal_distribution,
    mutual_information,
    total_correlation,
)

# Distribution-structure metrics
from .metrics import (
    # Primary metrics
    compute_asymmetry_index,
    compute_complexity_emergence_score,
    compute_entanglement_error_correlation,
    compute_pathway_concentration_ratio,
    compute_temporal_pathway_stability,
)

__all__ = [
    # Core Information Theory
    "entropy",
    "counts_to_probabilities",
    "marginal_distribution",
    "mutual_information",
    "total_correlation",
    "jensen_shannon_divergence",
    # Distribution-Structure Metrics
    "compute_asymmetry_index",
    "compute_pathway_concentration_ratio",
    "compute_entanglement_error_correlation",
    "compute_temporal_pathway_stability",
    "compute_complexity_emergence_score",
]
