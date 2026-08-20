"""Measurement Results Model."""

from __future__ import annotations

import logging
import math
from typing import Any

from pydantic import BaseModel, Field, model_validator

logger = logging.getLogger(__name__)


class MeasurementResults(BaseModel):
    """Raw measurement data and basic statistics."""

    raw_counts: dict[str, int] = Field(
        description="Raw measurement counts as {bitstring: count} pairs"
    )

    total_shots: int = Field(ge=1, description="Total number of measurement shots")

    unique_outcomes: int = Field(ge=1, description="Number of unique measurement outcomes observed")

    outcome_probabilities: dict[str, float] = Field(
        description="Normalized probabilities for each outcome"
    )

    density_matrix: list[list[list[float]]] | None = Field(
        default=None,
        description=(
            "Density matrix from density_matrix simulation mode. "
            "Shape: NxN where each element is [real, imag] "
            "for JSON-safe complex numbers."
        ),
    )

    statevector: list[list[float]] | None = Field(
        default=None,
        description=(
            "State vector from statevector simulation mode. "
            "Each element is [real, imag] "
            "for JSON-safe complex numbers."
        ),
    )

    fidelity: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description=(
            "Fidelity with ideal state (auto-computed for statevector/density_matrix modes)"
        ),
    )

    @classmethod
    def from_counts(cls, counts: dict[str, int]) -> MeasurementResults:
        """Create from raw counts, computing totals and probabilities.

        Args:
            counts: Mapping of bitstring outcomes to their counts.

        Returns:
            A new MeasurementResults instance.
        """
        total = int(sum(counts.values())) if counts else 0
        if total <= 0:
            raise ValueError(
                "from_counts requires a non-empty counts dictionary with positive totals"
            )
        probs = {k: v / total for k, v in counts.items()}
        return cls(
            raw_counts=dict(counts),
            total_shots=total,
            unique_outcomes=len(counts),
            outcome_probabilities=probs,
        )

    @model_validator(mode="before")
    @classmethod
    def _precompute_probs(cls, data: Any) -> Any:
        """Compute outcome_probabilities from raw_counts if missing."""
        if not isinstance(data, dict):
            return data
        counts = data.get("raw_counts") or {}
        total = data.get("total_shots")
        probs = data.get("outcome_probabilities")
        if (not probs) and counts and total:
            try:
                total = int(total)
                if total > 0:
                    data["outcome_probabilities"] = {k: v / total for k, v in counts.items()}
            except Exception:
                pass
        return data

    @model_validator(mode="after")
    def _validate_and_heal(self) -> MeasurementResults:
        """Auto-heal and validate measurement results.

        - Ensure total_shots == sum(raw_counts); fix if not.
        - Ensure unique_outcomes == len(raw_counts); fix if not.
        - Recompute/normalize probabilities if mismatched.
        """
        sum_counts = int(sum(int(v) for v in self.raw_counts.values())) if self.raw_counts else 0
        if sum_counts <= 0:
            raise ValueError("MeasurementResults.raw_counts must be non-empty with positive totals")

        if self.total_shots != sum_counts:
            logger.warning(
                f"[MeasurementResults] total_shots="
                f"{self.total_shots} != sum(raw_counts)="
                f"{sum_counts}; setting total_shots={sum_counts}"
            )
            self.total_shots = sum_counts

        expected_unique = len(self.raw_counts)
        if self.unique_outcomes != expected_unique:
            logger.warning(
                f"[MeasurementResults] unique_outcomes="
                f"{self.unique_outcomes} != "
                f"len(raw_counts)={expected_unique}; "
                f"setting unique_outcomes={expected_unique}"
            )
            self.unique_outcomes = expected_unique

        if (not self.outcome_probabilities) or (
            set(self.outcome_probabilities.keys()) != set(self.raw_counts.keys())
        ):
            self.outcome_probabilities = {
                k: v / self.total_shots for k, v in self.raw_counts.items()
            }
        else:
            total_p = float(sum(self.outcome_probabilities.values()))
            if not math.isfinite(total_p) or total_p <= 0.0:
                self.outcome_probabilities = {
                    k: v / self.total_shots for k, v in self.raw_counts.items()
                }
            elif abs(total_p - 1.0) > 1e-8:
                logger.warning(
                    "[MeasurementResults] outcome_probabilities "
                    f"sum={total_p:.6f} != 1.0; normalizing"
                )
                self.outcome_probabilities = {
                    k: p / total_p for k, p in self.outcome_probabilities.items()
                }

        for k, p in list(self.outcome_probabilities.items()):
            if p < 0.0 and p > -1e-12:
                self.outcome_probabilities[k] = 0.0
            elif p > 1.0 and p < 1.0 + 1e-12:
                self.outcome_probabilities[k] = 1.0

        return self
