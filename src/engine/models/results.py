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
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

from .research import StructuredDecoherenceMetrics, ResearchMetadata
from .storage import ArtifactRef


class ExperimentResult(BaseModel):
    """
    Complete quantum experiment result.
    
    This model captures everything needed to understand, reproduce,
    and build upon a quantum experiment result.
    """
    
    model_config = ConfigDict(
        extra="allow",  # Allow additional fields for extensibility
        validate_assignment=True
    )
    
    # ===== Core Analysis =====
    analysis: ExperimentAnalysis = Field(
        description="Complete experimental analysis including raw data and metrics"
    )
    
    # ===== Research Metrics =====
    structured_decoherence_metrics: Optional[StructuredDecoherenceMetrics] = Field(
        default=None,
        description="Structured decoherence pathway metrics (AI, PCR, EEC, TPS, CES)"
    )
    
    research_metadata: Optional[ResearchMetadata] = Field(
        default=None,
        description="Research context and experimental metadata"
    )
    
    # ===== System Information =====
    provenance: Provenance = Field(
        description="Complete provenance information for reproducibility"
    )
    
    # ===== Results Management =====
    artifacts: List[ArtifactRef] = Field(
        default_factory=list,
        description="References to generated files (plots, reports, etc.)"
    )
    
    config_hash: str = Field(
        description="Hash of experiment configuration for deduplication"
    )
    
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="When the experiment was completed"
    )
    
    # ===== Status and Quality =====
    status: ExperimentStatus = Field(
        default="completed",
        description="Experiment execution status"
    )
    
    quality_metrics: Optional[QualityMetrics] = Field(
        default=None,
        description="Quality assessment of experiment results"
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
        description="Information-theoretic analysis (entropy, mutual information, etc.)"
    )
    
    correlation_analysis: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Quantum correlation and entanglement analysis"
    )
    
    statistical_validation: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Statistical validation and confidence measures"
    )


class ExperimentMetadata(BaseModel):
    """Basic experiment identification and context."""
    
    experiment_id: str = Field(description="Unique experiment identifier")
    timestamp: str = Field(description="When experiment was performed")
    framework_version: str = Field(description="Quantum experiment framework version")
    
    research_type: Optional[str] = Field(
        default=None,
        description="Type of research analysis performed"
    )
    
    experiment_description: Optional[str] = Field(
        default=None,
        description="Human-readable description of experiment purpose"
    )


class CircuitStatistics(BaseModel):
    """Quantum circuit characteristics and statistics."""
    
    depth: int = Field(ge=0, description="Circuit depth (number of time steps)")
    num_gates: int = Field(ge=0, description="Total number of gates")
    num_qubits: int = Field(ge=1, description="Number of qubits")
    
    gate_types: Dict[str, int] = Field(
        default_factory=dict,
        description="Count of each gate type used"
    )
    
    # Advanced circuit metrics
    two_qubit_gate_count: Optional[int] = Field(
        default=None, ge=0,
        description="Number of two-qubit gates (entangling operations)"
    )
    
    connectivity_graph: Optional[List[List[int]]] = Field(
        default=None,
        description="Qubit connectivity graph for multi-qubit operations"
    )


class MeasurementResults(BaseModel):
    """Raw measurement data and basic statistics."""
    
    raw_counts: Dict[str, int] = Field(
        description="Raw measurement counts as {bitstring: count} pairs"
    )
    
    total_shots: int = Field(
        ge=1,
        description="Total number of measurement shots"
    )
    
    unique_outcomes: int = Field(
        ge=1, 
        description="Number of unique measurement outcomes observed"
    )
    
    outcome_probabilities: Dict[str, float] = Field(
        description="Normalized probabilities for each outcome"
    )
    
    # Optional advanced measurements
    density_matrix: Optional[List[List[float]]] = Field(
        default=None,
        description="Reconstructed density matrix (for density simulation mode)"
    )
    
    fidelity: Optional[float] = Field(
        default=None, ge=0.0, le=1.0,
        description="Fidelity with ideal state (if computed)"
    )


class QualityMetrics(BaseModel):
    """Quality assessment of experiment results."""
    
    # Data quality
    shot_adequacy: float = Field(
        ge=0.0, le=1.0,
        description="Adequacy of shot count for statistical significance"
    )
    
    outcome_coverage: float = Field(
        ge=0.0, le=1.0, 
        description="Fraction of possible outcomes observed"
    )
    
    # Statistical quality
    confidence_level: float = Field(
        ge=0.0, le=1.0,
        description="Statistical confidence in results"
    )
    
    convergence_achieved: bool = Field(
        description="Whether statistical convergence was achieved"
    )
    
    # Research quality
    research_significance: Optional[float] = Field(
        default=None, ge=0.0, le=1.0,
        description="Research significance score for structured decoherence studies"
    )
    
    publication_readiness: Optional[str] = Field(
        default=None,
        description="Assessment of publication readiness"
    )


class Provenance(BaseModel):
    """
    Complete provenance information for experiment reproducibility.
    
    This captures all information needed to exactly reproduce an experiment,
    following research best practices for computational reproducibility.
    """
    
    # Version information
    schema_version: str = Field(default="1.0.0", description="Provenance schema version")
    timestamp: str = Field(description="Provenance record creation timestamp")
    
    # Software environment
    software_versions: Dict[str, str] = Field(
        default_factory=dict,
        description="Versions of all software dependencies"
    )
    
    # Hardware environment  
    host_info: Dict[str, str] = Field(
        default_factory=dict,
        description="Host system information"
    )
    
    # Code version
    git_sha: Optional[str] = Field(
        default=None,
        description="Git commit SHA for exact code version"
    )
    
    # Randomness control
    rng_seed: Optional[int] = Field(
        default=None,
        description="Random number generator seed used"
    )
    
    # Simulation details
    simulator_info: Dict[str, Any] = Field(
        default_factory=dict,
        description="Quantum simulator configuration and metadata"
    )
    
    transpilation_summary: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Circuit transpilation details and optimizations"
    )
    
    # Execution details
    execution_time_seconds: Optional[float] = Field(
        default=None, ge=0.0,
        description="Total execution time in seconds"
    )
    
    memory_usage_mb: Optional[float] = Field(
        default=None, ge=0.0,
        description="Peak memory usage in megabytes"
    )


# Status enumeration
ExperimentStatus = Literal[
    "pending",      # Experiment queued but not started
    "running",      # Experiment currently executing  
    "completed",    # Experiment completed successfully
    "failed",       # Experiment failed with error
    "cancelled",    # Experiment cancelled by user
    "timeout"       # Experiment exceeded time limit
]