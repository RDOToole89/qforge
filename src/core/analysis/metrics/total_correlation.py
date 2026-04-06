"""Total Correlation - Multi-Information Analysis.

This module provides the canonical implementation of Total Correlation (TC)
for the v1.0 schema compliance, wrapping the core information theory
implementation with the registry system.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

import numpy as np

from ..constants import ALPHA, DEFAULT_BOOTSTRAP_B
from ..core.bootstrap import bootstrap_confidence_interval
from ..core.information_theory import total_correlation as core_total_correlation
from .registry import MetricResult, determine_status, register

logger = logging.getLogger(__name__)


@register("total_correlation")
def compute_total_correlation(
    *,
    counts: Mapping[str, int],
    alpha: float = ALPHA,
    B: int = DEFAULT_BOOTSTRAP_B,
    rng: Any | None = None,
    **kwargs: Any,
) -> MetricResult:
    """Compute Total Correlation with bootstrap confidence intervals.

    Total Correlation measures the total amount of correlation among all variables:
    TC = Σᵢ H(Xᵢ) - H(X₁, X₂, ..., Xₙ)

    Args:
        counts: Measurement counts {bitstring: count}
        alpha: Jeffreys prior parameter
        B: Bootstrap samples for confidence interval
        rng: Random number generator or integer seed
        **kwargs: Additional arguments (ignored)

    Returns:
        MetricResult with value, ci95, status, and extras
    """
    # Fast guard for empty input
    if not counts:
        return MetricResult(
            value=0.0,
            ci95=(0.0, 0.0),
            status="insufficient_data",
            extras={"reason": "Empty counts dictionary"},
        )

    # Normalize RNG input (support passing a seed or a Generator)
    if rng is None:
        rng = np.random.default_rng()
    elif isinstance(rng, (int, np.integer)):
        rng = np.random.default_rng(int(rng))
    # else assume it's already a Generator-compatible object

    try:
        # Compute primary value
        tc_value = float(core_total_correlation(counts, alpha=alpha))

        # Bootstrap confidence interval
        def tc_bootstrap_fn(bootstrap_counts: Mapping[str, int]) -> float:
            return float(core_total_correlation(bootstrap_counts, alpha=alpha))

        ci_lower, ci_upper = bootstrap_confidence_interval(
            counts,
            tc_bootstrap_fn,
            n_bootstrap=B,
            rng=rng,  # ensure reproducibility if rng provided
        )

        # Determine status & extras
        try:
            n_qubits = len(next(iter(counts.keys())))
        except StopIteration:
            n_qubits = 0

        extras = {
            "n_samples": int(sum(counts.values())),
            "n_qubits": int(n_qubits),
            "n_outcomes": int(len(counts)),
            "method": "total_correlation",
            "B": int(B),
            "ci_method": "percentile",
        }

        status = determine_status(tc_value, (float(ci_lower), float(ci_upper)), extras)

        logger.debug(
            "Total Correlation = %.6f [%.6f, %.6f] (status=%s)",
            tc_value,
            ci_lower,
            ci_upper,
            status,
        )

        return MetricResult(
            value=tc_value,
            ci95=(float(ci_lower), float(ci_upper)),
            status=status,
            extras=extras,
        )

    except Exception as e:
        logger.error("Error computing total correlation: %s", e)
        return MetricResult(
            value=0.0,
            ci95=(0.0, 0.0),
            status="unstable",
            extras={"error": str(e)},
        )


__all__ = ["compute_total_correlation"]
