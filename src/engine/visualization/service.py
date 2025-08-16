"""
Clean, extensible visualization service for research.

Plugin architecture allows adding new visualization types without
modifying core engine code.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

from src.engine.models import ArtifactRef

logger = logging.getLogger(__name__)


class VisualizationRenderer(ABC):
    """Abstract base class for visualization renderers."""
    
    @abstractmethod
    def can_render(self, viz_type: str, data: Dict[str, Any]) -> bool:
        """Check if this renderer supports the visualization type and data."""
        pass
        
    @abstractmethod
    def render(self, data: Dict[str, Any], output_path: str) -> ArtifactRef:
        """Render visualization and return artifact reference."""
        pass


class VisualizationService:
    """
    Research-focused visualization service with plugin architecture.
    
    Designed for structured decoherence studies but extensible
    for any quantum experiment visualization needs.
    """
    
    def __init__(self):
        self._renderers: List[VisualizationRenderer] = []
        
    def register_renderer(self, renderer: VisualizationRenderer) -> None:
        """Register a visualization renderer plugin."""
        self._renderers.append(renderer)
        logger.debug(f"Registered renderer: {renderer.__class__.__name__}")
        
    def can_render(self, viz_type: str, data: Dict[str, Any]) -> bool:
        """Check if any registered renderer can handle this visualization."""
        return any(renderer.can_render(viz_type, data) for renderer in self._renderers)
        
    def render(self, viz_type: str, data: Dict[str, Any], output_path: str) -> ArtifactRef:
        """
        Render visualization using appropriate renderer.
        
        Args:
            viz_type: Type of visualization (e.g., "histogram", "pathway_analysis")
            data: Experiment data (typically from ExperimentResult.model_dump())
            output_path: Where to save the visualization
            
        Returns:
            ArtifactRef pointing to saved visualization
            
        Raises:
            ValueError: If no renderer can handle the visualization type
        """
        for renderer in self._renderers:
            if renderer.can_render(viz_type, data):
                logger.info(f"Rendering {viz_type} with {renderer.__class__.__name__}")
                return renderer.render(data, output_path)
                
        raise ValueError(
            f"No renderer found for visualization type '{viz_type}'. "
            f"Available renderers: {[r.__class__.__name__ for r in self._renderers]}"
        )
        
    def list_supported_types(self) -> List[str]:
        """List all visualization types supported by registered renderers."""
        # This is a simple implementation - could be more sophisticated
        types = []
        test_data = {"counts": {}, "structured_decoherence_metrics": {}}
        
        common_types = ["histogram", "pathway_analysis", "metrics_comparison", "threshold_study"]
        for viz_type in common_types:
            if self.can_render(viz_type, test_data):
                types.append(viz_type)
                
        return types


def create_default_service() -> VisualizationService:
    """Create visualization service with default research renderers."""
    from .renderers import HistogramRenderer
    
    service = VisualizationService()
    service.register_renderer(HistogramRenderer())
    
    return service