"""
Engine Models Package

Purpose:
    Pydantic models that define the complete API contract for the quantum
    experiment engine. These models are the single source of truth for:
    - JSON schema generation
    - Type validation
    - API documentation
    - Frontend TypeScript interface generation

Architecture:
    - config.py      : Experiment configuration models
    - results.py     : Experiment result models (raw data, analysis, provenance)
    - research.py    : Structured decoherence research models (metrics & analysis)
    - sweep.py       : Parameter sweep configuration and result models
    - storage.py     : Storage, artifacts, and manifest models

Dependencies:
    Pydantic only (plus Python stdlib typing)

Used by:
    Engine API, CLI, validation layers, future React frontend
"""

from __future__ import annotations

# ===== Configuration =====
from .config import (
    ExperimentConfig,
    AdvancedNoiseConfig,
)

# ===== Results =====
from .results import (
    ExperimentResult,
    ExperimentAnalysis,
    ExperimentMetadata,
    CircuitStatistics,
    MeasurementResults,
    QualityMetrics,
    Provenance,
    ExperimentStatus,  # Literal type
)

# ===== Research (Structured Decoherence) =====
from .research import (
    StructuredDecoherenceMetrics,
    AnalysisMetadata,
    PathwayAnalysis,
    ResearchMetadata,
    ComparisonMetrics,
)

# ===== Sweeps =====
from .sweep import (
    SweepManifest,
    SweepResult,
    ParameterAnalysis,
    ParameterEffect,
    InteractionEffect,
    StatisticalSummary,
    OutcomeStatistics,
    SweepResearchInsights,
    SweepExecutionMetadata,
)

# ===== Storage & Artifacts =====
from .storage import (
    ArtifactRef,
    StorageConfig,
    DirectoryStructure,
    ResultManifest,
    ExperimentManifestEntry,
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
    # Research (Structured Decoherence)
    "StructuredDecoherenceMetrics",
    "AnalysisMetadata",
    "PathwayAnalysis",
    "ResearchMetadata",
    "ComparisonMetrics",
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
