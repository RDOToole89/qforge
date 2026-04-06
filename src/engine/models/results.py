"""Experiment Result Models.

Purpose: Define the top-level structure for quantum experiment results.
These models compose the focused submodules (metadata, circuit, measurement,
provenance, quality) into the complete experiment result.

Dependencies: Pydantic, research models, submodule models
Used by: Engine API, storage systems, analysis pipelines
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .circuit import CircuitStatistics
from .measurement import MeasurementResults
from .metadata import ExperimentMetadata
from .provenance import Provenance
from .quality import QualityMetrics, compute_quality_metrics
from .research import MetricsBundle, ResearchMetadata
from .storage import ArtifactRef

# Re-export submodule models for backward compatibility
__all__ = [
    "ExperimentResult",
    "ExperimentAnalysis",
    "ExperimentMetadata",
    "CircuitStatistics",
    "MeasurementResults",
    "QualityMetrics",
    "Provenance",
    "ExperimentStatus",
    "compute_quality_metrics",
]


class ExperimentResult(BaseModel):
    """Complete quantum experiment result.

    This model captures everything needed to understand, reproduce,
    and build upon a quantum experiment result.
    """

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
    )

    analysis: ExperimentAnalysis = Field(
        description="Complete experimental analysis including raw data and metrics"
    )

    metrics_bundle: MetricsBundle | None = Field(
        default=None,
        description="Computed analysis metrics (profile-based or explicit selection)",
    )

    research_metadata: ResearchMetadata | None = Field(
        default=None,
        description="Research context and experimental metadata",
    )

    provenance: Provenance = Field(
        description="Complete provenance information for reproducibility"
    )

    artifacts: list[ArtifactRef] = Field(
        default_factory=list,
        description="References to generated files (plots, reports, etc.)",
    )

    config_hash: str = Field(description="Hash of experiment configuration for deduplication")

    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="When the experiment was completed",
    )

    status: ExperimentStatus = Field(default="completed", description="Experiment execution status")

    quality_metrics: QualityMetrics | None = Field(
        default=None,
        description="Quality assessment of experiment results",
    )

    @property
    def has_metrics(self) -> bool:
        """Check if this experiment has computed metrics."""
        return self.metrics_bundle is not None

    @property
    def total_shots(self) -> int:
        """Get total measurement shots from analysis."""
        return self.analysis.measurement_results.total_shots


class ExperimentAnalysis(BaseModel):
    """Core experimental analysis data.

    Captures the essential analysis outputs from quantum experiments,
    separated from metadata for clean data access.
    """

    experiment_metadata: ExperimentMetadata = Field(
        description="Basic experiment identification and context"
    )

    experiment_parameters: dict[str, Any] = Field(
        description="Complete experiment configuration parameters"
    )

    circuit_statistics: CircuitStatistics = Field(
        description="Quantum circuit characteristics and statistics"
    )

    measurement_results: MeasurementResults = Field(
        description="Raw measurement data and basic statistics"
    )

    information_theory_metrics: dict[str, Any] | None = Field(
        default=None,
        description="Information-theoretic analysis (entropy, mutual information, etc.)",
    )

    correlation_analysis: dict[str, Any] | None = Field(
        default=None,
        description="Quantum correlation and entanglement analysis",
    )

    statistical_validation: dict[str, Any] | None = Field(
        default=None,
        description="Statistical validation and confidence measures",
    )


# Status enumeration
ExperimentStatus = Literal[
    "pending",
    "running",
    "completed",
    "failed",
    "cancelled",
    "timeout",
]

# Forward-ref resolution for Pydantic v2
ExperimentResult.model_rebuild()
ExperimentAnalysis.model_rebuild()
