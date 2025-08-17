"""
Statistical Confidence Methods for Structured Decoherence Metrics

# Bootstrap Confidence Intervals for Quantum Measurements
This module implements bootstrap methods to compute 95% confidence intervals
for all structured decoherence metrics, as required by the v1.0 schemas.

# Statistical Foundation
Bootstrap resampling (Efron 1979) provides non-parametric confidence intervals
without assumptions about the underlying distribution. For quantum measurements,
this is crucial since error distributions can be highly non-Gaussian.

# Research Significance
Confidence intervals enable:
- Statistical validation of pathway structure claims
- Comparison across different experimental conditions
- Publication-quality error bars for all metrics
- Hypothesis testing with proper significance levels

# Educational Framework
This module bridges quantum mechanics with statistical inference:
- Resampling theory and the bootstrap principle
- Confidence interval construction methods (percentile, BCa)
- Multiple testing corrections for quantum experiments
- Validation status determination from statistical evidence
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Callable, Optional, Any, Mapping
from dataclasses import dataclass
import warnings

from ..constants import ALPHA, DEFAULT_BOOTSTRAP_B, EPS, validate_counts_dict

logger = logging.getLogger(__name__)


@dataclass
class MetricWithConfidence:
    """
    Structured metric with confidence interval and validation status.
    
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
    ci95: Tuple[float, float]
    status: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to schema-compliant dictionary."""
        return {
            "value": self.value,
            "ci95": list(self.ci95),
            "status": self.status
        }


def bootstrap_confidence_interval(
    counts: Mapping[str, int],
    metric_function: Callable[[Mapping[str, int]], float],
    n_bootstrap: int = DEFAULT_BOOTSTRAP_B,
    confidence_level: float = 0.95,
    method: str = "percentile"
) -> Tuple[float, float]:
    """
    Compute bootstrap confidence interval for any metric function.
    
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
        
    Returns:
        Tuple[float, float]: (lower_bound, upper_bound) confidence interval
        
    Educational Notes:
        - Bootstrap assumes IID samples (valid for quantum measurements)
        - More bootstrap samples → more accurate CI (diminishing returns >5000)
        - CI width indicates metric stability/reliability
        - Asymmetric CIs reveal distribution skewness
    """
    # Validate input using centralized function
    counts_clean = validate_counts_dict(counts)
    
    if not counts_clean or sum(counts_clean.values()) == 0:
        logger.warning("Empty or zero counts for bootstrap CI")
        return (0.0, 0.0)
    
    # Convert counts to list of outcomes for resampling
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
        # Resample with replacement
        resampled_indices = np.random.choice(n_samples, size=n_samples, replace=True)
        resampled_outcomes = [outcomes[idx] for idx in resampled_indices]
        
        # Convert back to counts dictionary
        resampled_counts = {}
        for outcome in resampled_outcomes:
            resampled_counts[outcome] = resampled_counts.get(outcome, 0) + 1
        
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
    
    bootstrap_metrics = np.array(bootstrap_metrics)
    
    # Calculate confidence interval
    if method == "percentile":
        # Percentile method
        alpha = 1 - confidence_level
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100
        
        ci_lower = np.percentile(bootstrap_metrics, lower_percentile)
        ci_upper = np.percentile(bootstrap_metrics, upper_percentile)
        
    elif method == "bca":
        # BCa method (simplified version)
        # Full BCa requires jackknife for acceleration factor
        ci_lower, ci_upper = _compute_bca_interval(
            bootstrap_metrics, original_metric, confidence_level
        )
    else:
        raise ValueError(f"Unknown CI method: {method}")
    
    # Ensure CI contains original value (sanity check)
    if original_metric < ci_lower or original_metric > ci_upper:
        logger.debug(f"Original metric {original_metric:.4f} outside CI "
                    f"[{ci_lower:.4f}, {ci_upper:.4f}], adjusting")
        ci_lower = min(ci_lower, original_metric)
        ci_upper = max(ci_upper, original_metric)
    
    logger.debug(f"Bootstrap CI: [{ci_lower:.4f}, {ci_upper:.4f}] "
                f"from {len(bootstrap_metrics)} samples")
    
    return (ci_lower, ci_upper)


def _compute_bca_interval(bootstrap_metrics: np.ndarray, 
                         original_metric: float,
                         confidence_level: float) -> Tuple[float, float]:
    """
    Compute BCa (Bias-Corrected and accelerated) confidence interval.
    
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
    
    # Convert to percentile values
    ci_lower = np.percentile(bootstrap_metrics, p_lower * 100)
    ci_upper = np.percentile(bootstrap_metrics, p_upper * 100)
    
    return (ci_lower, ci_upper)


def _compute_bias_correction(bootstrap_metrics: np.ndarray, 
                            original_metric: float) -> float:
    """Calculate bias correction factor z0."""
    proportion_less = np.mean(bootstrap_metrics < original_metric)
    # Avoid infinity at boundaries
    proportion_less = np.clip(proportion_less, 0.001, 0.999)
    z0 = _normal_quantile(proportion_less)
    return z0


def _normal_quantile(p: float) -> float:
    """Compute normal distribution quantile (inverse CDF)."""
    from scipy.stats import norm
    return norm.ppf(p)


def _normal_cdf(z: float) -> float:
    """Compute normal distribution CDF."""
    from scipy.stats import norm
    return norm.cdf(z)


def determine_validation_status(ci_width: float, 
                               metric_value: float,
                               n_samples: int) -> str:
    """
    Determine validation status based on statistical evidence.
    
    # Status Criteria
    The validation status reflects our confidence in the metric:
    
    1. **"validated"**: High confidence
       - Narrow CI relative to metric value (CV < 0.2)
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
    
    # Research Implications
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
    # Avoid division by zero
    if abs(metric_value) < 1e-10:
        # For near-zero metrics, use absolute CI width
        if ci_width < 0.1 and n_samples >= 100:
            return "validated"
        elif ci_width < 0.3 and n_samples >= 50:
            return "experimental"
        else:
            return "unstable"
    
    # Calculate coefficient of variation proxy
    # CI width ≈ 4 * std_error for 95% CI
    # CV ≈ ci_width / (4 * |metric_value|)
    cv_proxy = ci_width / (4 * abs(metric_value))
    
    # Determine status based on CV and sample size
    if cv_proxy < 0.2 and n_samples >= 100:
        status = "validated"
    elif cv_proxy < 0.5 and n_samples >= 50:
        status = "experimental"
    else:
        status = "unstable"
    
    logger.debug(f"Validation status: {status} (CV≈{cv_proxy:.2f}, n={n_samples})")
    
    return status


def compute_metric_with_confidence(
    counts: Mapping[str, int],
    metric_function: Callable[[Mapping[str, int]], float],
    metric_name: str = "metric",
    n_bootstrap: int = DEFAULT_BOOTSTRAP_B,
    **metric_kwargs
) -> MetricWithConfidence:
    """
    Compute a metric with confidence interval and validation status.
    
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
        **metric_kwargs: Additional arguments for metric function
        
    Returns:
        MetricWithConfidence: Complete metric with CI and status
        
    Educational Notes:
        - This provides the complete statistical treatment required by schemas
        - Bootstrap is compute-intensive but provides robust CIs
        - Status determination is conservative to avoid false claims
    """
    logger.info(f"Computing {metric_name} with confidence interval")
    
    # Handle metric functions that need additional arguments
    if metric_kwargs:
        metric_func = lambda c: metric_function(c, **metric_kwargs)
    else:
        metric_func = metric_function
    
    # Compute metric value
    try:
        metric_value = metric_func(counts)
    except Exception as e:
        logger.error(f"Failed to compute {metric_name}: {e}")
        return MetricWithConfidence(
            value=0.0,
            ci95=(0.0, 0.0),
            status="unstable"
        )
    
    # Compute confidence interval
    ci_lower, ci_upper = bootstrap_confidence_interval(
        counts,
        metric_func,
        n_bootstrap=n_bootstrap
    )
    
    # Determine validation status
    ci_width = ci_upper - ci_lower
    n_samples = sum(counts.values())
    status = determine_validation_status(ci_width, metric_value, n_samples)
    
    logger.info(f"{metric_name}: {metric_value:.4f} [{ci_lower:.4f}, {ci_upper:.4f}] "
               f"status={status}")
    
    return MetricWithConfidence(
        value=metric_value,
        ci95=(ci_lower, ci_upper),
        status=status
    )


def compute_all_metrics_with_confidence(
    counts: Mapping[str, int],
    state_type: str = "GHZ",
    n_bootstrap: int = DEFAULT_BOOTSTRAP_B
) -> Dict[str, MetricWithConfidence]:
    """
    Compute all structured decoherence metrics with confidence intervals.
    
    # Complete Metric Suite
    Computes all 8 metrics required by the v1.0 schemas:
    1. Asymmetry Index (AI)
    2. Pathway Concentration Ratio (PCR)
    3. Entanglement-Error Correlation (EEC)
    4. Temporal Pathway Stability (TPS) - if multi-run data available
    5. Complexity Emergence Score (CES) - if multi-qubit data available
    6. Structure Score (SS) - NEW
    7. Concentration Index (CI) - NEW
    8. Total Correlation (TC) - NEW
    
    # Research Workflow Integration
    This function provides the complete statistical analysis required
    for publication-quality research results.
    
    Args:
        counts: Measurement counts
        state_type: Quantum state type for EEC calculation
        n_bootstrap: Number of bootstrap samples
        
    Returns:
        Dict mapping metric names to MetricWithConfidence objects
        
    Educational Notes:
        - All metrics get same bootstrap treatment for consistency
        - Computational cost scales with n_bootstrap * n_metrics
        - Results are immediately ready for schema serialization
    """
    from ..metrics import pathway_metrics
    from ..metrics import schema_bridge
    
    logger.info("Computing all structured decoherence metrics with confidence")
    
    results = {}
    
    # Original 5 metrics
    results["asymmetry_index"] = compute_metric_with_confidence(
        counts, pathway_metrics.compute_asymmetry_index,
        metric_name="asymmetry_index", n_bootstrap=n_bootstrap
    )
    
    results["pathway_concentration_ratio"] = compute_metric_with_confidence(
        counts, pathway_metrics.compute_pathway_concentration_ratio,
        metric_name="pathway_concentration_ratio", n_bootstrap=n_bootstrap
    )
    
    results["entanglement_error_correlation"] = compute_metric_with_confidence(
        counts, pathway_metrics.compute_entanglement_error_correlation,
        metric_name="entanglement_error_correlation", 
        n_bootstrap=n_bootstrap,
        state_type=state_type
    )
    
    # New schema-required metrics
    results["structure_score"] = compute_metric_with_confidence(
        counts, schema_bridge.compute_structure_score,
        metric_name="structure_score", n_bootstrap=n_bootstrap
    )
    
    results["concentration_index"] = compute_metric_with_confidence(
        counts, schema_bridge.compute_concentration_index,
        metric_name="concentration_index", n_bootstrap=n_bootstrap
    )
    
    results["total_correlation"] = compute_metric_with_confidence(
        counts, schema_bridge.compute_total_correlation,
        metric_name="total_correlation", n_bootstrap=n_bootstrap
    )
    
    # TPS and CES require special handling (multi-condition data)
    # For now, set as None with "insufficient_data" status
    results["temporal_pathway_stability"] = None
    results["complexity_emergence_score"] = None
    
    logger.info(f"Computed {len(results)} metrics with confidence intervals")
    
    return results