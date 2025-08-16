"""
Research-focused visualization system for structured decoherence studies.

This module provides clean, extensible visualization capabilities optimized
for quantum decoherence pathway research with plugin architecture.
"""

from .service import VisualizationService, VisualizationRenderer, create_default_service
from .renderers import HistogramRenderer

__all__ = [
    "VisualizationService",
    "VisualizationRenderer", 
    "HistogramRenderer",
    "create_default_service"
]