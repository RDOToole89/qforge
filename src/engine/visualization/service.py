"""Clean, extensible visualization service for research.

Plugin architecture allows adding new visualization types without
modifying core engine code.
"""

from __future__ import annotations

import logging
import threading
from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any

from src.engine.models import ArtifactRef

logger = logging.getLogger(__name__)


# --------------------------- Renderer Protocol ---------------------------


class VisualizationRenderer(ABC):
    """Abstract base class for visualization renderers.

    Renderers should be stateless (or at least reentrant) because the
    VisualizationService may call them from parallel sweep contexts.
    """

    #: Renderers with higher priority are selected first when multiple can render.
    #: Use this to make a specialized renderer outrank a generic fallback.
    priority: int = 0

    @property
    def name(self) -> str:
        """Human-readable name (defaults to class name)."""
        return self.__class__.__name__

    @abstractmethod
    def can_render(self, viz_type: str, data: dict[str, Any]) -> bool:
        """Return True if this renderer supports the visualization type and data."""
        raise NotImplementedError

    @abstractmethod
    def render(self, data: dict[str, Any], output_path: str) -> ArtifactRef:
        """Render visualization and return an ArtifactRef."""
        raise NotImplementedError

    def supported_types(self) -> Iterable[str]:
        """Return an iterable of visualization type strings this renderer handles.

        For example, {"histogram"}. Used for discovery. Optional override.
        """
        return ()


# --------------------------- Service & Registry ---------------------------


class RendererRegistryError(RuntimeError):
    """Raised for registry problems (duplicate, missing, etc.)."""


class VisualizationService:
    """Research-focused visualization service with plugin architecture.

    - Thread-safe renderer registry
    - Priority-based renderer selection
    - Helpful diagnostics when no renderer matches
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._renderers: list[VisualizationRenderer] = []

    # ----- Registry management -----

    def register_renderer(self, renderer: VisualizationRenderer) -> None:
        """Register a visualization renderer plugin.

        Guards against duplicate registration of the exact same instance.
        """
        if renderer is None:
            raise RendererRegistryError("renderer must not be None")

        with self._lock:
            if any(r is renderer for r in self._renderers):
                logger.debug("Renderer instance already registered: %s", renderer.name)
                return
            self._renderers.append(renderer)
            # Keep registry sorted by descending priority (high first), then name
            self._renderers.sort(key=lambda r: (-int(getattr(r, "priority", 0)), r.name))
            logger.debug(
                "Registered renderer: %s (priority=%s)",
                renderer.name,
                getattr(renderer, "priority", 0),
            )

    # ----- Discovery / selection -----

    def list_renderers(self) -> list[str]:
        """List registered renderer names in selection order."""
        with self._lock:
            return [r.name for r in self._renderers]

    def list_supported_types(self) -> list[str]:
        """Union of supported types reported by all renderers.

        Renderers that do not override `supported_types()` will contribute nothing here,
        but can still be selected via `can_render()`.
        """
        types: set[str] = set()
        with self._lock:
            for r in self._renderers:
                try:
                    for t in r.supported_types():
                        types.add(str(t))
                except Exception as e:
                    logger.debug("Renderer %s.supported_types() failed: %s", r.name, e)
        return sorted(types)

    def get_renderer(self, viz_type: str, data: dict[str, Any]) -> VisualizationRenderer | None:
        """Return the best renderer for (viz_type, data), or None if no match.

        Selection is priority-first, then registration order.
        """
        with self._lock:
            for r in self._renderers:
                try:
                    if r.can_render(viz_type, data):
                        return r
                except Exception as e:
                    logger.warning("Renderer %s.can_render() raised: %s", r.name, e)
        return None

    def can_render(self, viz_type: str, data: dict[str, Any]) -> bool:
        """True if any registered renderer can handle this visualization."""
        return self.get_renderer(viz_type, data) is not None

    # ----- Rendering -----

    def render(self, viz_type: str, data: dict[str, Any], output_path: str) -> ArtifactRef:
        """Render visualization using the highest-priority compatible renderer.

        Args:
            viz_type: Type of visualization (e.g., "histogram", "pathway_analysis")
            data: Experiment data (typically from ExperimentResult.model_dump())
            output_path: Where to save the visualization

        Returns:
            ArtifactRef pointing to saved visualization

        Raises:
            ValueError: If no renderer can handle the visualization type
        """
        renderer = self.get_renderer(viz_type, data)
        if renderer is None:
            msg = (
                f"No renderer found for visualization type '{viz_type}'. "
                f"Registered renderers (priority ↓): {self._describe_registry()} | "
                f"Supported types: {self.list_supported_types()}"
            )
            raise ValueError(msg)

        logger.info("Rendering %s with %s", viz_type, renderer.name)
        return renderer.render(data, output_path)

    def render_or_none(
        self, viz_type: str, data: dict[str, Any], output_path: str
    ) -> ArtifactRef | None:
        """Render visualization using the best renderer, returning None if no renderer matches.

        Useful for optional visualizations in pipelines.
        """
        try:
            return self.render(viz_type, data, output_path)
        except ValueError as e:
            logger.info("Visualization skipped: %s", e)
            return None

    # ----- Internals -----

    def _describe_registry(self) -> list[tuple[str, int]]:
        with self._lock:
            return [(r.name, int(getattr(r, "priority", 0))) for r in self._renderers]


# --------------------------- Convenience factory ---------------------------


def create_default_service() -> VisualizationService:
    """Create a visualization service with default research renderers.

    Add new renderers here or register them at runtime in your pipeline.
    """
    from .renderers import (  # local import to avoid import cycles
        CircuitDiagramRenderer,
        CorrelationRenderer,
        DensityMatrixRenderer,
        HistogramRenderer,
    )

    service = VisualizationService()
    service.register_renderer(HistogramRenderer())
    service.register_renderer(DensityMatrixRenderer())
    service.register_renderer(CorrelationRenderer())
    service.register_renderer(CircuitDiagramRenderer())
    return service
