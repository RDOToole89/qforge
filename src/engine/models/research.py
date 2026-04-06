"""Research Models — Generic Metrics Bundle.

Purpose: Define metric-agnostic models for the engine's analysis layer.
A MetricsBundle holds an arbitrary set of MetricEntry values keyed by name,
replacing the former SST-specific StructuredDecoherenceMetrics.

Dependencies: Pydantic only
Used by: Engine analysis pipeline, research result storage
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class MetricEntry(BaseModel):
    """A single computed metric with optional confidence interval."""

    model_config = ConfigDict(extra="forbid")

    value: float
    ci95: tuple[float, float] | None = None
    status: str = "experimental"
    extras: dict[str, Any] = Field(default_factory=dict)


class MetricsBundle(BaseModel):
    """Collection of named metrics produced by a single analysis run."""

    model_config = ConfigDict(extra="forbid")

    metrics: dict[str, MetricEntry] = Field(default_factory=dict)
    profile: str | None = Field(
        default=None,
        description="Profile name used to select these metrics, if any",
    )
    metadata: AnalysisMetadata

    def get(self, name: str) -> MetricEntry | None:
        """Look up a metric by name, returning None if absent."""
        return self.metrics.get(name)

    def value(self, name: str) -> float:
        """Return the scalar value for a metric; raises KeyError if absent."""
        entry = self.metrics.get(name)
        if entry is None:
            raise KeyError(f"Metric '{name}' not in bundle. Have: {list(self.metrics)}")
        return entry.value

    @property
    def metric_names(self) -> list[str]:
        """Sorted list of metric names in this bundle."""
        return sorted(self.metrics.keys())


class AnalysisMetadata(BaseModel):
    """Metadata about the analysis run."""

    state_type: str = Field(description="Quantum state type (GHZ, W, BELL, etc.)")
    num_qubits: int = Field(ge=1, description="Number of qubits in the system")
    total_shots: int = Field(ge=1, description="Total measurement shots used")
    unique_outcomes: int = Field(ge=1, description="Number of unique measurement outcomes")

    analysis_timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="When the analysis was performed",
    )

    noise_conditions: dict[str, Any] | None = Field(
        default=None, description="Noise model parameters used"
    )

    computation_time_ms: float | None = Field(
        default=None,
        ge=0.0,
        description="Time taken to compute metrics in milliseconds",
    )


class ResearchMetadata(BaseModel):
    """Metadata for research experiments and campaigns.

    Purpose: Track research context, hypotheses, and experimental conditions.
    """

    hypothesis: str | None = Field(default=None, description="Research hypothesis being tested")

    research_phase: str | None = Field(
        default=None,
        description="Phase of research (threshold, characterization, validation, etc.)",
    )

    campaign_id: str | None = Field(
        default=None,
        description="Research campaign identifier for grouping related experiments",
    )

    expected_outcomes: list[str] | None = Field(
        default=None, description="Expected experimental outcomes or predictions"
    )

    control_experiment: bool = Field(
        default=False, description="Whether this is a control experiment"
    )

    publication_ready: bool = Field(
        default=False, description="Whether results meet publication quality standards"
    )

    figure_candidate: bool = Field(
        default=False,
        description="Whether results are suitable for publication figures",
    )


# Resolve forward references
MetricEntry.model_rebuild()
MetricsBundle.model_rebuild()
AnalysisMetadata.model_rebuild()
ResearchMetadata.model_rebuild()
