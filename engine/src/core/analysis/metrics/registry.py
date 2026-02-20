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

import logging
from functools import wraps
from typing import Any, Callable, Literal, Optional, TypedDict

# NOTE: we import constants & bootstrap lazily inside wrappers to avoid circular imports
from ..constants import STATUS_BAND_WIDTH

logger = logging.getLogger(__name__)

# -----------------------
# Types & global registry
# -----------------------

Status = Literal["validated", "experimental", "unstable", "insufficient_runs", "insufficient_data"]


class MetricResult(TypedDict, total=False):
    """Standardized metric result with confidence intervals and status."""

    value: float
    ci95: tuple[float, float]
    status: Status
    extras: dict[str, Any]


_METRIC_REGISTRY: dict[str, Callable[..., MetricResult]] = {}

# -----------------------
# Core registry utilities
# -----------------------


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

    def decorator(func: Callable[..., MetricResult]) -> Callable[..., MetricResult]:
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
        # Defensive normalization for CI and value types
        if "ci95" in result:
            lo, hi = result["ci95"]
            result["ci95"] = (float(lo), float(hi))
        result["value"] = float(result.get("value", 0.0))
        logger.debug(
            "Metric %s: value=%s, status=%s",
            name,
            result.get("value", "N/A"),
            result.get("status", "unknown"),
        )
        return result
    except Exception as e:
        logger.error(f"Error computing metric {name}: {e}")
        return MetricResult(
            value=0.0,
            ci95=(0.0, 0.0),
            status="unstable",
            extras={"error": str(e)},
        )


def compute_all(metric_names: Optional[list[str]] = None, **kwargs) -> dict[str, MetricResult]:
    """
    Compute multiple metrics with shared parameters.

    Args:
        metric_names: List of metric names to compute (None = all available)
        **kwargs: Shared arguments passed to all metric functions

    Returns:
        Dictionary mapping metric names to MetricResult objects

    Conditional Metrics (inputs expected):
        - pathway_persistence (TPS): 'rankings' or 'pathway_rankings'
        - complexity_emergence_score (CES): 'multi_qubit_data'

    Example:
        >>> counts = {"000": 400, "111": 400, "001": 100, "110": 100}
        >>> results = compute_all(counts=counts, rng=np.random.default_rng(123))
        >>> for name, result in results.items():
        ...     print(f"{name}: {result['value']:.3f} ({result['status']})")
    """
    if metric_names is None:
        metric_names = list(_METRIC_REGISTRY.keys())

    results: dict[str, MetricResult] = {}

    # Preflight presence checks for conditional metrics
    has_rankings = ("rankings" in kwargs and kwargs["rankings"]) or (
        "pathway_rankings" in kwargs and kwargs["pathway_rankings"]
    )
    has_ces_series = "multi_qubit_data" in kwargs and kwargs["multi_qubit_data"]

    for name in metric_names:
        if name not in _METRIC_REGISTRY:
            logger.warning(f"Skipping unknown metric: {name}")
            continue

        # Enforce sensible defaults for conditional inputs
        if name == "pathway_persistence" and not has_rankings:
            results[name] = MetricResult(
                value=0.0,
                ci95=(0.0, 0.0),
                status="insufficient_runs",
                extras={"reason": "Missing 'rankings' (or 'pathway_rankings') input"},
            )
            continue

        if name == "complexity_emergence_score" and not has_ces_series:
            results[name] = MetricResult(
                value=0.0,
                ci95=(0.0, 0.0),
                status="insufficient_data",
                extras={"reason": "Missing 'multi_qubit_data' series"},
            )
            continue

        # Compute
        try:
            results[name] = compute_metric(name, **kwargs)
        except Exception as e:
            logger.error(f"Failed to compute {name}: {e}")
            results[name] = MetricResult(
                value=0.0,
                ci95=(0.0, 0.0),
                status="unstable",
                extras={"error": str(e)},
            )

    logger.info(f"Computed {len(results)} metrics")
    return results


# -----------------------
# Status logic
# -----------------------


def determine_status(
    value: float, ci95: tuple[float, float], extras: Optional[dict[str, Any]] = None
) -> Status:
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

    # Insufficient markers short-circuit
    if "insufficient_runs" in extras:
        return "insufficient_runs"
    if "insufficient_data" in extras:
        return "insufficient_data"

    lo, hi = ci95
    ci_half = max(0.0, (hi - lo) / 2.0)

    # Handle zero or near-zero mean values using absolute CI
    if abs(value) < 1e-10:
        if ci_half < 0.01:
            return "validated"
        elif ci_half < 0.05:
            return "experimental"
        else:
            return "unstable"

    rel = ci_half / abs(value)

    # Very wide CI → unstable
    if rel > 0.5:
        return "unstable"

    # Small-N → unstable if provided
    n_samples = extras.get("n_samples", float("inf"))
    if isinstance(n_samples, (int, float)) and n_samples < 50:
        return "unstable"

    # Consider statistical significance if available
    p_value = extras.get("p_null", extras.get("p_value", 1.0))

    # Narrow CI & significant → validated
    if rel <= STATUS_BAND_WIDTH:
        return "validated" if (p_value < 0.05 or "p_null" not in extras) else "experimental"

    # Moderate CI → experimental
    if rel <= 0.4:
        return "experimental"

    return "unstable"


# -----------------------
# Default registrations
# -----------------------


def _register_default_wrappers() -> None:
    """
    Lazily register canonical metrics (and aliases) with robust wrappers.
    Wrappers import their underlying implementations *inside the call* to
    avoid circular imports and to keep the registry lightweight.
    """

    # --- structure_score (proxy to Asymmetry Index unless a dedicated SS exists) ---
    @_register("structure_score")
    def _wrap_structure_score(**kwargs) -> MetricResult:
        counts = kwargs.get("counts", {}) or {}
        try:
            # Prefer dedicated structure_score if available
            try:
                from .structure_score import (
                    compute_structure_score as _ss,  # type: ignore
                )

                value = float(_ss(counts=counts).get("value", 0.0))
                ci95 = tuple(
                    _ss(counts=counts).get("ci95", (value, value))
                )  # if their module returns MetricResult
            except Exception:
                # Fallback to AI
                from ..constants import DEFAULT_BOOTSTRAP_B as _B  # type: ignore
                from ..core.bootstrap import (
                    bootstrap_confidence_interval as _bci,  # type: ignore
                )
                from .asymmetry_index import (
                    compute_asymmetry_index as _ai,  # type: ignore
                )

                def _stat(c: dict[str, int]) -> float:
                    return float(_ai(c))

                value = _stat(counts)
                lo, hi = _bci(
                    counts,
                    _stat,
                    n_bootstrap=kwargs.get("B", _B),
                    rng=kwargs.get("rng"),
                )
                ci95 = (float(lo), float(hi))

            extras = {
                "method": "structure_score",
                "proxy": ("asymmetry_index" if "compute_asymmetry_index" in locals() else "native"),
                "n_samples": sum(counts.values()) if counts else 0,
                "n_outcomes": len(counts),
            }
            status = determine_status(value, ci95, extras)
            return MetricResult(value=value, ci95=ci95, status=status, extras=extras)
        except Exception as e:
            logger.error("structure_score failed: %s", e)
            return MetricResult(
                value=0.0, ci95=(0.0, 0.0), status="unstable", extras={"error": str(e)}
            )

    # --- entanglement_error_correlation ---
    @_register("entanglement_error_correlation")
    def _wrap_eec(**kwargs) -> MetricResult:
        counts = kwargs.get("counts", {}) or {}
        state_type = kwargs.get("state_type", "GHZ")
        try:
            from ..constants import DEFAULT_BOOTSTRAP_B as _B  # type: ignore
            from ..core.bootstrap import (
                bootstrap_confidence_interval as _bci,  # type: ignore
            )
            from .entanglement_error_correlation import (
                compute_entanglement_error_correlation as _eec,  # type: ignore
            )

            def _stat(c: dict[str, int]) -> float:
                v = float(_eec(c, state_type=state_type))
                # Defensive clip in case of numerical edge cases
                return float(max(-1.0, min(1.0, v)))

            value = _stat(counts)
            lo, hi = _bci(counts, _stat, n_bootstrap=kwargs.get("B", _B), rng=kwargs.get("rng"))
            ci95 = (float(lo), float(hi))

            extras = {
                "method": "entanglement_error_correlation",
                "state_type": state_type,
                "n_samples": sum(counts.values()) if counts else 0,
                "n_outcomes": len(counts),
            }
            status = determine_status(value, ci95, extras)
            return MetricResult(value=value, ci95=ci95, status=status, extras=extras)
        except Exception as e:
            logger.error("EEC failed: %s", e)
            return MetricResult(
                value=0.0, ci95=(0.0, 0.0), status="unstable", extras={"error": str(e)}
            )

    # --- concentration_index (PCR) ---
    @_register("concentration_index")
    def _wrap_concentration(**kwargs) -> MetricResult:
        counts = kwargs.get("counts", {}) or {}
        try:
            from ..constants import DEFAULT_BOOTSTRAP_B as _B  # type: ignore
            from ..core.bootstrap import (
                bootstrap_confidence_interval as _bci,  # type: ignore
            )
            from .pathway_concentration_ratio import (
                compute_pathway_concentration_ratio as _pcr,  # type: ignore
            )

            def _stat(c: dict[str, int]) -> float:
                return float(_pcr(c))

            value = _stat(counts)
            lo, hi = _bci(counts, _stat, n_bootstrap=kwargs.get("B", _B), rng=kwargs.get("rng"))
            ci95 = (float(lo), float(hi))

            extras = {
                "method": "pathway_concentration_ratio",
                "n_samples": sum(counts.values()) if counts else 0,
                "n_outcomes": len(counts),
            }
            status = determine_status(value, ci95, extras)
            return MetricResult(value=value, ci95=ci95, status=status, extras=extras)
        except Exception as e:
            logger.error("concentration_index failed: %s", e)
            return MetricResult(
                value=0.0, ci95=(0.0, 0.0), status="unstable", extras={"error": str(e)}
            )

    # --- pathway_persistence (TPS) ---
    @_register("pathway_persistence")
    def _wrap_tps(**kwargs) -> MetricResult:
        # Accept either 'rankings' or 'pathway_rankings'
        rankings = kwargs.get("rankings") or kwargs.get("pathway_rankings")
        if not rankings:
            return MetricResult(
                value=0.0,
                ci95=(0.0, 0.0),
                status="insufficient_runs",
                extras={"reason": "Missing 'rankings' (or 'pathway_rankings') input"},
            )
        try:
            from .temporal_pathway_stability import (
                compute_temporal_pathway_stability as _tps,  # type: ignore
            )

            value = float(_tps(rankings, return_analysis=False))
            # TPS is a derived stability ratio; provide a conservative CI band if not bootstrapping
            # (bootstrapping would require resampling full runs; we keep it deterministic here)
            ci95 = (max(0.0, value - 0.1), min(1.0, value + 0.1))

            extras = {"method": "temporal_pathway_stability", "n_runs": len(rankings)}
            status = determine_status(value, ci95, extras)
            return MetricResult(value=value, ci95=ci95, status=status, extras=extras)
        except Exception as e:
            logger.error("pathway_persistence failed: %s", e)
            return MetricResult(
                value=0.0, ci95=(0.0, 0.0), status="unstable", extras={"error": str(e)}
            )

    # --- complexity_emergence_score (CES) ---
    @_register("complexity_emergence_score")
    def _wrap_ces(**kwargs) -> MetricResult:
        multi_qubit_data = kwargs.get("multi_qubit_data")
        if not multi_qubit_data:
            return MetricResult(
                value=0.0,
                ci95=(0.0, 0.0),
                status="insufficient_data",
                extras={"reason": "Missing 'multi_qubit_data' series"},
            )
        try:
            from .complexity_emergence_score import (
                compute_complexity_emergence_score as _ces,  # type: ignore
            )

            # Return analysis if available to expose extras; else just value
            analysis_or_value = _ces(multi_qubit_data, return_analysis=True)
            if hasattr(analysis_or_value, "to_dict"):
                d = analysis_or_value.to_dict()  # dataclass → dict
                value = float(d.get("complexity_emergence_score", 0.0))
                # Conservative CI for model-fit quantities unless bootstrapped externally
                ci95 = (max(0.0, value - 0.2), value + 0.2)
                extras = {
                    "method": "complexity_emergence_score",
                    "emergence_quality": d.get("emergence_quality"),
                    "fit_r_squared": d.get("fit_r_squared"),
                    "critical_threshold": d.get("critical_threshold"),
                    "n_system_sizes": len(multi_qubit_data),
                }
            else:
                value = float(analysis_or_value)
                ci95 = (max(0.0, value - 0.2), value + 0.2)
                extras = {
                    "method": "complexity_emergence_score",
                    "n_system_sizes": len(multi_qubit_data),
                }

            status = determine_status(value, ci95, extras)
            return MetricResult(value=value, ci95=ci95, status=status, extras=extras)
        except Exception as e:
            logger.error("complexity_emergence_score failed: %s", e)
            return MetricResult(
                value=0.0, ci95=(0.0, 0.0), status="unstable", extras={"error": str(e)}
            )

    # --- Aliases for backward compatibility ---
    _METRIC_REGISTRY["asymmetry_index"] = _METRIC_REGISTRY["structure_score"]
    _METRIC_REGISTRY["pathway_concentration_ratio"] = _METRIC_REGISTRY["concentration_index"]
    _METRIC_REGISTRY["temporal_pathway_stability"] = _METRIC_REGISTRY["pathway_persistence"]

    logger.debug("Default wrappers registered (canonical + aliases)")


def _register(
    name: str,
) -> Callable[[Callable[..., MetricResult]], Callable[..., MetricResult]]:
    """
    Internal helper: behaves like @register but used locally so we can define
    multiple wrappers in _register_default_wrappers() without re-import noise.
    """

    def deco(func: Callable[..., MetricResult]) -> Callable[..., MetricResult]:
        _METRIC_REGISTRY[name] = func
        return func

    return deco


# Register defaults on import
_register_default_wrappers()

# NOTE:
# The dedicated "total_correlation" metric is expected to register itself
# via @register("total_correlation") in its own module to avoid circular imports.
# If that module hasn’t been imported yet, users can `import ...total_correlation`
# once, or simply call compute_metric("total_correlation", ...) after importing it.
