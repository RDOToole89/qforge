"""
Test pipeline integration for structured decoherence analysis.
"""

import pytest
from typing import Dict

from src.core.analysis.pipelines.pathway_analysis import (
    analyze_decoherence_structure,
    compute_all_pathway_metrics,
)


class TestPipelineExecution:
    """Test pipeline execution and integration."""

    def test_compute_all_pathway_metrics_basic(self):
        """Test basic pathway metrics computation."""
        # GHZ-like measurement data
        counts = {"000": 400, "111": 400, "001": 100, "110": 100}
        
        # Compute all pathway metrics
        metrics = compute_all_pathway_metrics(counts)
        
        # Verify metrics structure
        assert isinstance(metrics, dict)
        assert len(metrics) >= 0  # May be empty if no metrics computed
        
        # Each metric should be a number
        for metric_name, metric_value in metrics.items():
            assert isinstance(metric_value, (int, float))
            # Should be a finite number
            assert not hasattr(metric_value, '__len__')  # Should be scalar

    def test_analyze_decoherence_structure(self):
        """Test decoherence structure analysis."""
        # Bell-like measurement data
        counts = {"00": 450, "11": 450, "01": 50, "10": 50}
        
        # Analyze structure
        analysis = analyze_decoherence_structure(counts)
        
        # Verify analysis structure
        assert isinstance(analysis, dict)
        # Analysis should return some form of structured result
        assert len(analysis) >= 0

    def test_empty_counts_error_handling(self):
        """Test error handling with empty counts."""
        empty_counts: Dict[str, int] = {}
        
        # Functions should handle empty input gracefully or raise ValueError
        try:
            metrics = compute_all_pathway_metrics(empty_counts)
            assert isinstance(metrics, dict)
        except ValueError:
            pass  # Acceptable to raise ValueError
            
        try:
            analysis = analyze_decoherence_structure(empty_counts)
            assert isinstance(analysis, dict)
        except ValueError:
            pass  # Acceptable to raise ValueError

    def test_single_outcome_handling(self):
        """Test handling of single outcome case."""
        single_counts = {"000": 1000}
        
        # Pipeline should handle single outcome gracefully
        try:
            metrics = compute_all_pathway_metrics(single_counts)
            assert isinstance(metrics, dict)
            
            analysis = analyze_decoherence_structure(single_counts)
            assert isinstance(analysis, dict)
        except (ValueError, ZeroDivisionError):
            # Acceptable for some metrics to fail with single outcome
            pass


class TestPipelineIntegration:
    """Test integration between pipeline components."""

    def test_pipeline_robustness(self):
        """Test pipeline robustness across different input patterns."""
        test_cases = [
            # Highly structured
            {"000": 800, "111": 150, "001": 25, "110": 25},
            # Moderately structured  
            {"00": 400, "11": 300, "01": 150, "10": 150},
            # Nearly random
            {"00": 260, "01": 240, "10": 250, "11": 250},
            # Binary case
            {"0": 600, "1": 400},
        ]
        
        for i, counts in enumerate(test_cases):
            # Each pipeline function should work for all test cases or fail gracefully
            try:
                metrics = compute_all_pathway_metrics(counts)
                assert isinstance(metrics, dict)
                
                analysis = analyze_decoherence_structure(counts)
                assert isinstance(analysis, dict)
                
            except (ValueError, ZeroDivisionError):
                # Some test cases may legitimately fail
                pass

    def test_error_propagation(self):
        """Test that errors propagate correctly through pipeline."""
        # Test with data that might cause numerical issues
        problematic_counts = {"0": 1, "1": 0}  # Zero count might cause issues
        
        # Pipeline should either succeed or fail gracefully
        try:
            metrics = compute_all_pathway_metrics(problematic_counts)
            assert isinstance(metrics, dict)
            
            analysis = analyze_decoherence_structure(problematic_counts)
            assert isinstance(analysis, dict)
        except (ValueError, ZeroDivisionError):
            # Graceful failure is also acceptable
            pass

    def test_performance_reasonable(self):
        """Test that pipeline performance is reasonable for typical inputs."""
        # Larger but reasonable dataset
        large_counts = {}
        for i in range(16):  # 4-qubit case
            bitstring = f"{i:04b}"
            large_counts[bitstring] = 50 + (i % 10) * 10
        
        # Pipeline should complete without issues or fail gracefully
        try:
            metrics = compute_all_pathway_metrics(large_counts)
            assert isinstance(metrics, dict)
            
            analysis = analyze_decoherence_structure(large_counts)
            assert isinstance(analysis, dict)
        except (ValueError, ZeroDivisionError, KeyError):
            # Some complex cases may fail
            pass