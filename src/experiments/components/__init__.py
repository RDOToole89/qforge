"""
Experiment Component Building Blocks

This module provides reusable, composable components for building quantum experiments.
Components can be mixed and matched to create complex experimental setups.

Building Blocks:
- Base classes for experiments and components  
- Mixins for common functionality (noise, analysis, visualization)
- Metadata and versioning systems
- Version-agnostic schema integration for validation

All validation is now handled by the unified validation system in validation.py.
"""

from .base import BaseExperiment, ExperimentComponent
from .mixins import NoiseMixin, AnalysisMixin, VisualizationMixin, ResearchMixin
from .metadata import ExperimentMetadata, ComponentMetadata

__all__ = [
    # Base classes
    "BaseExperiment",
    "ExperimentComponent",

    # Mixins
    "NoiseMixin",
    "AnalysisMixin", 
    "VisualizationMixin",
    "ResearchMixin",

    # Metadata
    "ExperimentMetadata",
    "ComponentMetadata",
]
