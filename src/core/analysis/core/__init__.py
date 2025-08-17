"""
Core analysis utilities for structured decoherence research.

This module provides essential functions for quantum measurement analysis:
- Information theory metrics (Shannon entropy, mutual information, etc.)
- Bootstrap confidence intervals and statistical validation
- Null model framework for hypothesis testing
"""

from .information_theory import (
    entropy,
    counts_to_probabilities,
    marginal_distribution,
    mutual_information,
    total_correlation,
    jensen_shannon_divergence,
)
from .bootstrap import (
    bootstrap_confidence_interval,
    compute_metric_with_confidence,
    MetricWithConfidence,
)
from .null_models import (
    factorized_null_model,
)

__all__ = [
    # Information Theory
    "entropy",
    "counts_to_probabilities",
    "marginal_distribution",
    "mutual_information",
    "total_correlation",
    "jensen_shannon_divergence",
    # Bootstrap Statistics
    "bootstrap_confidence_interval",
    "compute_metric_with_confidence",
    "MetricWithConfidence",
    # Null Models
    "factorized_null_model",
]
