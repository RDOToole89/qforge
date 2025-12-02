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
    AdvancedNoiseConfig,
    ExperimentConfig,
)

# ===== Research (Structured Decoherence) =====
from .research import (
    AnalysisMetadata,
    ComparisonMetrics,
    PathwayAnalysis,
    ResearchMetadata,
    StructuredDecoherenceMetrics,
)

# ===== Results =====
from .results import (
    CircuitStatistics,
    ExperimentAnalysis,
    ExperimentMetadata,
    ExperimentResult,
    ExperimentStatus,  # Literal type
    MeasurementResults,
    Provenance,
    QualityMetrics,
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
