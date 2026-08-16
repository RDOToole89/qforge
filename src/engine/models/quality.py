"""Quality Metrics Model."""

from __future__ import annotations

import math

from pydantic import BaseModel, Field

from .measurement import MeasurementResults


class QualityMetrics(BaseModel):
    """Quality assessment of experiment results."""

    shot_adequacy: float = Field(
        ge=0.0,
        le=1.0,
        description="Adequacy of shot count for statistical significance",
    )

    outcome_coverage: float = Field(
        ge=0.0,
        le=1.0,
        description="Fraction of possible outcomes observed",
    )

    confidence_level: float = Field(
        ge=0.0,
        le=1.0,
        description="Statistical confidence in results",
    )

    convergence_achieved: bool = Field(description="Whether statistical convergence was achieved")

    @classmethod
    def from_measurements(
        cls,
        meas: MeasurementResults,
        num_qubits: int | None = None,
        *,
        target_ci_half_width: float = 0.02,
        z_value: float = 1.96,
        convergence_threshold: float = 0.95,
        coverage_weight: float = 0.5,
    ) -> QualityMetrics:
        """Compute quality metrics from measurement results.

        Args:
            meas: MeasurementResults instance.
            num_qubits: Number of qubits (inferred from counts if None).
            target_ci_half_width: Target half-width for per-outcome CI.
            z_value: Z-score for CI (1.96 ~ 95%).
            convergence_threshold: Adequacy threshold to mark convergence.
            coverage_weight: Contribution of coverage to confidence_level.

        Returns:
            QualityMetrics with computed quality indicators.
        """
        inferred_n = num_qubits
        if inferred_n is None:
            try:
                inferred_n = max(len(k.replace(" ", "")) for k in meas.raw_counts.keys())
            except Exception:
                inferred_n = max(
                    1,
                    int(math.ceil(math.log2(max(1, meas.unique_outcomes)))),
                )

        possible_outcomes = max(1, 2**inferred_n)
        coverage = min(1.0, meas.unique_outcomes / possible_outcomes)

        required = _estimate_required_shots_for_precision(
            unique_outcomes=meas.unique_outcomes,
            target_ci_half_width=target_ci_half_width,
            z_value=z_value,
        )
        adequacy = 1.0 if required <= 0 else min(1.0, meas.total_shots / required)

        coverage_weight = min(max(coverage_weight, 0.0), 1.0)
        confidence = min(
            1.0,
            max(
                0.0,
                coverage_weight * coverage + (1.0 - coverage_weight) * adequacy,
            ),
        )

        converged = adequacy >= convergence_threshold

        return cls(
            shot_adequacy=adequacy,
            outcome_coverage=coverage,
            confidence_level=confidence,
            convergence_achieved=converged,
        )


def _estimate_required_shots_for_precision(
    *,
    unique_outcomes: int,
    target_ci_half_width: float = 0.02,
    z_value: float = 1.96,
) -> int:
    """Estimate required shots for a desired per-outcome CI half-width.

    Uses the per-outcome binomial approximation under a multinomial model.
    Assumes p ~ 1/unique_outcomes (conservative for structured data).

    Args:
        unique_outcomes: Number of observed outcomes (support size).
        target_ci_half_width: Desired half-width (e.g., 0.02 for +/-2%).
        z_value: Z-score (1.96 ~ 95% CI).

    Returns:
        Estimated number of required shots.
    """
    m = max(1, int(unique_outcomes))
    p = 1.0 / m
    var = p * (1.0 - p)
    w = max(1e-6, float(target_ci_half_width))
    required = (z_value**2) * var / (w**2)
    return int(math.ceil(required))


def compute_quality_metrics(
    meas: MeasurementResults,
    num_qubits: int | None = None,
    *,
    target_ci_half_width: float = 0.02,
    z_value: float = 1.96,
    convergence_threshold: float = 0.95,
    coverage_weight: float = 0.5,
) -> QualityMetrics:
    """Compute QualityMetrics from MeasurementResults.

    Thin wrapper around QualityMetrics.from_measurements for callers
    that prefer a function over a classmethod.

    Args:
        meas: MeasurementResults instance.
        num_qubits: Number of qubits (inferred from counts if None).
        target_ci_half_width: Desired per-outcome half-width.
        z_value: Z-score for CI.
        convergence_threshold: Adequacy threshold to mark convergence.
        coverage_weight: Contribution of coverage to confidence_level.

    Returns:
        Computed QualityMetrics.
    """
    return QualityMetrics.from_measurements(
        meas,
        num_qubits,
        target_ci_half_width=target_ci_half_width,
        z_value=z_value,
        convergence_threshold=convergence_threshold,
        coverage_weight=coverage_weight,
    )
