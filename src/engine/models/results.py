"""
Experiment Result Models

Purpose: Define the complete structure for quantum experiment results.
These models capture all output from quantum experiments including
raw data, analysis, metrics, and provenance information.

Key Features:
- Structured result storage
- Research metrics integration
- Provenance tracking for reproducibility
- Artifact management
- Publication-ready metadata

Dependencies: Pydantic, research models
Used by: Engine API, storage systems, analysis pipelines
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Literal, Tuple
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from datetime import datetime
import math
import logging

from .research import StructuredDecoherenceMetrics, ResearchMetadata
from .storage import ArtifactRef

logger = logging.getLogger(__name__)


class ExperimentResult(BaseModel):
    """
    Complete quantum experiment result.

    This model captures everything needed to understand, reproduce,
    and build upon a quantum experiment result.
    """

    model_config = ConfigDict(
        extra="allow",  # Allow additional fields for extensibility
        validate_assignment=True,
    )

    # ===== Core Analysis =====
    analysis: ExperimentAnalysis = Field(
        description="Complete experimental analysis including raw data and metrics"
    )

    # ===== Research Metrics =====
    structured_decoherence_metrics: Optional[StructuredDecoherenceMetrics] = Field(
        default=None,
        description="Structured decoherence pathway metrics (AI, PCR, EEC, TPS, CES)",
    )

    research_metadata: Optional[ResearchMetadata] = Field(
        default=None, description="Research context and experimental metadata"
    )

    # ===== System Information =====
    provenance: Provenance = Field(
        description="Complete provenance information for reproducibility"
    )

    # ===== Results Management =====
    artifacts: List[ArtifactRef] = Field(
        default_factory=list,
        description="References to generated files (plots, reports, etc.)",
    )

    config_hash: str = Field(
        description="Hash of experiment configuration for deduplication"
    )

    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="When the experiment was completed",
    )

    # ===== Status and Quality =====
    status: ExperimentStatus = Field(
        default="completed", description="Experiment execution status"
    )

    quality_metrics: Optional[QualityMetrics] = Field(
        default=None, description="Quality assessment of experiment results"
    )

    # ===== Computed Properties =====
    @property
    def is_research_experiment(self) -> bool:
        """Check if this is a research experiment with structured decoherence metrics."""
        return self.structured_decoherence_metrics is not None

    @property
    def has_structured_patterns(self) -> bool:
        """Check if structured decoherence patterns were detected."""
        if self.structured_decoherence_metrics is None:
            return False
        return self.structured_decoherence_metrics.is_structured

    @property
    def total_shots(self) -> int:
        """Get total measurement shots from analysis."""
        return self.analysis.measurement_results.total_shots


class ExperimentAnalysis(BaseModel):
    """
    Core experimental analysis data.

    This captures the essential analysis outputs from quantum experiments,
    separated from metadata for clean data access.
    """

    # Experiment identification
    experiment_metadata: ExperimentMetadata = Field(
        description="Basic experiment identification and context"
    )

    # Input parameters
    experiment_parameters: Dict[str, Any] = Field(
        description="Complete experiment configuration parameters"
    )

    # Circuit information
    circuit_statistics: CircuitStatistics = Field(
        description="Quantum circuit characteristics and statistics"
    )

    # Core results
    measurement_results: MeasurementResults = Field(
        description="Raw measurement data and basic statistics"
    )

    # Optional advanced analysis
    information_theory_metrics: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Information-theoretic analysis (entropy, mutual information, etc.)",
    )

    correlation_analysis: Optional[Dict[str, Any]] = Field(
        default=None, description="Quantum correlation and entanglement analysis"
    )

    statistical_validation: Optional[Dict[str, Any]] = Field(
        default=None, description="Statistical validation and confidence measures"
    )


class ExperimentMetadata(BaseModel):
    """Basic experiment identification and context."""

    experiment_id: str = Field(description="Unique experiment identifier")
    timestamp: str = Field(description="When experiment was performed")
    framework_version: str = Field(description="Quantum experiment framework version")

    research_type: Optional[str] = Field(
        default=None, description="Type of research analysis performed"
    )

    experiment_description: Optional[str] = Field(
        default=None, description="Human-readable description of experiment purpose"
    )


class CircuitStatistics(BaseModel):
    """Quantum circuit characteristics and statistics."""

    depth: int = Field(ge=0, description="Circuit depth (number of time steps)")
    num_gates: int = Field(ge=0, description="Total number of gates")
    num_qubits: int = Field(ge=1, description="Number of qubits")

    gate_types: Dict[str, int] = Field(
        default_factory=dict, description="Count of each gate type used"
    )

    # Advanced circuit metrics
    two_qubit_gate_count: Optional[int] = Field(
        default=None,
        ge=0,
        description="Number of two-qubit gates (entangling operations)",
    )

    connectivity_graph: Optional[List[List[int]]] = Field(
        default=None, description="Qubit connectivity graph for multi-qubit operations"
    )

    @model_validator(mode="after")
    def _reconcile_circuit_stats(self) -> "CircuitStatistics":
        """
        Auto-heal common inconsistencies:
        - If gate_types sum doesn't match num_gates, set num_gates = sum(gate_types)
        - Clamp two_qubit_gate_count to [0, num_gates]
        - Sanitize connectivity_graph as list of 2-int edges within [0, num_qubits-1]
        """
        if self.gate_types:
            summed = sum(int(v) for v in self.gate_types.values())
            if summed != self.num_gates:
                logger.warning(
                    f"[CircuitStatistics] num_gates={self.num_gates} != sum(gate_types)={summed}; "
                    f"reconciling to {summed}"
                )
                self.num_gates = summed

        if self.two_qubit_gate_count is not None:
            if self.two_qubit_gate_count > self.num_gates:
                logger.warning(
                    f"[CircuitStatistics] two_qubit_gate_count={self.two_qubit_gate_count} > num_gates={self.num_gates}; "
                    f"clamping to {self.num_gates}"
                )
                self.two_qubit_gate_count = self.num_gates
            if self.two_qubit_gate_count < 0:
                self.two_qubit_gate_count = 0

        if self.connectivity_graph is not None:
            cleaned: List[List[int]] = []
            for edge in self.connectivity_graph:
                if not isinstance(edge, list) or len(edge) != 2:
                    continue
                u, v = edge
                if not (isinstance(u, int) and isinstance(v, int)):
                    continue
                if 0 <= u < self.num_qubits and 0 <= v < self.num_qubits and u != v:
                    cleaned.append([u, v])
            dropped = len(self.connectivity_graph) - len(cleaned)
            if dropped > 0:
                logger.warning(
                    f"[CircuitStatistics] Dropped {dropped} invalid edges from connectivity_graph"
                )
            self.connectivity_graph = cleaned if cleaned else None

        return self


class MeasurementResults(BaseModel):
    """Raw measurement data and basic statistics."""

    raw_counts: Dict[str, int] = Field(
        description="Raw measurement counts as {bitstring: count} pairs"
    )

    total_shots: int = Field(ge=1, description="Total number of measurement shots")

    unique_outcomes: int = Field(
        ge=1, description="Number of unique measurement outcomes observed"
    )

    outcome_probabilities: Dict[str, float] = Field(
        description="Normalized probabilities for each outcome"
    )

    # Optional advanced measurements
    density_matrix: Optional[List[List[float]]] = Field(
        default=None,
        description="Reconstructed density matrix (for density simulation mode)",
    )

    fidelity: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Fidelity with ideal state (if computed)",
    )

    @classmethod
    def from_counts(cls, counts: Dict[str, int]) -> "MeasurementResults":
        """
        Convenience constructor from raw counts; computes total_shots, unique_outcomes, and probabilities.
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
    def _precompute_probs(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        If outcome_probabilities is missing or empty, compute it from raw_counts/total_shots.
        """
        if not isinstance(data, dict):
            return data
        counts = data.get("raw_counts") or {}
        total = data.get("total_shots")
        probs = data.get("outcome_probabilities")
        if (not probs) and counts and total:
            try:
                total = int(total)
                if total > 0:
                    data["outcome_probabilities"] = {
                        k: v / total for k, v in counts.items()
                    }
            except Exception:
                pass
        return data

    @model_validator(mode="after")
    def _validate_and_heal(self) -> "MeasurementResults":
        """
        Auto-heal and validate:
        - Ensure total_shots == sum(raw_counts); if not, fix to sum(raw_counts)
        - Ensure unique_outcomes == len(raw_counts); if not, fix it
        - Ensure outcome_probabilities keys match raw_counts; recompute if needed
        - Normalize probabilities to sum ~ 1 (within tolerance)
        """
        # Fix totals
        sum_counts = (
            int(sum(int(v) for v in self.raw_counts.values())) if self.raw_counts else 0
        )
        if sum_counts <= 0:
            raise ValueError(
                "MeasurementResults.raw_counts must be non-empty with positive totals"
            )

        if self.total_shots != sum_counts:
            logger.warning(
                f"[MeasurementResults] total_shots={self.total_shots} != sum(raw_counts)={sum_counts}; "
                f"setting total_shots={sum_counts}"
            )
            self.total_shots = sum_counts

        expected_unique = len(self.raw_counts)
        if self.unique_outcomes != expected_unique:
            logger.warning(
                f"[MeasurementResults] unique_outcomes={self.unique_outcomes} != len(raw_counts)={expected_unique}; "
                f"setting unique_outcomes={expected_unique}"
            )
            self.unique_outcomes = expected_unique

        # Recompute/normalize probabilities if mismatched
        if (not self.outcome_probabilities) or (
            set(self.outcome_probabilities.keys()) != set(self.raw_counts.keys())
        ):
            self.outcome_probabilities = {
                k: v / self.total_shots for k, v in self.raw_counts.items()
            }
        else:
            # Normalize if needed (tolerance 1e-8)
            total_p = float(sum(self.outcome_probabilities.values()))
            if not math.isfinite(total_p) or total_p <= 0.0:
                self.outcome_probabilities = {
                    k: v / self.total_shots for k, v in self.raw_counts.items()
                }
            elif abs(total_p - 1.0) > 1e-8:
                logger.warning(
                    f"[MeasurementResults] outcome_probabilities sum={total_p:.6f} != 1.0; normalizing"
                )
                self.outcome_probabilities = {
                    k: p / total_p for k, p in self.outcome_probabilities.items()
                }

        # Clip tiny negatives / >1 due to FP
        for k, p in list(self.outcome_probabilities.items()):
            if p < 0.0 and p > -1e-12:
                self.outcome_probabilities[k] = 0.0
            elif p > 1.0 and p < 1.0 + 1e-12:
                self.outcome_probabilities[k] = 1.0

        return self


class QualityMetrics(BaseModel):
    """Quality assessment of experiment results."""

    # Data quality
    shot_adequacy: float = Field(
        ge=0.0,
        le=1.0,
        description="Adequacy of shot count for statistical significance",
    )

    outcome_coverage: float = Field(
        ge=0.0, le=1.0, description="Fraction of possible outcomes observed"
    )

    # Statistical quality
    confidence_level: float = Field(
        ge=0.0, le=1.0, description="Statistical confidence in results"
    )

    convergence_achieved: bool = Field(
        description="Whether statistical convergence was achieved"
    )

    # Research quality
    research_significance: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Research significance score for structured decoherence studies",
    )

    publication_readiness: Optional[str] = Field(
        default=None, description="Assessment of publication readiness"
    )

    @classmethod
    def from_measurements(
        cls,
        meas: MeasurementResults,
        num_qubits: Optional[int] = None,
        *,
        target_ci_half_width: float = 0.02,
        z_value: float = 1.96,
        convergence_threshold: float = 0.95,
        coverage_weight: float = 0.5,
    ) -> "QualityMetrics":
        """
        Convenience constructor computing core quality metrics from measurements.

        Args:
            meas: MeasurementResults instance
            num_qubits: Number of qubits (if None, inferred from count bitstring length)
            target_ci_half_width: Target half-width for per-outcome CI (e.g., ±2%)
            z_value: Z-score for CI (1.96 ≈ 95%)
            convergence_threshold: shot_adequacy threshold to mark convergence
            coverage_weight: contribution of coverage to confidence_level (0..1)

        Returns:
            QualityMetrics with shot_adequacy, outcome_coverage, confidence_level, convergence_achieved
        """
        inferred_n = num_qubits
        if inferred_n is None:
            try:
                inferred_n = max(
                    len(k.replace(" ", "")) for k in meas.raw_counts.keys()
                )
            except Exception:
                # fallback: infer from support size
                inferred_n = max(
                    1, int(math.ceil(math.log2(max(1, meas.unique_outcomes))))
                )

        possible_outcomes = max(1, 2**inferred_n)
        coverage = min(1.0, meas.unique_outcomes / possible_outcomes)

        required = _estimate_required_shots_for_precision(
            unique_outcomes=meas.unique_outcomes,
            target_ci_half_width=target_ci_half_width,
            z_value=z_value,
        )
        adequacy = 1.0 if required <= 0 else min(1.0, meas.total_shots / required)

        # Blend adequacy and coverage into a simple confidence proxy
        coverage_weight = min(max(coverage_weight, 0.0), 1.0)
        confidence = min(
            1.0,
            max(0.0, coverage_weight * coverage + (1.0 - coverage_weight) * adequacy),
        )

        converged = adequacy >= convergence_threshold

        # Simple publication readiness heuristic (optional)
        pub = None
        if converged and confidence >= 0.9:
            pub = "figure-ready"
        elif adequacy >= 0.7:
            pub = "draft"

        return cls(
            shot_adequacy=adequacy,
            outcome_coverage=coverage,
            confidence_level=confidence,
            convergence_achieved=converged,
            publication_readiness=pub,
        )


class Provenance(BaseModel):
    """
    Complete provenance information for experiment reproducibility.

    This captures all information needed to exactly reproduce an experiment,
    following research best practices for computational reproducibility.
    """

    # Version information
    schema_version: str = Field(
        default="1.0.0", description="Provenance schema version"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Provenance record creation timestamp",
    )

    # Software environment
    software_versions: Dict[str, str] = Field(
        default_factory=dict, description="Versions of all software dependencies"
    )

    # Hardware environment
    host_info: Dict[str, str] = Field(
        default_factory=dict, description="Host system information"
    )

    # Code version
    git_sha: Optional[str] = Field(
        default=None, description="Git commit SHA for exact code version"
    )

    # Randomness control
    rng_seed: Optional[int] = Field(
        default=None, description="Random number generator seed used"
    )

    # Simulation details
    simulator_info: Dict[str, Any] = Field(
        default_factory=dict, description="Quantum simulator configuration and metadata"
    )

    transpilation_summary: Dict[str, Any] = Field(
        default_factory=dict,
        description="Circuit transpilation details and optimizations",
    )

    # Execution details
    execution_time_seconds: Optional[float] = Field(
        default=None, ge=0.0, description="Total execution time in seconds"
    )

    memory_usage_mb: Optional[float] = Field(
        default=None, ge=0.0, description="Peak memory usage in megabytes"
    )


# Status enumeration
ExperimentStatus = Literal[
    "pending",  # Experiment queued but not started
    "running",  # Experiment currently executing
    "completed",  # Experiment completed successfully
    "failed",  # Experiment failed with error
    "cancelled",  # Experiment cancelled by user
    "timeout",  # Experiment exceeded time limit
]


# ---------- Helpers (module-level) ----------


def _estimate_required_shots_for_precision(
    *,
    unique_outcomes: int,
    target_ci_half_width: float = 0.02,
    z_value: float = 1.96,
) -> int:
    """
    Estimate required shots for a desired per-outcome CI half-width (±w) under a
    multinomial model, using the per-outcome binomial approximation.

    Assumes (conservatively for structured data) p ≈ 1/unique_outcomes.
    Half-width ≈ z * sqrt(p(1-p) / N)  ⇒  N ≥ z^2 * p(1-p) / w^2

    Args:
        unique_outcomes: number of observed outcomes (support size)
        target_ci_half_width: desired half-width (e.g., 0.02 for ±2%)
        z_value: z-score (1.96 ≈ 95% CI)

    Returns:
        int: estimated number of required shots
    """
    m = max(1, int(unique_outcomes))
    p = 1.0 / m
    var = p * (1.0 - p)
    w = max(1e-6, float(target_ci_half_width))
    required = (z_value**2) * var / (w**2)
    return int(math.ceil(required))


def compute_quality_metrics(
    meas: MeasurementResults,
    num_qubits: Optional[int] = None,
    *,
    target_ci_half_width: float = 0.02,
    z_value: float = 1.96,
    convergence_threshold: float = 0.95,
    coverage_weight: float = 0.5,
) -> QualityMetrics:
    """
    Compute QualityMetrics from MeasurementResults (engine-friendly helper).

    This is a thin wrapper around `QualityMetrics.from_measurements` so callers
    don’t need to touch the model classmethod directly.

    Args:
        meas: MeasurementResults instance
        num_qubits: Number of qubits (inferred from counts if None)
        target_ci_half_width: desired per-outcome half-width (±w)
        z_value: z-score for CI (1.96 ≈ 95%)
        convergence_threshold: adequacy threshold to mark convergence
        coverage_weight: contribution of coverage to confidence_level

    Returns:
        QualityMetrics
    """
    return QualityMetrics.from_measurements(
        meas,
        num_qubits,
        target_ci_half_width=target_ci_half_width,
        z_value=z_value,
        convergence_threshold=convergence_threshold,
        coverage_weight=coverage_weight,
    )


# Forward-ref resolution to be bulletproof with Pydantic v2
ExperimentResult.model_rebuild()
ExperimentAnalysis.model_rebuild()
ExperimentMetadata.model_rebuild()
CircuitStatistics.model_rebuild()
MeasurementResults.model_rebuild()
QualityMetrics.model_rebuild()
Provenance.model_rebuild()
