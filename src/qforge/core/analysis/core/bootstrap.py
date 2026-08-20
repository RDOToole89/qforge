"""Statistical confidence methods for analysis metrics.

# Bootstrap Confidence Intervals for Quantum Measurements
This module implements bootstrap methods to compute 95% confidence intervals
for all analysis metrics, as required by the v1.0 schemas.

# Statistical Foundation
Bootstrap resampling (Efron 1979) provides non-parametric confidence intervals
without assumptions about the underlying distribution. For quantum measurements,
this is crucial since error distributions can be highly non-Gaussian.

# Statistical Significance
Confidence intervals enable:
- Quantifying uncertainty in each metric value
- Comparison across different experimental conditions
- Error bars for all metrics
- Significance testing with proper thresholds

# Educational Framework
This module bridges quantum mechanics with statistical inference:
- Resampling theory and the bootstrap principle
- Confidence interval construction methods (percentile, BCa)
- Multiple testing corrections for quantum experiments
- Validation status determination from statistical evidence
"""

from __future__ import annotations

import logging
import warnings
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

import numpy as np

from ..constants import (
    DEFAULT_BOOTSTRAP_B,
    EXPERIMENTAL_CV_THRESHOLD,
    EXPERIMENTAL_MIN_SAMPLES,
    VALIDATED_CV_THRESHOLD,
    VALIDATED_MIN_SAMPLES,
    validate_counts_dict,
)

logger = logging.getLogger(__name__)


@dataclass
class MetricWithConfidence:
    """Structured metric with confidence interval and validation status.

    # Schema Compliance
    Matches the structure required by structure_metrics.schema.json:
    - value: The computed metric value
    - ci95: [lower, upper] 95% confidence interval
    - status: Validation status based on statistical evidence

    # Status Determination
    - "validated": Tight CI, sufficient samples, consistent results
    - "experimental": Moderate CI, adequate samples, some variation
    - "unstable": Wide CI, insufficient samples, high variation
    """

    value: float
    ci95: tuple[float, float]
    status: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to schema-compliant dictionary."""
        return {"value": self.value, "ci95": list(self.ci95), "status": self.status}


def bootstrap_confidence_interval(
    counts: Mapping[str, int],
    metric_function: Callable[[Mapping[str, int]], float],
    n_bootstrap: int = DEFAULT_BOOTSTRAP_B,
    confidence_level: float = 0.95,
    method: str = "percentile",
    rng: np.random.Generator | None = None,
    # compatibility alias; if provided, use it when rng is None
    random_state: np.random.Generator | None = None,
) -> tuple[float, float]:
    """Compute bootstrap confidence interval for any metric function.

     # Bootstrap Resampling Theory
     The bootstrap principle: The sampling distribution of a statistic can be
     approximated by the distribution of that statistic computed from resamples
     of the original data with replacement.

     # Quantum Measurement Context
     For quantum measurements, we resample from the empirical distribution
     of measurement outcomes. Each bootstrap sample represents a possible
     experimental realization with the same number of shots.

     # Confidence Interval Methods
     1. **Percentile Method**: Direct quantiles of bootstrap distribution
        - Simple and intuitive
        - Works well for symmetric distributions
        - May be biased for skewed distributions

     2. **BCa Method** (Bias-Corrected and accelerated):
        - Corrects for bias and skewness
        - More accurate for small samples
        - Computationally intensive

    Args:
     counts: Original measurement counts {bitstring: count}
     metric_function: Function that computes metric from counts
     n_bootstrap: Number of bootstrap samples (≥1000 recommended)
     confidence_level: Confidence level (0.95 for 95% CI)
     method: "percentile" or "bca"
     rng: Optional NumPy Generator for reproducible resampling.
     random_state: Deprecated alias; used only if rng is None.

    Returns:
         Tuple[float, float]: (lower_bound, upper_bound) confidence interval

     Educational Notes:
         - Bootstrap assumes IID samples (valid for quantum measurements)
         - More bootstrap samples → more accurate CI (diminishing returns >5000)
         - CI width indicates metric stability/reliability
         - Asymmetric CIs reveal distribution skewness
    """
    if n_bootstrap <= 0:
        raise ValueError(f"n_bootstrap must be positive, got {n_bootstrap}")
    if rng is None:
        rng = random_state or np.random.default_rng()

    # Validate input using centralized function
    counts_clean = validate_counts_dict(counts)

    if not counts_clean or sum(counts_clean.values()) == 0:
        logger.warning("Empty or zero counts for bootstrap CI")
        return (0.0, 0.0)

    # Build outcome list once
    outcomes = []
    for bitstring, count in counts_clean.items():
        outcomes.extend([bitstring] * count)
    n_samples = len(outcomes)

    if n_samples < 10:
        logger.warning(f"Very few samples ({n_samples}) for reliable bootstrap CI")

    # Compute original metric value
    original_metric = metric_function(counts_clean)

    # Bootstrap resampling
    bootstrap_metrics = []

    for i in range(n_bootstrap):
        # Use rng for reproducibility; integers faster than choice-of-objects
        resampled_indices = rng.integers(0, n_samples, size=n_samples, endpoint=False)
        resampled_counts: dict[str, int] = {}
        for idx in resampled_indices:
            o = outcomes[idx]
            resampled_counts[o] = resampled_counts.get(o, 0) + 1

        # Compute metric on resampled data
        try:
            bootstrap_metric = metric_function(resampled_counts)
            bootstrap_metrics.append(bootstrap_metric)
        except Exception as e:
            logger.debug(f"Bootstrap sample {i} failed: {e}")
            continue

    if len(bootstrap_metrics) < n_bootstrap * 0.9:
        logger.warning(f"Many bootstrap samples failed: {len(bootstrap_metrics)}/{n_bootstrap}")

    if not bootstrap_metrics:
        logger.error("All bootstrap samples failed")
        return (original_metric, original_metric)

    bootstrap_array = np.array(bootstrap_metrics)

    # Calculate confidence interval
    ci_lower: float
    ci_upper: float
    if method == "percentile":
        # Percentile method
        alpha = 1 - confidence_level
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100

        ci_lower = float(np.percentile(bootstrap_array, lower_percentile))
        ci_upper = float(np.percentile(bootstrap_array, upper_percentile))

    elif method == "bca":
        try:
            ci_lower, ci_upper = _compute_bca_interval(
                bootstrap_array, original_metric, confidence_level
            )
        except Exception:
            alpha = 1 - confidence_level
            lower_percentile = (alpha / 2) * 100
            upper_percentile = (1 - alpha / 2) * 100
            ci_lower = float(np.percentile(bootstrap_array, lower_percentile))
            ci_upper = float(np.percentile(bootstrap_array, upper_percentile))
    else:
        raise ValueError(f"Unknown CI method: {method}")

    # Ensure CI contains original value (sanity check)
    if original_metric < ci_lower or original_metric > ci_upper:
        logger.debug(
            f"Original metric {original_metric:.4f} outside CI "
            f"[{ci_lower:.4f}, {ci_upper:.4f}], adjusting"
        )
        ci_lower = min(ci_lower, original_metric)
        ci_upper = max(ci_upper, original_metric)

    logger.debug(
        f"Bootstrap CI: [{ci_lower:.4f}, {ci_upper:.4f}] from {len(bootstrap_metrics)} samples"
    )

    return (float(ci_lower), float(ci_upper))


def _compute_bca_interval(
    bootstrap_metrics: np.ndarray, original_metric: float, confidence_level: float
) -> tuple[float, float]:
    """Compute BCa (Bias-Corrected and accelerated) confidence interval.

    # BCa Method
    Adjusts percentile endpoints to account for:
    1. Bias: Median of bootstrap distribution ≠ original estimate
    2. Acceleration: Rate of change of standard error with parameter value

    Simplified version without jackknife acceleration factor.
    """
    # Calculate bias correction factor
    z0 = _compute_bias_correction(bootstrap_metrics, original_metric)

    # For simplified BCa, set acceleration to 0
    a = 0

    # Calculate adjusted percentiles
    alpha = 1 - confidence_level
    z_alpha_2 = _normal_quantile(alpha / 2)
    z_1_alpha_2 = _normal_quantile(1 - alpha / 2)

    # Adjusted percentiles
    p_lower = _normal_cdf(z0 + (z0 + z_alpha_2) / (1 - a * (z0 + z_alpha_2)))
    p_upper = _normal_cdf(z0 + (z0 + z_1_alpha_2) / (1 - a * (z0 + z_1_alpha_2)))

    # numeric safety bounds
    p_lower = float(np.clip(p_lower, 1e-6, 1 - 1e-6))
    p_upper = float(np.clip(p_upper, 1e-6, 1 - 1e-6))
    # Convert to percentile values
    ci_lower = np.percentile(bootstrap_metrics, p_lower * 100)
    ci_upper = np.percentile(bootstrap_metrics, p_upper * 100)

    return (float(ci_lower), float(ci_upper))


def _compute_bias_correction(bootstrap_metrics: np.ndarray, original_metric: float) -> float:
    """Calculate bias correction factor z0."""
    proportion_less = np.mean(bootstrap_metrics < original_metric)
    # Avoid infinity at boundaries
    proportion_less = np.clip(proportion_less, 0.001, 0.999)
    z0 = _normal_quantile(proportion_less)
    return z0


def _normal_quantile(p: float) -> float:
    """Compute normal distribution quantile (inverse CDF)."""
    try:
        from scipy.stats import norm

        return float(norm.ppf(p))
    except Exception:
        warnings.warn("BCa requires SciPy; falling back to percentile CI.", stacklevel=2)
        raise


def _normal_cdf(z: float) -> float:
    """Compute normal distribution CDF."""
    try:
        from scipy.stats import norm

        return float(norm.cdf(z))
    except Exception:
        warnings.warn("BCa requires SciPy; falling back to percentile CI.", stacklevel=2)
        raise


def determine_validation_status(ci_width: float, metric_value: float, n_samples: int) -> str:
    """Determine validation status based on statistical evidence.

    # Status Criteria
    The validation status reflects our confidence in the metric:

    1. **"validated"**: High confidence
       - Narrow CI relative to metric value (CV < 0.33)
       - Sufficient samples (≥100)
       - Metric significantly different from zero

    2. **"experimental"**: Moderate confidence
       - Moderate CI width (CV < 0.5)
       - Adequate samples (≥50)
       - Some statistical significance

    3. **"unstable"**: Low confidence
       - Wide CI or very few samples
       - High coefficient of variation
       - Results should be interpreted with caution

    # Interpretation
    - Only "validated" metrics should be used for strong claims
    - "Experimental" metrics suggest trends worth investigating
    - "Unstable" metrics need more data before interpretation

    Args:
        ci_width: Width of confidence interval (upper - lower)
        metric_value: The computed metric value
        n_samples: Number of measurement samples

    Returns:
        str: "validated", "experimental", or "unstable"

    Educational Notes:
        - Coefficient of Variation (CV) = std_dev / mean
        - CI width ≈ 2 * std_dev for normal distributions
        - Sample size affects reliability regardless of CI width
    """
    # Near-zero value: use absolute CI width + sample thresholds
    if abs(metric_value) < 1e-10:
        if ci_width < 0.1 and n_samples >= VALIDATED_MIN_SAMPLES:
            return "validated"
        if ci_width < 0.3 and n_samples >= EXPERIMENTAL_MIN_SAMPLES:
            return "experimental"
        return "unstable"

    # CI width ≈ 4 * std_error for 95% CI (proxy)
    cv_proxy = ci_width / (4 * abs(metric_value))

    if cv_proxy <= VALIDATED_CV_THRESHOLD and n_samples >= VALIDATED_MIN_SAMPLES:
        return "validated"
    if cv_proxy <= EXPERIMENTAL_CV_THRESHOLD and n_samples >= EXPERIMENTAL_MIN_SAMPLES:
        return "experimental"
    return "unstable"


def compute_metric_with_confidence(
    counts: Mapping[str, int],
    metric_function: Callable[[Mapping[str, int]], float],
    metric_name: str = "metric",
    n_bootstrap: int = DEFAULT_BOOTSTRAP_B,
    rng: np.random.Generator | None = None,
    **metric_kwargs: Any,
) -> MetricWithConfidence:
    """Compute a metric with confidence interval and validation status.

    # Complete Statistical Pipeline
    1. Compute metric value from original data
    2. Bootstrap resample to get confidence interval
    3. Determine validation status from statistical evidence
    4. Package into schema-compliant structure

    # Usage Pattern
    This is the main interface for computing schema-compliant metrics:
    ```python
    result = compute_metric_with_confidence(
        counts,
        compute_asymmetry_index,
        metric_name="asymmetry_index"
    )
    ```

    Args:
        counts: Measurement counts
        metric_function: Function to compute metric
        metric_name: Name for logging
        n_bootstrap: Number of bootstrap samples
        rng: NumPy random generator for reproducible bootstrap sampling.
        **metric_kwargs: Additional arguments for metric function

    Returns:
        MetricWithConfidence: Complete metric with CI and status

    Educational Notes:
        - This provides the complete statistical treatment required by schemas
        - Bootstrap is compute-intensive but provides robust CIs
        - Status determination is conservative to avoid false claims
    """
    logger.info(f"Computing {metric_name} with confidence interval")

    # Bind kwargs (including rng) for metric if needed
    metric_func: Callable[[Mapping[str, int]], float]
    if metric_kwargs:

        def _bound_metric(c: Mapping[str, int]) -> float:
            return metric_function(c, **metric_kwargs)

        metric_func = _bound_metric
    else:
        metric_func = metric_function

    try:
        metric_value = metric_func(counts)
    except Exception as e:
        logger.error(f"Failed to compute {metric_name}: {e}")
        return MetricWithConfidence(value=0.0, ci95=(0.0, 0.0), status="unstable")

    ci_lower, ci_upper = bootstrap_confidence_interval(
        counts,
        metric_func,
        n_bootstrap=n_bootstrap,
        rng=rng,  # <- pass through
    )

    # Determine validation status
    ci_width = ci_upper - ci_lower
    n_samples = sum(counts.values())
    status = determine_validation_status(ci_width, metric_value, n_samples)

    logger.info(
        f"{metric_name}: {metric_value:.4f} [{ci_lower:.4f}, {ci_upper:.4f}] status={status}"
    )

    return MetricWithConfidence(value=metric_value, ci95=(ci_lower, ci_upper), status=status)


# compute_all_metrics_with_confidence removed - moved to pipelines for decoupling
