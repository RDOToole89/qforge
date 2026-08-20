"""Metric Profiles.

Named collections of metrics for common use cases.
Profiles are resolved by name to a list of metric keys from the registry.
"""

from __future__ import annotations

METRIC_PROFILES: dict[str, list[str]] = {
    "decoherence": [
        "structure_score",
        "entanglement_error_correlation",
        "concentration_index",
        "pathway_persistence",
        "complexity_emergence_score",
        "total_correlation",
    ],
    "quick": [
        "structure_score",
        "concentration_index",
    ],
    "information_theory": [
        "structure_score",
        "concentration_index",
        "total_correlation",
    ],
}


def resolve_metrics(metrics: list[str] | str | None) -> list[str] | None:
    """Resolve a metrics specifier to a concrete list of metric names.

    Args:
        metrics: One of:
            - None → no metrics (returns None)
            - str  → profile name lookup
            - list[str] → passthrough

    Returns:
        List of metric names, or None if metrics is None.

    Raises:
        KeyError: If a profile name is not found.
    """
    if metrics is None:
        return None
    if isinstance(metrics, str):
        if metrics not in METRIC_PROFILES:
            available = list(METRIC_PROFILES.keys())
            raise KeyError(f"Unknown metric profile '{metrics}'. Available: {available}")
        return list(METRIC_PROFILES[metrics])
    return list(metrics)
