"""
Research Models - Structured Decoherence Analysis

Purpose: Define models for structured decoherence pathway research.
These models capture the 5 quantitative metrics that characterize
whether quantum decoherence follows structured vs random patterns.

Key Metrics:
- AI (Asymmetry Index): Deviation from uniform error distribution
- PCR (Pathway Concentration Ratio): Error concentration in dominant pathways
- EEC (Entanglement-Error Correlation): Topology-error pattern correlation
- TPS (Temporal Pathway Stability): Consistency across noise conditions
- CES (Complexity Emergence Score): Critical threshold identification

Dependencies: Pydantic only
Used by: Engine analysis pipeline, research result storage, publications
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from datetime import datetime


class StructuredDecoherenceMetrics(BaseModel):
    """
    Complete structured decoherence pathway metrics.

    These metrics quantify whether quantum decoherence follows structured
    pathways determined by entanglement topology vs purely random patterns.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    # ===== Core Metrics =====
    asymmetry_index: float = Field(
        ge=0.0,
        description="AI: Deviation from uniform error distribution. Formula: (1/N) Σᵢ |pᵢ - p_uniform| / p_uniform",
    )

    pathway_concentration_ratio: float = Field(
        ge=0.0,
        description="PCR: Concentration of errors in top pathways vs bottom pathways. Formula: (Top 25% frequencies) / (Bottom 25% frequencies)",
    )

    entanglement_error_correlation: float = Field(
        ge=-1.0,
        le=1.0,
        description="EEC: Correlation between entanglement topology and error patterns. Range: [-1, 1]",
    )

    temporal_pathway_stability: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="TPS: Consistency of pathway rankings across noise levels. Range: [0, 1], None if single condition",
    )

    complexity_emergence_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="CES: Critical threshold where structured patterns emerge. None if insufficient data",
    )

    # ===== New Schema Metrics =====
    structure_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="SS: Jensen-Shannon divergence from null model. Measures structure vs randomness",
    )

    concentration_index: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="CI: Gini coefficient of error distribution. Measures inequality in error patterns",
    )

    total_correlation: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="TC: Multi-information in quantum measurements. Measures total correlation among qubits",
    )

    # ===== Analysis Metadata =====
    metadata: AnalysisMetadata = Field(
        description="Metadata about the analysis conditions and parameters"
    )

    pathway_analysis: PathwayAnalysis = Field(
        description="Human-readable analysis of pathway characteristics"
    )

    # ===== Computed Properties =====
    @property
    def is_structured(self) -> bool:
        """Determine if patterns show structured vs random decoherence."""
        # Heuristic: structured if AI > 0.3 AND PCR > 1.5 AND |EEC| > 0.3
        return (
            self.asymmetry_index > 0.3
            and self.pathway_concentration_ratio > 1.5
            and abs(self.entanglement_error_correlation) > 0.3
        )

    @property
    def structure_confidence(self) -> float:
        """Confidence score for structured pattern detection (0-1)."""
        # Weighted combination of metrics
        ai_score = min(1.0, self.asymmetry_index / 0.5)
        pcr_score = min(1.0, (self.pathway_concentration_ratio - 1.0) / 2.0)
        eec_score = abs(self.entanglement_error_correlation)

        return ai_score * 0.4 + pcr_score * 0.3 + eec_score * 0.3

    # ===== Field Normalization / Safety =====
    @field_validator("entanglement_error_correlation")
    @classmethod
    def _clip_eec(cls, v: float) -> float:
        """Clip to [-1, 1] to survive floating-point noise from upstream computations."""
        if v is None:
            return v
        if v > 1.0:
            return 1.0
        if v < -1.0:
            return -1.0
        return float(v)


class AnalysisMetadata(BaseModel):
    """Metadata about the structured decoherence analysis."""

    state_type: str = Field(description="Quantum state type (GHZ, W, BELL, etc.)")
    num_qubits: int = Field(ge=1, description="Number of qubits in the system")
    total_shots: int = Field(ge=1, description="Total measurement shots used")
    unique_outcomes: int = Field(
        ge=1, description="Number of unique measurement outcomes"
    )

    analysis_timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="When the analysis was performed",
    )

    noise_conditions: Optional[Dict[str, Any]] = Field(
        default=None, description="Noise model parameters used"
    )

    computation_time_ms: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Time taken to compute metrics in milliseconds",
    )


class PathwayAnalysis(BaseModel):
    """Human-readable analysis of decoherence pathways."""

    # Dominant pathways (bitstring, probability) pairs
    dominant_pathways: List[Tuple[str, float]] = Field(
        description="Top error pathways as (bitstring, probability) pairs"
    )

    pathway_concentration: str = Field(
        description="Qualitative assessment of pathway concentration"
    )

    asymmetry_level: str = Field(
        description="Qualitative level of asymmetry in error distribution"
    )

    entanglement_influence: str = Field(
        description="Qualitative assessment of entanglement topology influence"
    )

    # Statistical summary
    total_outcomes: int = Field(ge=1, description="Total possible outcomes")
    measurement_shots: int = Field(ge=1, description="Measurement shots used")

    # Research insights
    research_notes: Optional[str] = Field(
        default=None, description="Additional research insights or observations"
    )

    @field_validator("dominant_pathways")
    @classmethod
    def _validate_dominant_probabilities(
        cls, v: List[Tuple[str, float]]
    ) -> List[Tuple[str, float]]:
        """Ensure probabilities are within [0, 1]."""
        for bitstring, p in v:
            if p < 0.0 or p > 1.0:
                raise ValueError(
                    f"dominant_pathways probability for '{bitstring}' must be within [0, 1], got {p}"
                )
        return v

    @field_validator("pathway_concentration")
    @classmethod
    def validate_concentration_level(cls, v: str) -> str:
        """Validate concentration level is one of expected values."""
        valid_levels = ["very_low", "low", "moderate", "high", "very_high"]
        if v not in valid_levels:
            raise ValueError(f"pathway_concentration must be one of {valid_levels}")
        return v

    @field_validator("asymmetry_level")
    @classmethod
    def validate_asymmetry_level(cls, v: str) -> str:
        """Validate asymmetry level is one of expected values."""
        valid_levels = [
            "very_uniform",
            "slight_asymmetry",
            "moderate_asymmetry",
            "high_asymmetry",
        ]
        if v not in valid_levels:
            raise ValueError(f"asymmetry_level must be one of {valid_levels}")
        return v

    @field_validator("entanglement_influence")
    @classmethod
    def validate_entanglement_influence(cls, v: str) -> str:
        """Validate entanglement influence is one of expected values."""
        valid_levels = [
            "no_correlation",
            "weak_correlation",
            "moderate_correlation",
            "strong_correlation",
        ]
        if v not in valid_levels:
            raise ValueError(f"entanglement_influence must be one of {valid_levels}")
        return v


class ResearchMetadata(BaseModel):
    """
    Metadata for research experiments and campaigns.

    Purpose: Track research context, hypotheses, and experimental conditions
    for structured decoherence studies.
    """

    # Research context
    hypothesis: Optional[str] = Field(
        default=None, description="Research hypothesis being tested"
    )

    research_phase: Optional[str] = Field(
        default=None,
        description="Phase of research (threshold, characterization, validation, etc.)",
    )

    campaign_id: Optional[str] = Field(
        default=None,
        description="Research campaign identifier for grouping related experiments",
    )

    # Experimental conditions
    expected_outcomes: Optional[List[str]] = Field(
        default=None, description="Expected experimental outcomes or predictions"
    )

    control_experiment: bool = Field(
        default=False, description="Whether this is a control experiment"
    )

    # Publication metadata
    publication_ready: bool = Field(
        default=False, description="Whether results meet publication quality standards"
    )

    figure_candidate: bool = Field(
        default=False,
        description="Whether results are suitable for publication figures",
    )


class ComparisonMetrics(BaseModel):
    """
    Metrics for comparing structured decoherence across different conditions.

    Purpose: Enable statistical comparison of pathway metrics across
    different quantum states, noise levels, and system sizes.
    """

    # Statistical comparison
    baseline_metrics: Optional[StructuredDecoherenceMetrics] = Field(
        default=None, description="Baseline metrics for comparison"
    )

    delta_asymmetry_index: Optional[float] = Field(
        default=None, description="Change in AI relative to baseline"
    )

    delta_pathway_concentration: Optional[float] = Field(
        default=None, description="Change in PCR relative to baseline"
    )

    delta_entanglement_correlation: Optional[float] = Field(
        default=None, description="Change in EEC relative to baseline"
    )

    # Significance testing
    statistical_significance: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="P-value for statistical significance of differences",
    )

    effect_size: Optional[float] = Field(
        default=None, description="Effect size (Cohen's d) for practical significance"
    )

    # Trend analysis
    trend_direction: Optional[str] = Field(
        default=None, description="Overall trend direction across conditions"
    )

    @field_validator("trend_direction")
    @classmethod
    def validate_trend_direction(cls, v: Optional[str]) -> Optional[str]:
        """Validate trend direction."""
        if v is not None:
            valid_trends = [
                "increasing",
                "decreasing",
                "stable",
                "nonlinear",
                "unclear",
            ]
            if v not in valid_trends:
                raise ValueError(f"trend_direction must be one of {valid_trends}")
        return v


# Resolve forward references defensively (Pydantic v2 is usually fine, this makes it bulletproof)
StructuredDecoherenceMetrics.model_rebuild()
PathwayAnalysis.model_rebuild()
AnalysisMetadata.model_rebuild()
ResearchMetadata.model_rebuild()
ComparisonMetrics.model_rebuild()
