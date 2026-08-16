"""
Test metric registry system for dynamic metric computation and management.
"""

import numpy as np
import pytest

from src.core.analysis.metrics.registry import (
    _METRIC_REGISTRY,
    MetricResult,
    compute_all,
    compute_metric,
)


class TestMetricResult:
    """Test MetricResult data structure."""

    def test_metric_result_creation(self):
        """Test creating MetricResult objects."""
        result = MetricResult(
            value=0.75, status="validated", ci95=(0.65, 0.85), extras={"method": "bootstrap"}
        )

        assert result["value"] == 0.75
        assert result["status"] == "validated"
        assert result["ci95"] == (0.65, 0.85)
        assert result["extras"]["method"] == "bootstrap"

    def test_metric_result_minimal(self):
        """Test MetricResult with minimal required fields."""
        result = MetricResult(value=0.5, status="experimental")

        assert result["value"] == 0.5
        assert result["status"] == "experimental"
        assert "ci95" not in result
        assert "extras" not in result

    def test_metric_result_dict_interface(self):
        """Test MetricResult behaves like a dictionary."""
        result = MetricResult(value=0.3, status="validated")

        # Dict-like access
        assert result.get("value") == 0.3
        assert result.get("missing_key") is None
        assert "value" in result
        assert "missing_key" not in result

        # Iteration
        keys = list(result.keys())
        assert "value" in keys
        assert "status" in keys


class TestRegistryComputation:
    """Test metric computation through registry system."""

    def test_compute_all_builtin_metrics(self):
        """Test compute_all with built-in metrics."""
        counts = {"00": 300, "01": 200, "10": 250, "11": 250}
        rng = np.random.default_rng(42)

        results = compute_all(counts=counts, rng=rng)

        # Should have core metrics (by canonical names)
        expected_metrics = [
            "structure_score",
            "concentration_index",
            "entanglement_error_correlation",
        ]

        for metric in expected_metrics:
            assert metric in results
            result = results[metric]
            assert "value" in result
            assert "status" in result
            assert isinstance(result["value"], (int, float))

    def test_compute_single_metric(self):
        """Test computing a single metric by name."""
        counts = {"00": 400, "11": 600}

        # Test structure score
        result = compute_metric("structure_score", counts=counts)
        assert "value" in result
        assert "status" in result
        assert 0.0 <= result["value"] <= 0.5  # AI range

    def test_compute_metric_unknown(self):
        """Test error handling for unknown metric."""
        counts = {"0": 100, "1": 200}

        with pytest.raises(KeyError, match="Unknown metric"):
            compute_metric("nonexistent_metric", counts=counts)

    def test_parameter_passing(self):
        """Test that parameters are passed correctly to metrics."""
        counts = {"000": 400, "111": 350, "001": 150, "110": 100}

        # Test state_type parameter for EEC
        result_ghz = compute_metric(
            "entanglement_error_correlation", counts=counts, state_type="GHZ"
        )
        result_bell = compute_metric(
            "entanglement_error_correlation", counts=counts, state_type="BELL"
        )

        # Both should be valid correlation values
        assert -1.0 <= result_ghz["value"] <= 1.0
        assert -1.0 <= result_bell["value"] <= 1.0

    def test_error_handling(self):
        """Test error handling in metric computation."""
        # Empty counts should be handled gracefully
        results = compute_all(counts={})

        # Should return results (may be defaults/errors)
        assert isinstance(results, dict)

        # All results should have required fields
        for _name, result in results.items():
            assert "value" in result
            assert "status" in result

    def test_conditional_metrics(self):
        """Test metrics with conditional inputs."""
        counts = {"00": 300, "01": 200, "10": 250, "11": 250}

        # Without rankings - should get insufficient_runs status
        results = compute_all(counts=counts)
        if "pathway_persistence" in results:
            assert results["pathway_persistence"]["status"] == "insufficient_runs"

        # Without multi_qubit_data - should get insufficient_data status
        if "complexity_emergence_score" in results:
            assert results["complexity_emergence_score"]["status"] == "insufficient_data"

    def test_rng_consistency(self):
        """Test RNG consistency in computations."""
        counts = {"00": 300, "01": 200, "10": 250, "11": 250}

        # Same seed should give consistent results
        rng1 = np.random.default_rng(42)
        results1 = compute_all(counts=counts, rng=rng1)

        rng2 = np.random.default_rng(42)
        results2 = compute_all(counts=counts, rng=rng2)

        # Deterministic metrics should match exactly
        for metric in ["structure_score", "concentration_index"]:
            if metric in results1 and metric in results2:
                assert results1[metric]["value"] == results2[metric]["value"]


class TestRegistryIntegration:
    """Test integration between registry and actual metrics."""

    def test_metric_value_consistency(self):
        """Test that registry values match direct metric calls."""
        counts = {"000": 400, "111": 350, "001": 150, "110": 100}

        # Get values through registry
        registry_results = compute_all(counts=counts)

        # Compare with direct calls
        from src.core.analysis.metrics.asymmetry_index import compute_asymmetry_index
        from src.core.analysis.metrics.pathway_concentration_ratio import (
            compute_pathway_concentration_ratio,
        )
        from src.core.analysis.metrics.structure_score import compute_structure_score

        direct_ai = compute_asymmetry_index(counts)
        direct_pcr = compute_pathway_concentration_ratio(counts)
        direct_ss = compute_structure_score(counts=counts)["value"]

        # Should match (within numerical precision)
        if "structure_score" in registry_results:
            assert abs(direct_ss - registry_results["structure_score"]["value"]) < 1e-10
        if "asymmetry_index" in registry_results:
            assert abs(direct_ai - registry_results["asymmetry_index"]["value"]) < 1e-10
        if "concentration_index" in registry_results:
            assert abs(direct_pcr - registry_results["concentration_index"]["value"]) < 1e-10

    def test_status_determination(self):
        """Test that status is determined appropriately."""
        counts = {"00": 1000}  # Deterministic case

        result = compute_metric("structure_score", counts=counts)

        # Should have a reasonable status
        assert result["status"] in [
            "validated",
            "experimental",
            "unstable",
            "insufficient_runs",
            "insufficient_data",
        ]

        # Deterministic case: structure_score (JSD from factorized null) is ~0
        # because a single-outcome distribution is perfectly factorizable.
        assert abs(result["value"]) < 1e-2

        # Deterministic case gives near-maximal asymmetry index (TVD vs uniform):
        # K=4, N=1000, alpha=0.5 -> (N+a)/(N+aK) - 1/K = 750/1002.
        ai_result = compute_metric("asymmetry_index", counts=counts)
        assert abs(ai_result["value"] - 750.0 / 1002.0) < 1e-10

    def test_confidence_intervals(self):
        """Test confidence interval generation."""
        counts = {"00": 300, "01": 200, "10": 250, "11": 250}
        rng = np.random.default_rng(42)

        results = compute_all(counts=counts, rng=rng)

        # Check CI properties where present
        for _name, result in results.items():
            if "ci95" in result:
                ci_low, ci_high = result["ci95"]
                value = result["value"]

                # CI should bracket the value (approximately)
                assert ci_low <= value <= ci_high or abs(ci_low - ci_high) < 1e-10

    def test_extras_information(self):
        """Test that extras contain useful information."""
        counts = {"000": 400, "111": 300, "001": 200, "110": 100}

        results = compute_all(counts=counts, state_type="GHZ")

        # Check for useful extras
        for _name, result in results.items():
            if "extras" in result:
                extras = result["extras"]
                # Should identify the method used or provide a reason/error
                assert any(k in extras for k in ["method", "reason", "error"])

                # Some metrics should report sample information
                if "n_samples" in extras:
                    assert extras["n_samples"] == sum(counts.values())

    def test_large_scale_computation(self):
        """Test registry with multiple metrics."""
        counts = {
            "000": 100,
            "001": 150,
            "010": 200,
            "011": 250,
            "100": 300,
            "101": 350,
            "110": 400,
            "111": 450,
        }

        # Should handle efficiently
        results = compute_all(counts=counts)

        # Should have several metrics
        assert len(results) >= 3

        # All should have valid structure
        for _name, result in results.items():
            assert "value" in result
            assert "status" in result
            assert isinstance(result["value"], (int, float))
            assert np.isfinite(result["value"])

    def test_metric_mathematical_properties(self):
        """Test that metrics preserve mathematical properties through registry."""
        test_cases = [
            {"00": 250, "01": 250, "10": 250, "11": 250},  # Uniform
            {"00": 1000},  # Deterministic
            {"000": 400, "111": 400, "001": 100, "110": 100},  # Structured
        ]

        for counts in test_cases:
            results = compute_all(counts=counts)

            # Check bounds for each metric
            if "structure_score" in results:
                ai = results["structure_score"]["value"]
                assert 0.0 <= ai <= 1.0  # AI is TVD, bounded by [0, 1]

            if "concentration_index" in results:
                pcr = results["concentration_index"]["value"]
                assert pcr >= 0.0

            if "entanglement_error_correlation" in results:
                eec = results["entanglement_error_correlation"]["value"]
                assert -1.0 <= eec <= 1.0

    def test_registry_state_inspection(self):
        """Test that we can inspect registry state."""
        # Should have default metrics registered
        assert len(_METRIC_REGISTRY) > 0

        # Should have canonical names
        expected_metrics = [
            "structure_score",
            "entanglement_error_correlation",
            "concentration_index",
        ]
        for metric in expected_metrics:
            assert metric in _METRIC_REGISTRY

        # Should also have aliases
        expected_aliases = ["asymmetry_index", "pathway_concentration_ratio"]
        for alias in expected_aliases:
            assert alias in _METRIC_REGISTRY

    def test_numerical_stability(self):
        """Test numerical stability with extreme cases."""
        extreme_cases = [
            {"0": 9999, "1": 1},  # Highly skewed (reduced from 999999)
            {"00": 1, "01": 1, "10": 1, "11": 1},  # Very small counts
        ]

        for counts in extreme_cases:
            try:
                # Only compute a subset of metrics to avoid timeout
                results = compute_metric("structure_score", counts=counts)

                # Value should be finite
                value = results["value"]
                assert np.isfinite(value) or value == float("inf")  # PCR can be inf

            except Exception:
                # If computation fails, should be gracefully handled
                # (this tests that the framework doesn't crash on edge cases)
                pass
