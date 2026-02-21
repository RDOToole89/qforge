"""
Research-focused visualization system for structured decoherence studies.

This package provides clean, extensible visualization capabilities with a
plugin architecture:

- Thread-safe renderer registry
- Priority-based renderer selection (most specific wins)
- Optional rendering via `VisualizationService.render_or_none(...)`
- Easy capability discovery with `VisualizationService.list_supported_types()`

Typical usage:
    from src.engine.visualization import create_default_service
    service = create_default_service()
    artifact = service.render_or_none("histogram", result.model_dump(), "out/hist.png")
"""

from __future__ import annotations

from .export import save_figure
from .renderers import (
    CircuitDiagramRenderer,
    CorrelationRenderer,
    DensityMatrixRenderer,
    HistogramRenderer,
)
from .service import (
    RendererRegistryError,
    VisualizationRenderer,
    VisualizationService,
    create_default_service,
)

__all__ = [
    "VisualizationService",
    "VisualizationRenderer",
    "RendererRegistryError",
    "HistogramRenderer",
    "DensityMatrixRenderer",
    "CorrelationRenderer",
    "CircuitDiagramRenderer",
    "save_figure",
    "create_default_service",
]
