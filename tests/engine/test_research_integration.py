"""
Tests for research integration module.

Validates the bridge between engine and core analysis modules.
"""

import pytest
from typing import Dict

from src.engine.models.config import ExperimentConfig
from src.engine.analysis.research_integration import (
    compute_research_metrics,
    extract_counts_from_result,
)


class TestResearchIntegration:
    """Test research integration functionality."""
    
    def test_extract_counts_from_dict(self):
        """Test extracting counts from dictionary format."""
        # Simulate qiskit result format
        mock_counts = {"000": 100, "111": 200}
        result = {"counts": mock_counts}
        
        extracted = extract_counts_from_result(result)
        
        assert extracted == mock_counts
    
    def test_compute_research_metrics_disabled(self):
        """Test that no metrics are computed when disabled."""
        config = ExperimentConfig(
            num_qubits=3,
            state_type="GHZ",
            enable_research_metrics=False
        )
        counts = {"000": 100, "111": 200}
        
        result = compute_research_metrics(counts, config)
        
        assert result is None
    
    def test_compute_research_metrics_wrong_type(self):
        """Test that no metrics are computed for wrong research type."""
        config = ExperimentConfig(
            num_qubits=3,
            state_type="GHZ",
            enable_research_metrics=True,
            research_type="parameter_sweep"  # Not structured_decoherence
        )
        counts = {"000": 100, "111": 200}
        
        result = compute_research_metrics(counts, config)
        
        assert result is None
    
    def test_compute_research_metrics_success(self):
        """Test successful computation of research metrics."""
        config = ExperimentConfig(
            num_qubits=3,
            state_type="GHZ",
            enable_research_metrics=True,
            research_type="structured_decoherence",
            noise_enabled=True,
            noise_type="depolarizing",
            error_rate=0.05
        )
        counts = {"000": 400, "111": 500, "001": 50, "110": 74}
        
        result = compute_research_metrics(counts, config)
        
        assert result is not None
        assert result.asymmetry_index >= 0
        assert result.pathway_concentration_ratio >= 0
        assert -1 <= result.entanglement_error_correlation <= 1
        assert result.temporal_pathway_stability is None  # Single experiment
        assert result.complexity_emergence_score is None  # Single experiment
        
        # Check metadata
        assert result.metadata.state_type == "GHZ"
        assert result.metadata.num_qubits == 3
        assert result.metadata.total_shots == 1024
        assert result.metadata.unique_outcomes == 4
        assert result.metadata.noise_conditions is not None
        
        # Check pathway analysis
        assert len(result.pathway_analysis.dominant_pathways) <= 5
        assert result.pathway_analysis.total_outcomes == 4
        assert result.pathway_analysis.measurement_shots == 1024
    
    def test_compute_research_metrics_empty_counts(self):
        """Test behavior with empty counts."""
        config = ExperimentConfig(
            num_qubits=3,
            state_type="GHZ",
            enable_research_metrics=True,
            research_type="structured_decoherence"
        )
        counts = {}
        
        result = compute_research_metrics(counts, config)
        
        assert result is None
    
    def test_noise_conditions_extraction(self):
        """Test extraction of noise conditions."""
        config = ExperimentConfig(
            num_qubits=3,
            state_type="GHZ",
            enable_research_metrics=True,
            research_type="structured_decoherence",
            noise_enabled=True,
            noise_type="thermal_relaxation",
            error_rate=0.1,
            t1=50.0,
            t2=30.0
        )
        counts = {"000": 512, "111": 512}
        
        result = compute_research_metrics(counts, config)
        
        assert result is not None
        noise_conditions = result.metadata.noise_conditions
        assert noise_conditions["noise_type"] == "thermal_relaxation"
        assert noise_conditions["error_rate"] == 0.1
        assert noise_conditions["t1"] == 50.0
        assert noise_conditions["t2"] == 30.0


class TestPathwayAnalysisQuality:
    """Test quality of pathway analysis."""
    
    def test_pathway_analysis_qualitative_assessments(self):
        """Test qualitative assessment accuracy."""
        config = ExperimentConfig(
            num_qubits=3,
            state_type="GHZ",
            enable_research_metrics=True,
            research_type="structured_decoherence"
        )
        
        # High concentration case
        high_concentration_counts = {"000": 900, "111": 100, "001": 20, "110": 4}
        result = compute_research_metrics(high_concentration_counts, config)
        
        assert result is not None
        assert result.pathway_analysis.pathway_concentration in ["high", "very_high"]
        assert result.pathway_concentration_ratio > 2.0
        
        # Low concentration case (more uniform)
        uniform_counts = {"000": 256, "111": 256, "001": 256, "110": 256}
        result = compute_research_metrics(uniform_counts, config)
        
        assert result is not None
        assert result.pathway_concentration_ratio <= 2.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])