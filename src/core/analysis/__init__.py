# src/analysis/__init__.py

"""Structured Decoherence Analysis Module.

Research-grade analysis framework for quantum structured decoherence studies.
Focuses on pathway detection, correlation analysis, and statistical validation.

Core Components:
- Metrics: Asymmetry Index, Pathway Concentration, Entanglement-Error Correlation
- Core utilities: Information theory, bootstrap confidence, null models
- Integration: Schema compliance and research-grade output
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

# Structured decoherence metrics
from .metrics import (
    # Primary structured decoherence metrics
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
    # Structured Decoherence Metrics
    "compute_asymmetry_index",
    "compute_pathway_concentration_ratio",
    "compute_entanglement_error_correlation",
    "compute_temporal_pathway_stability",
    "compute_complexity_emergence_score",
]
