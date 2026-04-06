"""Engine Models Package.

Purpose:
    Pydantic models that define the complete API contract for the quantum
    experiment engine. These models are the single source of truth for:
    - JSON schema generation
    - Type validation
    - API documentation
    - Frontend TypeScript interface generation

Architecture:
    - config.py      : Experiment configuration models
    - metadata.py    : Experiment identification and context
    - circuit.py     : Quantum circuit statistics
    - measurement.py : Measurement data and statistics
    - provenance.py  : Reproducibility provenance tracking
    - quality.py     : Quality assessment metrics
    - results.py     : Top-level result composition (imports above)
    - research.py    : Structured decoherence research models
    - sweep.py       : Parameter sweep configuration and results
    - storage.py     : Storage, artifacts, and manifest models

Dependencies:
    Pydantic only (plus Python stdlib typing)

Used by:
    Engine API, CLI, validation layers, future React frontend
"""

from __future__ import annotations

# ===== Focused Model Submodules =====
from .circuit import CircuitStatistics

# ===== Configuration =====
from .config import (
    AdvancedNoiseConfig,
    ExperimentConfig,
)
from .measurement import MeasurementResults
from .metadata import ExperimentMetadata
from .provenance import Provenance
from .quality import QualityMetrics, compute_quality_metrics

# ===== Research Metrics =====
from .research import (
    AnalysisMetadata,
    MetricEntry,
    MetricsBundle,
    ResearchMetadata,
)

# ===== Results (composes above) =====
from .results import (
    ExperimentAnalysis,
    ExperimentResult,
    ExperimentStatus,
)

# ===== Storage & Artifacts =====
from .storage import (
    ArtifactRef,
    DirectoryStructure,
    ExperimentManifestEntry,
    ResultManifest,
    StorageConfig,
)

# ===== Sweeps =====
from .sweep import (
    InteractionEffect,
    OutcomeStatistics,
    ParameterAnalysis,
    ParameterEffect,
    StatisticalSummary,
    SweepExecutionMetadata,
    SweepManifest,
    SweepResearchInsights,
    SweepResult,
)

__all__ = [
    # Configuration
    "ExperimentConfig",
    "AdvancedNoiseConfig",
    # Results
    "ExperimentResult",
    "ExperimentAnalysis",
    "ExperimentMetadata",
    "CircuitStatistics",
    "MeasurementResults",
    "QualityMetrics",
    "Provenance",
    "ExperimentStatus",
    "compute_quality_metrics",
    # Research Metrics
    "MetricEntry",
    "MetricsBundle",
    "AnalysisMetadata",
    "ResearchMetadata",
    # Sweeps
    "SweepManifest",
    "SweepResult",
    "ParameterAnalysis",
    "ParameterEffect",
    "InteractionEffect",
    "StatisticalSummary",
    "OutcomeStatistics",
    "SweepResearchInsights",
    "SweepExecutionMetadata",
    # Storage & Artifacts
    "ArtifactRef",
    "StorageConfig",
    "DirectoryStructure",
    "ResultManifest",
    "ExperimentManifestEntry",
]
