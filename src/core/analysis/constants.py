"""Analysis constants and defaults.

# Central Configuration & Defaults
This module defines all numerical constants, tolerances, and default parameters
used throughout the analysis framework. Centralizing these values ensures
consistency and makes the framework easy to tune.

# Rationale
All constants are chosen based on:
- Statistical best practices (Jeffreys prior for uninformative priors)
- Numerical stability (epsilon values for log safety)
- Computational efficiency (bootstrap sample sizes)
- Reproducibility (fixed random seeds)

# Educational Framework
These constants embody key principles from:
- Bayesian statistics (prior selection)
- Information theory (base-2 logarithms)
- Bootstrap theory (sample size recommendations)
- Quantum measurement theory (smoothing for shot noise)
"""

from collections.abc import Mapping
from typing import Final

import numpy as np

# =============================================================================
# STATISTICAL CONSTANTS
# =============================================================================

# Smoothing and Priors
ALPHA: Final[float] = 0.5
"""Jeffreys prior parameter for categorical distributions.
α = 0.5 provides uninformative prior for Bernoulli/categorical parameters.
Used for smoothing probability distributions before entropy calculations.
Reference: Jeffreys (1946), "An Invariant Form for the Prior Probability"
"""

# Numerical Stability
EPS: Final[float] = 1e-12
"""Minimum probability value for numerical stability.
Probabilities are clamped to [EPS, 1] before logarithmic operations.
Chosen to avoid underflow in 64-bit floating point calculations.
"""

LOG_BASE: Final[float] = 2.0
"""Base for all logarithmic operations in information theory.
Base-2 ensures all entropy measures are in bits.
"""

# Bootstrap Parameters
DEFAULT_BOOTSTRAP_B: Final[int] = 1000
"""Default number of bootstrap samples for confidence intervals.
B = 1000 provides good balance between accuracy and computation time.
For higher-precision intervals, consider B = 5000-10000.
Reference: Efron & Tibshirani (1993), "An Introduction to the Bootstrap"
"""

FAST_BOOTSTRAP_B: Final[int] = 300
"""Fast bootstrap sample count for testing and development.
Used in unit tests to maintain reasonable execution times.
"""

SLOW_BOOTSTRAP_B: Final[int] = 5000
"""High-precision bootstrap sample count.
Use when tighter confidence intervals are worth the extra computation.
"""

# Confidence Levels
CONFIDENCE_LEVEL: Final[float] = 0.95
"""Standard confidence level for interval estimation.
95% corresponds to α = 0.05 significance level.
"""

ALPHA_LEVEL: Final[float] = 1 - CONFIDENCE_LEVEL
"""Significance level for hypothesis testing (α = 0.05)."""

CONF_INT_DEFAULT: Final[tuple[float, float]] = (2.5, 97.5)
"""Default (lower, upper) percentile bounds for bootstrap confidence intervals."""

# =============================================================================
# METRIC-SPECIFIC CONSTANTS
# =============================================================================

# Entanglement-Error Correlation (EEC)
EEC_LAMBDA: Final[float] = 1.0
"""Distance decay parameter for topology adjacency matrix.
A_ij = exp(-λ * d_ij) where d_ij is physical/logical distance.
λ = 1.0 provides reasonable decay for typical qubit layouts.
"""

# Pathway Persistence (PP)
PP_TOP_K_MIN: Final[int] = 5
"""Minimum number of top pathways to track for persistence."""

PP_TOP_K_MAX: Final[int] = 32
"""Maximum number of top pathways to avoid exponential explosion."""

PP_MASS_THRESHOLD: Final[float] = 0.8
"""Probability mass threshold for adaptive top-k selection.
Choose k such that top-k pathways capture ≥80% of total probability.
"""

PP_MIN_RUNS: Final[int] = 3
"""Minimum number of runs required for meaningful persistence calculation."""

# Canonical aliases for PP constants
MAX_TOP_K: Final[int] = PP_TOP_K_MAX
TOPK_MASS_TARGET: Final[float] = PP_MASS_THRESHOLD

# Complexity Emergence Score (CES)
CES_MIN_POINTS: Final[int] = 4
"""Minimum number of (n, SS) points needed for logistic fit."""

CES_MAX_QUBITS: Final[int] = 10
"""Maximum qubit count for complexity emergence analysis.
Beyond this, 2^n becomes computationally prohibitive.
"""

# Null Model Regularization
TIKHONOV_LAMBDA: Final[float] = 1e-3
"""Tikhonov regularization parameter for readout confusion inversion.
Prevents numerical instability when inverting near-singular matrices.
"""

# =============================================================================
# STATUS DETERMINATION THRESHOLDS
# =============================================================================

# Confidence Interval Quality
VALIDATED_CV_THRESHOLD: Final[float] = 0.33
"""Coefficient of variation threshold for 'validated' status.
CI half-width ≤ 0.33 * metric_value indicates high precision.
"""

STATUS_BAND_WIDTH: Final[float] = 0.33
"""Status band width for validated status determination.
Alias for VALIDATED_CV_THRESHOLD for registry compatibility.
"""

EXPERIMENTAL_CV_THRESHOLD: Final[float] = 0.50
"""Coefficient of variation threshold for 'experimental' status.
Above this threshold, results are marked as 'unstable'.
"""

# Sample Size Requirements
VALIDATED_MIN_SAMPLES: Final[int] = 100
"""Minimum number of samples for 'validated' status."""

EXPERIMENTAL_MIN_SAMPLES: Final[int] = 50
"""Minimum number of samples for 'experimental' status."""

UNSTABLE_MAX_SAMPLES: Final[int] = 20
"""Below this sample count, automatically mark as 'unstable'."""

# Statistical Significance
SIGNIFICANCE_P_VALUE: Final[float] = 0.05
"""P-value threshold for statistical significance.
Used when comparing metric values against null-model baselines.
"""

# =============================================================================
# PHYSICAL CONSTANTS & LIMITS
# =============================================================================

# Quantum System Limits
MAX_QUBITS_EXACT: Final[int] = 20
"""Maximum qubits for exact state vector calculations.
Beyond this, use sampling approximations or specialized algorithms.
"""

MAX_OUTCOMES_EXACT: Final[int] = 2**16
"""Maximum number of measurement outcomes for exact calculations.
Corresponds to 16 qubits for binary measurements.
"""

# Entanglement Bounds
GHZ_EXACT_TC_2QUBIT: Final[float] = 1.0
"""Exact total correlation for 2-qubit GHZ (Bell) state.
TC = H(X₁) + H(X₂) - H(X₁,X₂) = 1 + 1 - 1 = 1 bit.
"""

GHZ_EXACT_TC_3QUBIT: Final[float] = 2.0
"""Exact total correlation for 3-qubit GHZ state.
TC = 3 * 1 - 1 = 2 bits for ideal case.
"""

# =============================================================================
# INTERPRETATION THRESHOLDS
# =============================================================================

# Structure Detection
STRUCTURE_WEAK_THRESHOLD: Final[float] = 0.1
"""Weak threshold for distribution-structure metrics."""

STRUCTURE_MODERATE_THRESHOLD: Final[float] = 0.3
"""Moderate threshold for distribution-structure metrics."""

STRUCTURE_STRONG_THRESHOLD: Final[float] = 0.5
"""Strong threshold for distribution-structure metrics."""

# Correlation Strength
CORRELATION_WEAK_THRESHOLD: Final[float] = 0.2
"""Weak correlation threshold for EEC and other correlation metrics."""

CORRELATION_MODERATE_THRESHOLD: Final[float] = 0.5
"""Moderate correlation threshold for EEC and other correlation metrics."""

CORRELATION_STRONG_THRESHOLD: Final[float] = 0.8
"""Strong correlation threshold for EEC and other correlation metrics."""

# =============================================================================
# SCHEMA COMPLIANCE
# =============================================================================

SCHEMA_VERSION: Final[str] = "1.0"
"""Current schema version for all outputs.
Must match the frozen v1.0 schema suite exactly.
"""

# =============================================================================
# DEVELOPMENT & TESTING
# =============================================================================

# Random Seeds
DEFAULT_TEST_SEED: Final[int] = 123456789
"""Default random seed for reproducible testing."""

PERFORMANCE_TEST_SEED: Final[int] = 987654321
"""Separate seed for performance benchmarking."""

# Tolerances for Testing
NUMERICAL_TOLERANCE: Final[float] = 1e-10
"""Tolerance for numerical equality comparisons in tests."""

STATISTICAL_TOLERANCE: Final[float] = 1e-2
"""Tolerance for statistical property tests (entropy bounds, etc.)."""

# Test Data Sizes
SMALL_TEST_N: Final[int] = 3
"""Small qubit count for fast unit tests."""

MEDIUM_TEST_N: Final[int] = 5
"""Medium qubit count for integration tests."""

LARGE_TEST_N: Final[int] = 8
"""Large qubit count for stress tests (marked as slow)."""

SMALL_TEST_SHOTS: Final[int] = 1000
"""Small shot count for fast tests."""

MEDIUM_TEST_SHOTS: Final[int] = 10000
"""Medium shot count for accuracy tests."""

LARGE_TEST_SHOTS: Final[int] = 100000
"""Large shot count for high-precision validation."""

# =============================================================================
# PERFORMANCE TUNING
# =============================================================================

# Memory Management
MAX_COUNTS_DICT_SIZE: Final[int] = 2**16
"""Maximum size for counts dictionaries before warning.
Helps detect exponential memory explosion.
"""

# Parallel Processing
DEFAULT_N_JOBS: Final[int] = -1
"""Default number of parallel jobs (-1 = use all cores)."""

# Cache Settings
ENABLE_RESULT_CACHING: Final[bool] = False
"""Whether to enable result caching (disabled by default to ensure freshness)."""

# =============================================================================
# VALIDATION HELPERS
# =============================================================================


def validate_probability_array(p: np.ndarray, name: str = "probability") -> np.ndarray:
    """Validate and normalize probability array with safety checks."""
    p = np.asarray(p, dtype=np.float64)

    if np.any(p < 0):
        raise ValueError(f"{name} array contains negative values")

    if np.allclose(p.sum(), 0.0):
        raise ValueError(f"{name} array sums to zero")

    # Normalize
    p = p / p.sum()

    # Apply safety clamping
    p = np.clip(p, EPS, 1.0)
    p = p / p.sum()  # Renormalize after clamping

    return p


def validate_counts_dict(counts: Mapping[str, int], name: str = "counts") -> dict[str, int]:
    """Validate counts dictionary for binary strings and positive counts."""
    if not counts:
        raise ValueError(f"{name} dictionary is empty")

    # Check all values are non-negative integers
    for bitstring, count in counts.items():
        if not isinstance(count, int) or count < 0:
            raise ValueError(f"{name}['{bitstring}'] = {count} is not a non-negative integer")

    # Check bitstring consistency
    lengths = {len(bs) for bs in counts.keys()}
    if len(lengths) > 1:
        raise ValueError(f"{name} contains bitstrings of inconsistent lengths: {lengths}")

    # Check binary format
    for bitstring in counts.keys():
        if not all(c in "01" for c in bitstring):
            raise ValueError(f"{name} contains non-binary bitstring: '{bitstring}'")

    return dict(counts)


def get_status_thresholds() -> dict:
    """Get status determination thresholds as a dictionary."""
    return {
        "validated_cv": VALIDATED_CV_THRESHOLD,
        "experimental_cv": EXPERIMENTAL_CV_THRESHOLD,
        "validated_min_samples": VALIDATED_MIN_SAMPLES,
        "experimental_min_samples": EXPERIMENTAL_MIN_SAMPLES,
        "significance_p": SIGNIFICANCE_P_VALUE,
    }


# Public exports
__all__ = [
    # Core knobs
    "ALPHA",
    "EPS",
    "LOG_BASE",
    "SCHEMA_VERSION",
    "DEFAULT_BOOTSTRAP_B",
    "FAST_BOOTSTRAP_B",
    "SLOW_BOOTSTRAP_B",
    "CONFIDENCE_LEVEL",
    "ALPHA_LEVEL",
    "CONF_INT_DEFAULT",
    # Metric-specific
    "EEC_LAMBDA",
    "PP_TOP_K_MIN",
    "PP_TOP_K_MAX",
    "PP_MASS_THRESHOLD",
    "PP_MIN_RUNS",
    "CES_MIN_POINTS",
    "CES_MAX_QUBITS",
    "TIKHONOV_LAMBDA",
    # Canonical aliases for public API
    "MAX_TOP_K",
    "TOPK_MASS_TARGET",
    # Status thresholds
    "VALIDATED_CV_THRESHOLD",
    "STATUS_BAND_WIDTH",
    "EXPERIMENTAL_CV_THRESHOLD",
    "VALIDATED_MIN_SAMPLES",
    "EXPERIMENTAL_MIN_SAMPLES",
    "UNSTABLE_MAX_SAMPLES",
    "SIGNIFICANCE_P_VALUE",
    # Physical/reference values
    "MAX_QUBITS_EXACT",
    "MAX_OUTCOMES_EXACT",
    "GHZ_EXACT_TC_2QUBIT",
    "GHZ_EXACT_TC_3QUBIT",
    # Dev & testing
    "DEFAULT_TEST_SEED",
    "PERFORMANCE_TEST_SEED",
    "NUMERICAL_TOLERANCE",
    "STATISTICAL_TOLERANCE",
    "SMALL_TEST_N",
    "MEDIUM_TEST_N",
    "LARGE_TEST_N",
    "SMALL_TEST_SHOTS",
    "MEDIUM_TEST_SHOTS",
    "LARGE_TEST_SHOTS",
    # Performance & execution
    "MAX_COUNTS_DICT_SIZE",
    "DEFAULT_N_JOBS",
    "ENABLE_RESULT_CACHING",
    # Validators / helpers
    "validate_probability_array",
    "validate_counts_dict",
    "get_status_thresholds",
]
