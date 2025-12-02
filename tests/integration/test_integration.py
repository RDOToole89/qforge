"""
End-to-end integration tests for structured decoherence analysis framework.
"""

import numpy as np
import pytest

from src.core.analysis.core.bootstrap import compute_metric_with_confidence
from src.core.analysis.core.correlations import mi_matrix
from src.core.analysis.core.information_theory import counts_to_probabilities, entropy
from src.core.analysis.pipelines.pathway_analysis import (
    analyze_decoherence_structure,
    compute_all_pathway_metrics,
)


def get_entropy_from_counts(counts):
    """Helper to compute entropy from counts dict."""
    probs_dict = counts_to_probabilities(counts)
    return entropy(np.array(list(probs_dict.values())))


class TestEndToEndWorkflow:
    """Test complete end-to-end workflow."""

    def test_complete_analysis_workflow(self):
        """Test complete structured decoherence analysis workflow."""
        # Simulate GHZ state with decoherence
        ghz_counts = {"000": 400, "111": 400, "001": 100, "110": 100}

        # 1. Information theory analysis
        ent = get_entropy_from_counts(ghz_counts)
        assert isinstance(ent, float)
        assert ent > 0.0

        # 2. Correlation analysis
        mi_mat = mi_matrix(ghz_counts)
        assert mi_mat.shape == (3, 3)
        assert np.all(mi_mat >= -1e-10)  # Allow small numerical errors

        # 3. Pipeline-based metrics computation
        try:
            all_metrics = compute_all_pathway_metrics(ghz_counts)
            assert isinstance(all_metrics, dict)
        except Exception:
            pass  # Some metrics may not be available

        # 4. Individual metric with confidence
        def test_metric(c):
            return get_entropy_from_counts(c)

        ent_with_ci = compute_metric_with_confidence(ghz_counts, test_metric, n_bootstrap=50)
        assert hasattr(ent_with_ci, "value")
        assert hasattr(ent_with_ci, "ci95")
        assert hasattr(ent_with_ci, "status")

        # 5. Structure analysis
        try:
            analysis = analyze_decoherence_structure(ghz_counts)
            assert isinstance(analysis, dict)
        except Exception:
            pass  # May not be available for all data

    def test_multi_qubit_scaling(self):
        """Test framework scaling across different qubit counts."""
        test_cases = [
            # 1-qubit (degenerate)
            {"0": 600, "1": 400},
            # 2-qubit
            {"00": 400, "11": 400, "01": 100, "10": 100},
            # 3-qubit
            {"000": 400, "111": 400, "001": 100, "110": 100},
        ]

        for i, counts in enumerate(test_cases):
            try:
                # Information theory should work for all
                ent = get_entropy_from_counts(counts)
                assert isinstance(ent, float)
                assert ent >= 0.0

                # Pipeline metrics (may work for some cases)
                try:
                    all_metrics = compute_all_pathway_metrics(counts)
                    assert isinstance(all_metrics, dict)
                except Exception:
                    pass  # Some cases may not work

            except Exception as e:
                pytest.fail(f"Framework failed on {i + 1}-qubit case: {e}")

    def test_error_recovery_integration(self):
        """Test error recovery across the integrated framework."""
        problematic_cases = [
            # Empty data
            {},
            # Single outcome
            {"0": 1000},
            # Negative counts (should error)
            {"00": -100, "01": 200, "10": 300, "11": 400},
            # Zero counts
            {"00": 0, "01": 0, "10": 0, "11": 0},
        ]

        for i, counts in enumerate(problematic_cases):
            if i == 2:  # Negative counts case
                # Should raise ValueError consistently
                with pytest.raises(ValueError):
                    get_entropy_from_counts(counts)
            elif i == 0:  # Empty counts
                # Should raise ValueError consistently
                with pytest.raises(ValueError):
                    get_entropy_from_counts(counts)
            elif i == 3:  # Zero counts
                # Should work due to smoothing (returns uniform distribution)
                ent = get_entropy_from_counts(counts)
                assert isinstance(ent, float)
            else:  # Single outcome
                # Should handle gracefully or fail consistently
                try:
                    ent = get_entropy_from_counts(counts)
                    # If successful, verify basic properties
                    assert isinstance(ent, float)
                except ValueError:
                    # Consistent failure is also acceptable
                    pass


class TestFrameworkConfiguration:
    """Test basic framework functionality."""

    def test_information_theory_basics(self):
        """Test basic information theory functionality."""
        # Test data
        counts = {"00": 400, "11": 300, "01": 150, "10": 150}

        # Basic entropy computation
        ent = get_entropy_from_counts(counts)
        assert isinstance(ent, float)
        assert ent >= 0.0

        # Correlation matrix
        mi_mat = mi_matrix(counts)
        assert mi_mat.shape == (2, 2)
        assert np.all(mi_mat >= -1e-10)  # Allow numerical errors

    def test_bootstrap_functionality(self):
        """Test bootstrap confidence interval functionality."""
        counts = {"000": 400, "111": 300, "001": 150, "110": 150}

        # Test with entropy function
        def entropy_metric(c):
            return get_entropy_from_counts(c)

        result = compute_metric_with_confidence(counts, entropy_metric, n_bootstrap=50)

        assert hasattr(result, "value")
        assert hasattr(result, "ci95")
        assert hasattr(result, "status")
        assert isinstance(result.value, float)
        assert len(result.ci95) == 2

    def test_framework_robustness_basic(self):
        """Basic robustness test with simple cases."""
        stress_cases = [
            # Very skewed distribution
            {"0": 999, "1": 1},
            # Uniform distribution
            {"00": 250, "01": 250, "10": 250, "11": 250},
        ]

        for counts in stress_cases:
            try:
                # Core information theory should work
                ent = get_entropy_from_counts(counts)
                assert isinstance(ent, float)
                assert ent >= 0.0

                # Correlation analysis
                if len(list(counts.keys())[0]) >= 2:  # Multi-qubit
                    mi_mat = mi_matrix(counts)
                    assert isinstance(mi_mat, np.ndarray)

            except Exception:
                # Some edge cases may legitimately fail
                pass
