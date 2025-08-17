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

from .service import (
    VisualizationService,
    VisualizationRenderer,
    RendererRegistryError,
    create_default_service,
)
from .renderers import HistogramRenderer

__all__ = [
    "VisualizationService",
    "VisualizationRenderer",
    "RendererRegistryError",
    "HistogramRenderer",
    "create_default_service",
]
