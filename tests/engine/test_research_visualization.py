"""
Tests for research-focused visualization system.
"""

import pytest
from pathlib import Path
import tempfile
import json

from src.engine.visualization import VisualizationService, HistogramRenderer
from src.engine.models import ArtifactRef


class TestResearchVisualizationService:
    """Test the clean visualization service."""
    
    def test_service_creation(self):
        """Test creating visualization service."""
        service = VisualizationService()
        assert len(service._renderers) == 0
        
    def test_renderer_registration(self):
        """Test registering renderers."""
        service = VisualizationService()
        renderer = HistogramRenderer()
        
        service.register_renderer(renderer)
        assert len(service._renderers) == 1
        
    def test_can_render_check(self):
        """Test visualization capability checking."""
        service = VisualizationService()
        service.register_renderer(HistogramRenderer())
        
        # Valid histogram data
        valid_data = {
            "analysis": {
                "measurement_results": {
                    "raw_counts": {"000": 500, "111": 500}
                }
            }
        }
        
        assert service.can_render("histogram", valid_data)
        assert not service.can_render("nonexistent", valid_data)
        assert not service.can_render("histogram", {})


class TestHistogramRenderer:
    """Test histogram renderer specifically."""
    
    def test_can_render_detection(self):
        """Test histogram renderer capability detection."""
        renderer = HistogramRenderer()
        
        # Valid data formats
        valid_formats = [
            {"analysis": {"measurement_results": {"raw_counts": {"000": 100}}}},
            {"analysis": {"measurement_results": {"outcome_probabilities": {"000": 0.5}}}},
            {"counts": {"000": 100, "111": 100}}
        ]
        
        for data in valid_formats:
            assert renderer.can_render("histogram", data)
            
        # Invalid data
        invalid_formats = [
            {},
            {"analysis": {}},
            {"analysis": {"measurement_results": {}}},
            {"counts": {}}
        ]
        
        for data in invalid_formats:
            assert not renderer.can_render("histogram", data)
            
    def test_histogram_rendering(self):
        """Test actual histogram rendering."""
        renderer = HistogramRenderer()
        
        # Create test data with research metrics
        data = {
            "analysis": {
                "measurement_results": {
                    "raw_counts": {"000": 400, "111": 500, "001": 50, "110": 74}
                },
                "experiment_parameters": {
                    "state_type": "GHZ",
                    "num_qubits": 3,
                    "noise_enabled": True,
                    "noise_type": "depolarizing",
                    "error_rate": 0.05
                }
            },
            "structured_decoherence_metrics": {
                "asymmetry_index": 0.245,
                "pathway_concentration_ratio": 3.2,
                "entanglement_error_correlation": 0.67
            }
        }
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "test_histogram.png"
            
            artifact = renderer.render(data, str(output_path))
            
            # Check artifact
            assert isinstance(artifact, ArtifactRef)
            assert artifact.kind == "histogram"
            assert artifact.path == str(output_path)
            assert "HistogramRenderer" in artifact.metadata["renderer"]
            assert artifact.metadata["experiment_type"] == "GHZ"
            assert artifact.metadata["has_research_metrics"] is True
            
            # Check file was created
            assert output_path.exists()
            assert output_path.stat().st_size > 0
            
    def test_histogram_without_research_metrics(self):
        """Test histogram rendering without research metrics."""
        renderer = HistogramRenderer()
        
        data = {
            "analysis": {
                "measurement_results": {
                    "raw_counts": {"00": 512, "11": 512}
                },
                "experiment_parameters": {
                    "state_type": "BELL",
                    "num_qubits": 2
                }
            }
        }
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "simple_histogram.png"
            
            artifact = renderer.render(data, str(output_path))
            
            assert isinstance(artifact, ArtifactRef)
            assert artifact.metadata["has_research_metrics"] is False
            assert output_path.exists()


class TestIntegration:
    """Test integration between service and renderers."""
    
    def test_end_to_end_rendering(self):
        """Test complete visualization workflow."""
        # Create service with histogram renderer
        service = VisualizationService()
        service.register_renderer(HistogramRenderer())
        
        # Create experiment-like data
        data = {
            "analysis": {
                "measurement_results": {
                    "raw_counts": {"000": 300, "111": 700}
                },
                "experiment_parameters": {
                    "state_type": "GHZ",
                    "num_qubits": 3
                }
            }
        }
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "integration_test.png"
            
            # Render through service
            artifact = service.render("histogram", data, str(output_path))
            
            assert isinstance(artifact, ArtifactRef)
            assert output_path.exists()
            
    def test_unsupported_visualization_type(self):
        """Test error handling for unsupported types."""
        service = VisualizationService()
        service.register_renderer(HistogramRenderer())
        
        data = {"counts": {"00": 100}}
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "test.png"
            
            with pytest.raises(ValueError, match="No renderer found"):
                service.render("unsupported_type", data, str(output_path))


def test_default_service_creation():
    """Test creating service with default renderers."""
    from src.engine.visualization.service import create_default_service
    
    service = create_default_service()
    assert len(service._renderers) >= 1
    
    # Should support histogram
    test_data = {"analysis": {"measurement_results": {"raw_counts": {"0": 1}}}}
    assert service.can_render("histogram", test_data)