"""Metrics Registry and Public API.

Centralized registry system for all structured decoherence metrics with
standardized API, type safety, and schema compliance.

This module provides:
- MetricResult TypedDict for consistent return types
- Registry decorator for metric registration
- compute_metric() and compute_all() for unified API
- Status determination logic for research quality assessment
- Declarative MetricSpec for adding new bootstrap-based metrics
"""

from __future__ import annotations

import importlib
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Literal, TypedDict

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
    """Decorator to register a metric function in the global registry.

    Args:
        name: Canonical metric name for registry and schema.

    Returns:
        Decorator function that registers the metric.
    """

    def decorator(func: Callable[..., MetricResult]) -> Callable[..., MetricResult]:
        _METRIC_REGISTRY[name] = func

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> MetricResult:
            return func(*args, **kwargs)

        logger.debug("Registered metric: %s", name)
        return wrapper

    return decorator


def compute_metric(name: str, **kwargs: Any) -> MetricResult:
    """Compute a single metric by name.

    Args:
        name: Registered metric name.
        **kwargs: Arguments passed to metric function.

    Returns:
        MetricResult with value, confidence interval, and status.

    Raises:
        KeyError: If metric name is not registered.
    """
    if name not in _METRIC_REGISTRY:
        available = list(_METRIC_REGISTRY.keys())
        raise KeyError(f"Unknown metric '{name}'. Available: {available}")

    metric_func = _METRIC_REGISTRY[name]
    logger.debug("Computing metric: %s", name)

    try:
        result = metric_func(**kwargs)
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
        logger.error("Error computing metric %s: %s", name, e)
        return MetricResult(
            value=0.0,
            ci95=(0.0, 0.0),
            status="unstable",
            extras={"error": str(e)},
        )


def compute_all(metric_names: list[str] | None = None, **kwargs: Any) -> dict[str, MetricResult]:
    """Compute multiple metrics with shared parameters.

    Args:
        metric_names: List of metric names to compute (None = all available).
        **kwargs: Shared arguments passed to all metric functions.

    Returns:
        Dictionary mapping metric names to MetricResult objects.
    """
    if metric_names is None:
        metric_names = list(_METRIC_REGISTRY.keys())

    results: dict[str, MetricResult] = {}

    has_rankings = ("rankings" in kwargs and kwargs["rankings"]) or (
        "pathway_rankings" in kwargs and kwargs["pathway_rankings"]
    )
    has_ces_series = "multi_qubit_data" in kwargs and kwargs["multi_qubit_data"]

    for name in metric_names:
        if name not in _METRIC_REGISTRY:
            logger.warning("Skipping unknown metric: %s", name)
            continue

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

        try:
            results[name] = compute_metric(name, **kwargs)
        except Exception as e:
            logger.error("Failed to compute %s: %s", name, e)
            results[name] = MetricResult(
                value=0.0,
                ci95=(0.0, 0.0),
                status="unstable",
                extras={"error": str(e)},
            )

    logger.info("Computed %d metrics", len(results))
    return results


# -----------------------
# Status logic
# -----------------------


def determine_status(
    value: float, ci95: tuple[float, float], extras: dict[str, Any] | None = None
) -> Status:
    """Determine research quality status based on CI and additional criteria.

    Args:
        value: Metric value.
        ci95: 95% confidence interval (lower, upper).
        extras: Additional information (p-values, sample sizes, etc.).

    Returns:
        Status indicating research quality level.
    """
    if extras is None:
        extras = {}

    if "insufficient_runs" in extras:
        return "insufficient_runs"
    if "insufficient_data" in extras:
        return "insufficient_data"

    lo, hi = ci95
    ci_half = max(0.0, (hi - lo) / 2.0)

    if abs(value) < 1e-10:
        if ci_half < 0.01:
            return "validated"
        elif ci_half < 0.05:
            return "experimental"
        else:
            return "unstable"

    rel = ci_half / abs(value)

    if rel > 0.5:
        return "unstable"

    n_samples = extras.get("n_samples", float("inf"))
    if isinstance(n_samples, (int, float)) and n_samples < 50:
        return "unstable"

    if rel <= STATUS_BAND_WIDTH:
        return "validated"

    if rel <= 0.4:
        return "experimental"

    return "unstable"


# -----------------------
# Declarative MetricSpec
# -----------------------


@dataclass
class MetricSpec:
    """Declarative specification for a bootstrap-based metric.

    Each spec defines how to lazily import and compute a metric,
    eliminating repetitive wrapper boilerplate.

    Attributes:
        name: Registry name for this metric.
        module: Relative module path (e.g. ".asymmetry_index").
        func_name: Function name in the module.
        method_label: Human-readable label for extras["method"].
        clip: Optional (min, max) to clip the computed value.
        extra_kwargs: Additional kwargs to forward from the caller.
    """

    name: str
    module: str
    func_name: str
    method_label: str
    clip: tuple[float, float] | None = None
    extra_kwargs: list[str] = field(default_factory=list)


def _make_bootstrap_wrapper(spec: MetricSpec) -> Callable[..., MetricResult]:
    """Create a standardized bootstrap wrapper from a MetricSpec.

    All bootstrap-based metrics follow the same pattern:
    1. Lazy-import the compute function
    2. Define a statistic closure (optionally clipped)
    3. Compute value + bootstrap CI
    4. Build extras dict
    5. Determine status

    Args:
        spec: Declarative metric specification.

    Returns:
        A wrapper function suitable for registry registration.
    """

    def wrapper(**kwargs: Any) -> MetricResult:
        counts = kwargs.get("counts", {}) or {}
        try:
            from ..constants import DEFAULT_BOOTSTRAP_B

            bci_mod = importlib.import_module("src.core.analysis.core.bootstrap", package=None)
            bci = bci_mod.bootstrap_confidence_interval

            metric_mod = importlib.import_module(
                f"src.core.analysis.metrics{spec.module}", package=None
            )
            compute_fn = getattr(metric_mod, spec.func_name)

            # Build extra kwargs to pass to the compute function
            extra_kw = {k: kwargs[k] for k in spec.extra_kwargs if k in kwargs}

            def _stat(c: dict[str, int]) -> float:
                val = float(compute_fn(c, **extra_kw))
                if spec.clip:
                    val = max(spec.clip[0], min(spec.clip[1], val))
                return val

            value = _stat(counts)
            lo, hi = bci(
                counts,
                _stat,
                n_bootstrap=kwargs.get("B", DEFAULT_BOOTSTRAP_B),
                rng=kwargs.get("rng"),
            )
            ci95 = (float(lo), float(hi))

            extras: dict[str, Any] = {
                "method": spec.method_label,
                "n_samples": sum(counts.values()) if counts else 0,
                "n_outcomes": len(counts),
            }
            status = determine_status(value, ci95, extras)
            return MetricResult(value=value, ci95=ci95, status=status, extras=extras)
        except Exception as e:
            logger.error("%s failed: %s", spec.name, e)
            return MetricResult(
                value=0.0, ci95=(0.0, 0.0), status="unstable", extras={"error": str(e)}
            )

    wrapper.__name__ = f"_wrap_{spec.name}"
    wrapper.__qualname__ = f"_wrap_{spec.name}"
    return wrapper


# -----------------------
# Metric specifications
# -----------------------

_BOOTSTRAP_SPECS: list[MetricSpec] = [
    MetricSpec(
        name="concentration_index",
        module=".pathway_concentration_ratio",
        func_name="compute_pathway_concentration_ratio",
        method_label="pathway_concentration_ratio",
    ),
]


# -----------------------
# Special-case wrappers
# -----------------------


def _wrap_structure_score(**kwargs: Any) -> MetricResult:
    """Structure score (JSD from factorized null) with bootstrap CI."""
    counts = kwargs.get("counts", {}) or {}
    try:
        from ..constants import DEFAULT_BOOTSTRAP_B

        bci_mod = importlib.import_module("src.core.analysis.core.bootstrap", package=None)
        bci = bci_mod.bootstrap_confidence_interval
        from .structure_score import compute_structure_score as _ss

        def _stat(c: dict[str, int]) -> float:
            return float(_ss(counts=c).get("value", 0.0))

        value = _stat(counts)
        lo, hi = bci(
            counts,
            _stat,
            n_bootstrap=kwargs.get("B", DEFAULT_BOOTSTRAP_B),
            rng=kwargs.get("rng"),
        )
        ci95 = (float(lo), float(hi))

        extras: dict[str, Any] = {
            "method": "jsd_factorized_null",
            "n_samples": sum(counts.values()) if counts else 0,
            "n_outcomes": len(counts),
        }
        status = determine_status(value, ci95, extras)
        return MetricResult(value=value, ci95=ci95, status=status, extras=extras)
    except Exception as e:
        logger.error("structure_score failed: %s", e)
        return MetricResult(value=0.0, ci95=(0.0, 0.0), status="unstable", extras={"error": str(e)})


def _wrap_asymmetry_index(**kwargs: Any) -> MetricResult:
    """Asymmetry index (TVD from uniform) with bootstrap CI."""
    counts = kwargs.get("counts", {}) or {}
    try:
        from ..constants import DEFAULT_BOOTSTRAP_B

        bci_mod = importlib.import_module("src.core.analysis.core.bootstrap", package=None)
        bci = bci_mod.bootstrap_confidence_interval
        from .asymmetry_index import compute_asymmetry_index

        def _stat(c: dict[str, int]) -> float:
            return float(compute_asymmetry_index(c))

        value = _stat(counts)
        lo, hi = bci(
            counts,
            _stat,
            n_bootstrap=kwargs.get("B", DEFAULT_BOOTSTRAP_B),
            rng=kwargs.get("rng"),
        )
        ci95 = (float(lo), float(hi))

        extras: dict[str, Any] = {
            "method": "total_variation_distance",
            "n_samples": sum(counts.values()) if counts else 0,
            "n_outcomes": len(counts),
        }
        status = determine_status(value, ci95, extras)
        return MetricResult(value=value, ci95=ci95, status=status, extras=extras)
    except Exception as e:
        logger.error("asymmetry_index failed: %s", e)
        return MetricResult(value=0.0, ci95=(0.0, 0.0), status="unstable", extras={"error": str(e)})


def _wrap_eec(**kwargs: Any) -> MetricResult:
    """Entanglement-error correlation with topology analysis matrices in extras."""
    counts = kwargs.get("counts", {}) or {}
    state_type = kwargs.get("state_type", "GHZ")
    try:
        from ..constants import DEFAULT_BOOTSTRAP_B

        bci_mod = importlib.import_module("src.core.analysis.core.bootstrap", package=None)
        bci = bci_mod.bootstrap_confidence_interval
        from .entanglement_error_correlation import compute_entanglement_error_correlation

        def _stat(c: dict[str, int]) -> float:
            v = float(compute_entanglement_error_correlation(c, state_type=state_type))
            return float(max(-1.0, min(1.0, v)))

        value = _stat(counts)
        lo, hi = bci(
            counts, _stat, n_bootstrap=kwargs.get("B", DEFAULT_BOOTSTRAP_B), rng=kwargs.get("rng")
        )
        ci95 = (float(lo), float(hi))

        extras: dict[str, Any] = {
            "method": "entanglement_error_correlation",
            "state_type": state_type,
            "n_samples": sum(counts.values()) if counts else 0,
            "n_outcomes": len(counts),
        }
        # Include topology analysis matrices for visualization
        try:
            analysis = compute_entanglement_error_correlation(
                counts, state_type=state_type, return_analysis=True
            )
            if hasattr(analysis, "entanglement_matrix"):
                extras["entanglement_matrix"] = analysis.entanglement_matrix.tolist()
                extras["error_correlation_matrix"] = analysis.error_correlation_matrix.tolist()
        except Exception:
            pass
        status = determine_status(value, ci95, extras)
        return MetricResult(value=value, ci95=ci95, status=status, extras=extras)
    except Exception as e:
        logger.error("EEC failed: %s", e)
        return MetricResult(value=0.0, ci95=(0.0, 0.0), status="unstable", extras={"error": str(e)})


def _wrap_pathway_persistence(**kwargs: Any) -> MetricResult:
    """Pathway persistence (TPS) from rankings; deterministic, no bootstrap."""
    rankings = kwargs.get("rankings") or kwargs.get("pathway_rankings")
    if not rankings:
        return MetricResult(
            value=0.0,
            ci95=(0.0, 0.0),
            status="insufficient_runs",
            extras={"reason": "Missing 'rankings' (or 'pathway_rankings') input"},
        )
    try:
        from .temporal_pathway_stability import compute_temporal_pathway_stability

        value = float(compute_temporal_pathway_stability(rankings, return_analysis=False))
        ci95 = (max(0.0, value - 0.1), min(1.0, value + 0.1))
        extras = {"method": "temporal_pathway_stability", "n_runs": len(rankings)}
        status = determine_status(value, ci95, extras)
        return MetricResult(value=value, ci95=ci95, status=status, extras=extras)
    except Exception as e:
        logger.error("pathway_persistence failed: %s", e)
        return MetricResult(value=0.0, ci95=(0.0, 0.0), status="unstable", extras={"error": str(e)})


def _wrap_complexity_emergence(**kwargs: Any) -> MetricResult:
    """Complexity emergence score (CES) from multi-qubit series data."""
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
            EmergenceAnalysis,
            compute_complexity_emergence_score,
        )

        analysis_or_value: float | EmergenceAnalysis = compute_complexity_emergence_score(
            multi_qubit_data, return_analysis=True
        )
        if hasattr(analysis_or_value, "to_dict"):
            d = analysis_or_value.to_dict()
            value = float(d.get("complexity_emergence_score", 0.0))
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
        return MetricResult(value=0.0, ci95=(0.0, 0.0), status="unstable", extras={"error": str(e)})


# -----------------------
# Registration
# -----------------------


def _register_all() -> None:
    """Register all metrics: declarative specs + special-case wrappers + aliases."""
    # Declarative bootstrap-based metrics
    for spec in _BOOTSTRAP_SPECS:
        _METRIC_REGISTRY[spec.name] = _make_bootstrap_wrapper(spec)

    # Special-case metrics with unique logic
    _METRIC_REGISTRY["structure_score"] = _wrap_structure_score
    _METRIC_REGISTRY["asymmetry_index"] = _wrap_asymmetry_index
    _METRIC_REGISTRY["entanglement_error_correlation"] = _wrap_eec
    _METRIC_REGISTRY["pathway_persistence"] = _wrap_pathway_persistence
    _METRIC_REGISTRY["complexity_emergence_score"] = _wrap_complexity_emergence

    # Aliases for backward compatibility
    _METRIC_REGISTRY["pathway_concentration_ratio"] = _METRIC_REGISTRY["concentration_index"]
    _METRIC_REGISTRY["temporal_pathway_stability"] = _METRIC_REGISTRY["pathway_persistence"]

    logger.debug("All metrics registered (canonical + aliases)")


# Register on import
_register_all()
