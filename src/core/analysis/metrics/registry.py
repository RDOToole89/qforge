"""
Metrics Registry and Public API

Centralized registry system for all structured decoherence metrics with
standardized API, type safety, and schema compliance.

This module provides:
- MetricResult TypedDict for consistent return types
- Registry decorator for metric registration  
- compute_metric() and compute_all() for unified API
- Status determination logic for research quality assessment
"""

from typing import TypedDict, Literal, Callable, Any, Dict, List, Optional
import logging
from functools import wraps

from ..constants import STATUS_BAND_WIDTH

logger = logging.getLogger(__name__)

# Type definitions
Status = Literal["validated", "experimental", "unstable", "insufficient_runs", "insufficient_data"]

class MetricResult(TypedDict, total=False):
    """Standardized metric result with confidence intervals and status."""
    value: float
    ci95: tuple[float, float]
    status: Status
    extras: Dict[str, Any]

# Global registry
_METRIC_REGISTRY: Dict[str, Callable] = {}

def register(name: str) -> Callable:
    """
    Decorator to register a metric function in the global registry.
    
    Args:
        name: Canonical metric name for registry and schema
        
    Returns:
        Decorator function that registers the metric
        
    Example:
        >>> @register("structure_score")
        >>> def compute_structure_score(**kwargs) -> MetricResult:
        ...     return {"value": 0.5, "status": "validated"}
    """
    def decorator(func: Callable) -> Callable:
        _METRIC_REGISTRY[name] = func
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> MetricResult:
            return func(*args, **kwargs)
        
        logger.debug(f"Registered metric: {name}")
        return wrapper
    
    return decorator

def compute_metric(name: str, **kwargs) -> MetricResult:
    """
    Compute a single metric by name.
    
    Args:
        name: Registered metric name
        **kwargs: Arguments passed to metric function
        
    Returns:
        MetricResult with value, confidence interval, and status
        
    Raises:
        KeyError: If metric name is not registered
        
    Example:
        >>> result = compute_metric("structure_score", counts={"00": 500, "11": 500})
        >>> print(f"SS = {result['value']:.3f} [{result['ci95'][0]:.3f}, {result['ci95'][1]:.3f}]")
    """
    if name not in _METRIC_REGISTRY:
        available = list(_METRIC_REGISTRY.keys())
        raise KeyError(f"Unknown metric '{name}'. Available: {available}")
    
    metric_func = _METRIC_REGISTRY[name]
    logger.debug(f"Computing metric: {name}")
    
    try:
        result = metric_func(**kwargs)
        logger.debug(f"Metric {name}: value={result.get('value', 'N/A')}, status={result.get('status', 'unknown')}")
        return result
    except Exception as e:
        logger.error(f"Error computing metric {name}: {e}")
        return MetricResult(
            value=0.0,
            ci95=(0.0, 0.0),
            status="unstable",
            extras={"error": str(e)}
        )

def compute_all(metric_names: Optional[List[str]] = None, **kwargs) -> Dict[str, MetricResult]:
    """
    Compute multiple metrics with shared parameters.
    
    Args:
        metric_names: List of metric names to compute (None = all available)
        **kwargs: Shared arguments passed to all metric functions
        
    Returns:
        Dictionary mapping metric names to MetricResult objects
        
    Conditional Metrics:
        - pathway_persistence: requires 'runs' parameter
        - complexity_emergence_score: requires 'n_values' and 'ss_values'
        
    Example:
        >>> counts = {"000": 400, "111": 400, "001": 100, "110": 100}
        >>> results = compute_all(counts=counts, rng=np.random.default_rng(123))
        >>> for name, result in results.items():
        ...     print(f"{name}: {result['value']:.3f} ({result['status']})")
    """
    if metric_names is None:
        metric_names = list(_METRIC_REGISTRY.keys())
    
    results = {}
    
    for name in metric_names:
        if name not in _METRIC_REGISTRY:
            logger.warning(f"Skipping unknown metric: {name}")
            continue
        
        # Check conditional requirements
        if name == "pathway_persistence":
            if "runs" not in kwargs:
                logger.debug(f"Skipping {name}: requires 'runs' parameter")
                results[name] = MetricResult(
                    value=0.0,
                    ci95=(0.0, 0.0),
                    status="insufficient_runs",
                    extras={"reason": "Missing 'runs' parameter"}
                )
                continue
        
        elif name == "complexity_emergence_score":
            if "n_values" not in kwargs or "ss_values" not in kwargs:
                logger.debug(f"Skipping {name}: requires 'n_values' and 'ss_values'")
                results[name] = MetricResult(
                    value=0.0,
                    ci95=(0.0, 0.0),
                    status="insufficient_data",
                    extras={"reason": "Missing series data"}
                )
                continue
        
        # Compute metric
        try:
            results[name] = compute_metric(name, **kwargs)
        except Exception as e:
            logger.error(f"Failed to compute {name}: {e}")
            results[name] = MetricResult(
                value=0.0,
                ci95=(0.0, 0.0),
                status="unstable",
                extras={"error": str(e)}
            )
    
    logger.info(f"Computed {len(results)} metrics")
    return results

def determine_status(value: float, 
                    ci95: tuple[float, float],
                    extras: Optional[Dict[str, Any]] = None) -> Status:
    """
    Determine research quality status based on confidence interval and additional criteria.
    
    Args:
        value: Metric value
        ci95: 95% confidence interval (lower, upper)
        extras: Additional information (p-values, sample sizes, etc.)
        
    Returns:
        Status indicating research quality level
        
    Status Logic:
        - validated: CI half-width ≤ STATUS_BAND_WIDTH * value AND strong evidence
        - experimental: computed but CI wide or limited evidence  
        - unstable: CI half-width > 0.5 * value or very small N
        - insufficient_*: missing required inputs
    """
    if extras is None:
        extras = {}
    
    # Check for insufficient data markers
    if "insufficient_runs" in extras or "insufficient_data" in extras:
        return "insufficient_runs" if "insufficient_runs" in extras else "insufficient_data"
    
    # Calculate CI metrics
    ci_lower, ci_upper = ci95
    ci_half_width = (ci_upper - ci_lower) / 2
    
    # Handle zero or near-zero values
    if abs(value) < 1e-10:
        # For zero values, use absolute CI width
        if ci_half_width < 0.01:
            return "validated"
        elif ci_half_width < 0.05:
            return "experimental"
        else:
            return "unstable"
    
    # Relative CI width for non-zero values
    relative_ci_width = ci_half_width / abs(value)
    
    # Check for unstable (very wide CI)
    if relative_ci_width > 0.5:
        return "unstable"
    
    # Check sample size if available
    n_samples = extras.get("n_samples", float('inf'))
    if n_samples < 50:
        return "unstable"
    
    # Check statistical significance if available
    p_value = extras.get("p_null", extras.get("p_value", 1.0))
    
    # Validated: narrow CI and (if tested) significant
    if relative_ci_width <= STATUS_BAND_WIDTH:
        if p_value < 0.05 or "p_null" not in extras:
            return "validated"
        else:
            return "experimental"
    
    # Experimental: moderate CI or borderline significance
    elif relative_ci_width <= 0.4:
        return "experimental"
    
    # Default to unstable
    else:
        return "unstable"

def get_registered_metrics() -> List[str]:
    """Get list of all registered metric names."""
    return list(_METRIC_REGISTRY.keys())

def clear_registry():
    """Clear the metric registry (primarily for testing)."""
    global _METRIC_REGISTRY
    _METRIC_REGISTRY.clear()
    logger.debug("Cleared metric registry")

# Auto-register existing metrics on import
def _auto_register_metrics():
    """Auto-register existing metrics with canonical names."""
    try:
        # Import existing metric functions
        from .asymmetry_index import compute_asymmetry_index
        from .pathway_concentration_ratio import compute_pathway_concentration_ratio  
        from .entanglement_error_correlation import compute_entanglement_error_correlation
        from .temporal_pathway_stability import compute_temporal_pathway_stability
        from .complexity_emergence_score import compute_complexity_emergence_score
        from .total_correlation import compute_total_correlation
        
        # Create wrapper functions that handle **kwargs and return MetricResult format
        def _wrap_asymmetry_index(**kwargs):
            counts = kwargs.get('counts', {})
            result = compute_asymmetry_index(counts)
            return {
                "value": result,
                "status": "experimental",
                "ci95": (result * 0.9, result * 1.1),  # Placeholder CI
                "extras": {"method": "asymmetry_index"}
            }
        
        def _wrap_concentration_ratio(**kwargs):
            counts = kwargs.get('counts', {})
            result = compute_pathway_concentration_ratio(counts)
            return {
                "value": result,
                "status": "experimental", 
                "ci95": (result * 0.9, result * 1.1),  # Placeholder CI
                "extras": {"method": "pathway_concentration_ratio"}
            }
        
        def _wrap_entanglement_correlation(**kwargs):
            counts = kwargs.get('counts', {})
            state_type = kwargs.get('state_type', 'GHZ')
            result = compute_entanglement_error_correlation(counts, state_type)
            return {
                "value": result,
                "status": "experimental",
                "ci95": (max(-1, result - 0.1), min(1, result + 0.1)),  # Placeholder CI
                "extras": {"method": "entanglement_error_correlation", "state_type": state_type}
            }
        
        def _wrap_temporal_stability(**kwargs):
            # temporal_pathway_stability expects rankings, not counts
            # For now, return placeholder until we fix this properly
            return {
                "value": 0.5,
                "status": "insufficient_data",
                "ci95": (0.4, 0.6),
                "extras": {"method": "temporal_pathway_stability", "reason": "requires rankings not counts"}
            }
        
        def _wrap_complexity_emergence(**kwargs):
            # complexity_emergence_score expects multi-qubit data
            # For now, return placeholder until we fix this properly  
            return {
                "value": 0.0,
                "status": "insufficient_data",
                "ci95": (0.0, 0.1),
                "extras": {"method": "complexity_emergence_score", "reason": "requires multi-qubit series data"}
            }
        
        # Register with canonical schema names (using wrappers)
        _METRIC_REGISTRY["structure_score"] = _wrap_asymmetry_index  # Map AI to SS
        _METRIC_REGISTRY["entanglement_error_correlation"] = _wrap_entanglement_correlation
        _METRIC_REGISTRY["concentration_index"] = _wrap_concentration_ratio  # Map PCR to CI
        _METRIC_REGISTRY["pathway_persistence"] = _wrap_temporal_stability  # Map TPS to PP
        _METRIC_REGISTRY["complexity_emergence_score"] = _wrap_complexity_emergence
        # total_correlation already registered properly
        
        # Also register original names for backward compatibility
        _METRIC_REGISTRY["asymmetry_index"] = _wrap_asymmetry_index
        _METRIC_REGISTRY["pathway_concentration_ratio"] = _wrap_concentration_ratio
        _METRIC_REGISTRY["temporal_pathway_stability"] = _wrap_temporal_stability
        
        logger.debug(f"Auto-registered {len(_METRIC_REGISTRY)} metrics with wrappers")
        
    except ImportError as e:
        logger.warning(f"Could not auto-register some metrics: {e}")

# Auto-register on module import
_auto_register_metrics()