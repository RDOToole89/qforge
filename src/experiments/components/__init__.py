"""
Experiment Component Building Blocks

This module provides reusable, composable components for building quantum experiments.
Components can be mixed and matched to create complex experimental setups.

Building Blocks:
- Base classes for experiments and components
- Mixins for common functionality (noise, analysis, visualization)
- Parameter validation and transformation pipelines
- Metadata and versioning systems
"""

from .base import BaseExperiment, ExperimentComponent
from .mixins import NoiseMixin, AnalysisMixin, VisualizationMixin, ResearchMixin
from .validators import ParameterValidator, ConfigurationValidator
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

    # Validators
    "ParameterValidator",
    "ConfigurationValidator",

    # Metadata
    "ExperimentMetadata",
    "ComponentMetadata",
]
