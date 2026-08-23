"""Metric profiles — named lists of registered metric keys.

Core ships topic-free profiles. Research tracks (and user code) add more
with ``register_profile``; they do not belong in this module's identity.
"""

from __future__ import annotations

METRIC_PROFILES: dict[str, list[str]] = {}

_STRUCTURE_METRICS = [
    "structure_score",
    "entanglement_error_correlation",
    "concentration_index",
    "pathway_persistence",
    "complexity_emergence_score",
    "total_correlation",
]


def register_profile(
    name: str,
    metrics: list[str],
    *,
    replace: bool = False,
) -> None:
    """Register a named metric profile.

    Call this from an experiment package or user module. The engine resolves
    ``metrics="my_profile"`` against this live table.

    Args:
        name: Profile name (used as ``ExperimentConfig.metrics``).
        metrics: Ordered metric registry keys.
        replace: If True, overwrite an existing profile of the same name.

    Raises:
        ValueError: If ``metrics`` is empty.
        KeyError: If ``name`` is already registered and ``replace`` is False.
    """
    if not metrics:
        raise ValueError("A metric profile must list at least one metric")
    if name in METRIC_PROFILES and not replace:
        raise KeyError(
            f"Metric profile '{name}' is already registered. Pass replace=True to overwrite."
        )
    METRIC_PROFILES[name] = list(metrics)


def unregister_profile(name: str) -> None:
    """Remove a profile. Intended for tests."""
    METRIC_PROFILES.pop(name, None)


def list_profiles() -> dict[str, list[str]]:
    """Return a copy of all registered profiles."""
    return {key: list(values) for key, values in METRIC_PROFILES.items()}


def resolve_metrics(metrics: list[str] | str | None) -> list[str] | None:
    """Resolve a metrics specifier to a concrete list of metric names.

    Args:
        metrics: One of:
            - None → no metrics (returns None)
            - str  → profile name lookup
            - list[str] → passthrough (user-selected metric names)

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


register_profile("structure", _STRUCTURE_METRICS)
register_profile("quick", ["structure_score", "concentration_index"])
register_profile(
    "information_theory",
    ["structure_score", "concentration_index", "total_correlation"],
)
