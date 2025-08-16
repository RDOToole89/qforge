"""
Engine Models Package

Purpose: Pydantic models that define the complete API contract for the quantum experiment engine.
These models serve as the single source of truth for:
- JSON schema generation
- Type validation
- API documentation 
- Frontend TypeScript interface generation

Architecture:
- config.py: Experiment configuration models
- results.py: Experiment result models
- research.py: Research-specific models (structured decoherence metrics)
- sweep.py: Parameter sweep models
- storage.py: Storage and artifact models

Dependencies: None (pure Pydantic models)
Used by: Engine API, CLI, future React frontend, validation layers
"""

# Main exports for backwards compatibility and clean imports
from .config import ExperimentConfig
from .results import ExperimentResult, Provenance
from .research import StructuredDecoherenceMetrics, ResearchMetadata
from .sweep import SweepManifest, SweepResult
from .storage import ArtifactRef, StorageConfig

__all__ = [
    # Configuration
    "ExperimentConfig",
    
    # Results
    "ExperimentResult", 
    "Provenance",
    
    # Research
    "StructuredDecoherenceMetrics",
    "ResearchMetadata",
    
    # Sweeps
    "SweepManifest",
    "SweepResult", 
    
    # Storage
    "ArtifactRef",
    "StorageConfig",
]