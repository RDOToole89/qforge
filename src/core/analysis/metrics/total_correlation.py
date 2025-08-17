"""
Total Correlation - Multi-Information Analysis

This module provides the canonical implementation of Total Correlation (TC)
for the v1.0 schema compliance, wrapping the core information theory
implementation with the registry system.
"""

from .registry import MetricResult, register, determine_status
from ..core.information_theory import total_correlation as core_total_correlation
from ..core.bootstrap import bootstrap_confidence_interval
from ..constants import DEFAULT_BOOTSTRAP_B, ALPHA
import numpy as np
import logging

logger = logging.getLogger(__name__)

@register("total_correlation")
def compute_total_correlation(*, counts, alpha: float = ALPHA, 
                            B: int = DEFAULT_BOOTSTRAP_B, rng=None, **kwargs) -> MetricResult:
    """
    Compute Total Correlation with bootstrap confidence intervals.
    
    Total Correlation measures the total amount of correlation among all variables:
    TC = Σᵢ H(Xᵢ) - H(X₁, X₂, ..., Xₙ)
    
    Args:
        counts: Measurement counts {bitstring: count}
        alpha: Jeffreys prior parameter
        B: Bootstrap samples for confidence interval
        rng: Random number generator
        **kwargs: Additional arguments (ignored)
        
    Returns:
        MetricResult with value, ci95, status, and extras
    """
    if not counts:
        return MetricResult(
            value=0.0,
            ci95=(0.0, 0.0),
            status="insufficient_data",
            extras={"reason": "Empty counts dictionary"}
        )
    
    if rng is None:
        rng = np.random.default_rng()
    
    try:
        # Compute primary value
        tc_value = core_total_correlation(counts, alpha=alpha)
        
        # Bootstrap confidence interval
        def tc_bootstrap_fn(bootstrap_counts):
            return core_total_correlation(bootstrap_counts, alpha=alpha)
        
        ci_lower, ci_upper = bootstrap_confidence_interval(
            counts, tc_bootstrap_fn, n_bootstrap=B
        )
        
        # Determine status
        n_samples = sum(counts.values())
        extras = {
            "n_samples": n_samples,
            "n_qubits": len(next(iter(counts.keys()))),
            "n_outcomes": len(counts),
            "method": "total_correlation"
        }
        
        status = determine_status(tc_value, (ci_lower, ci_upper), extras)
        
        logger.debug(f"Total Correlation = {tc_value:.4f} [{ci_lower:.4f}, {ci_upper:.4f}] ({status})")
        
        return MetricResult(
            value=tc_value,
            ci95=(ci_lower, ci_upper),
            status=status,
            extras=extras
        )
        
    except Exception as e:
        logger.error(f"Error computing total correlation: {e}")
        return MetricResult(
            value=0.0,
            ci95=(0.0, 0.0),
            status="unstable",
            extras={"error": str(e)}
        )