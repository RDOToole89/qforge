"""
Core analysis utilities for structured decoherence research.

This module provides essential functions for quantum measurement analysis:
- Information theory metrics (Shannon entropy, mutual information, etc.)
- Bootstrap confidence intervals and statistical validation
- Null model framework for hypothesis testing
"""

from .bootstrap import (
    MetricWithConfidence,
    bootstrap_confidence_interval,
    compute_metric_with_confidence,
)
from .information_theory import (
    counts_to_probabilities,
    entropy,
    jensen_shannon_divergence,
    marginal_distribution,
    mutual_information,
    total_correlation,
)
from .null_models import (
    factorized_null_model,
)

__all__ = (
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
)
