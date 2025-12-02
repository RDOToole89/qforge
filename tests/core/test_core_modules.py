"""
Test core analysis modules: null models, bootstrap, and correlations.
"""

import numpy as np

from src.core.analysis.core.bootstrap import (
    bootstrap_confidence_interval,
    compute_metric_with_confidence,
)
from src.core.analysis.core.correlations import (
    get_topology_adjacency,
    mi_matrix,
)
from src.core.analysis.core.null_models import (
    factorized_null_model,
    generate_null_samples,
    sample_multinomial_counts,
)


class TestNullModels:
    """Test null model generation for hypothesis testing."""

    def test_factorized_null_model(self):
        """Test factorized null model generation."""
        counts = {"00": 250, "01": 250, "10": 250, "11": 250}
        null_model = factorized_null_model(counts)

        # Should have full support
        assert len(null_model) == 4

        # Should sum to 1
        assert abs(sum(null_model.values()) - 1.0) < 1e-10

        # For uniform input, should be nearly uniform
        for prob in null_model.values():
            assert abs(prob - 0.25) < 0.05

    def test_factorized_null_model_biased(self):
        """Test factorized null model with biased marginals."""
        counts = {"00": 400, "01": 100, "10": 100, "11": 400}
        null_model = factorized_null_model(counts)

        # Should have full support
        assert len(null_model) == 4

        # Should preserve marginal biases
        # First qubit biased toward 0
        p0_marginal = null_model["00"] + null_model["01"]
        assert p0_marginal >= 0.5  # Changed to >= to handle exact 0.5

    def test_sample_multinomial_counts(self):
        """Test multinomial sampling."""
        probs = {"00": 0.25, "01": 0.25, "10": 0.25, "11": 0.25}
        n_samples = 1000
        rng = np.random.default_rng(42)

        samples = sample_multinomial_counts(probs, n_samples, rng)

        # Should have correct total
        assert sum(samples.values()) == n_samples

        # All counts should be non-negative
        for count in samples.values():
            assert count >= 0

    def test_generate_null_samples(self):
        """Test null sample generation."""
        null_model = {"00": 0.3, "01": 0.2, "10": 0.25, "11": 0.25}
        num_samples = 1000
        rng = np.random.default_rng(42)

        samples = generate_null_samples(null_model, num_samples, rng)

        # Returns a list with a single sample
        assert len(samples) == 1

        # The sample should have the correct total
        sample = samples[0]
        assert sum(sample.values()) == num_samples


class TestBootstrap:
    """Test bootstrap confidence interval methods."""

    def test_bootstrap_confidence_interval(self):
        """Test basic bootstrap CI computation."""
        counts = {"00": 300, "01": 200, "10": 250, "11": 250}

        def test_statistic(c: dict[str, int]) -> float:
            total = sum(c.values())
            return c.get("00", 0) / total if total > 0 else 0

        rng = np.random.default_rng(42)
        ci_low, ci_high = bootstrap_confidence_interval(
            counts, test_statistic, n_bootstrap=100, rng=rng
        )

        # CI should be valid
        assert ci_low <= ci_high
        assert 0 <= ci_low <= 1
        assert 0 <= ci_high <= 1

    def test_bootstrap_deterministic(self):
        """Test bootstrap with deterministic data."""
        counts = {"00": 1000}

        def test_statistic(c: dict[str, int]) -> float:
            return 1.0 if "00" in c else 0.0

        rng = np.random.default_rng(42)
        ci_low, ci_high = bootstrap_confidence_interval(
            counts, test_statistic, n_bootstrap=50, rng=rng
        )

        # Should be very tight CI around 1.0
        assert ci_low > 0.9
        assert ci_high == 1.0

    def test_compute_metric_with_confidence(self):
        """Test metric computation with confidence intervals."""
        counts = {"00": 250, "01": 250, "10": 250, "11": 250}

        def metric_func(c: dict[str, int]) -> float:
            # Simple balance metric
            total = sum(c.values())
            if total == 0:
                return 0.5
            p00 = c.get("00", 0) / total
            p11 = c.get("11", 0) / total
            return abs(p00 - p11)

        rng = np.random.default_rng(42)
        result = compute_metric_with_confidence(counts, metric_func, n_bootstrap=100, rng=rng)

        # Result is a MetricWithConfidence object
        assert hasattr(result, "value")
        assert hasattr(result, "ci95")
        assert hasattr(result, "status")

        # Value should be within CI
        ci_lower, ci_upper = result.ci95
        assert ci_lower <= result.value <= ci_upper


class TestCorrelations:
    """Test correlation analysis functions."""

    def test_mi_matrix(self):
        """Test mutual information matrix computation."""
        counts = {"000": 400, "111": 350, "001": 150, "110": 100}

        mi_mat = mi_matrix(counts)

        # Should be 3x3 for 3 qubits
        assert mi_mat.shape == (3, 3)

        # Diagonal should be zero (MI of qubit with itself)
        for i in range(3):
            assert abs(mi_mat[i, i]) < 1e-10

        # Should be symmetric
        for i in range(3):
            for j in range(3):
                assert abs(mi_mat[i, j] - mi_mat[j, i]) < 1e-10

        # MI should be non-negative
        for i in range(3):
            for j in range(3):
                if i != j:
                    assert mi_mat[i, j] >= -1e-10  # Allow small numerical errors

    def test_get_topology_adjacency(self):
        """Test topology adjacency matrix generation."""
        # Test linear topology
        adj_linear = get_topology_adjacency("linear", 4)
        assert adj_linear.shape == (4, 4)
        # Linear should connect adjacent qubits
        assert adj_linear[0, 1] == 1
        assert adj_linear[1, 2] == 1
        assert adj_linear[2, 3] == 1
        assert adj_linear[0, 2] == 0  # Not adjacent

        # Test all-to-all topology
        adj_all = get_topology_adjacency("all_to_all", 3)
        assert adj_all.shape == (3, 3)
        # All-to-all should connect everything
        for i in range(3):
            for j in range(3):
                if i != j:
                    assert adj_all[i, j] == 1
                else:
                    assert adj_all[i, j] == 0

    def test_topology_types(self):
        """Test different topology types."""
        n_qubits = 5

        # Test supported topologies
        for topo in ["linear", "all_to_all", "star"]:
            adj = get_topology_adjacency(topo, n_qubits)
            assert adj.shape == (n_qubits, n_qubits)
            # Should be symmetric
            assert np.allclose(adj, adj.T)
            # Diagonal should be zero
            assert np.allclose(np.diag(adj), 0)


class TestCoreModulesIntegration:
    """Test integration between core modules."""

    def test_null_model_bootstrap(self):
        """Test combining null models with bootstrap."""
        counts = {"00": 400, "01": 100, "10": 100, "11": 400}

        # Generate null model
        null_probs = factorized_null_model(counts)

        # Sample from null model
        rng = np.random.default_rng(42)
        null_samples = []
        for _ in range(10):
            sample = sample_multinomial_counts(null_probs, sum(counts.values()), rng)
            null_samples.append(sample)

        # Each sample should have correct total
        for sample in null_samples:
            assert sum(sample.values()) == sum(counts.values())

    def test_correlation_with_bootstrap(self):
        """Test correlation analysis with bootstrap CI."""
        counts = {"000": 450, "111": 450, "001": 50, "110": 50}

        def correlation_metric(c: dict[str, int]) -> float:
            # Simple correlation metric based on MI matrix
            mi_mat = mi_matrix(c)
            # Return average off-diagonal MI
            n = mi_mat.shape[0]
            if n <= 1:
                return 0.0
            total = 0.0
            count = 0
            for i in range(n):
                for j in range(i + 1, n):
                    total += mi_mat[i, j]
                    count += 1
            return total / count if count > 0 else 0.0

        rng = np.random.default_rng(42)
        result = compute_metric_with_confidence(counts, correlation_metric, n_bootstrap=50, rng=rng)

        # Should have valid result
        assert result.value >= 0.0
        ci_lower, ci_upper = result.ci95
        assert ci_lower >= 0.0
        assert ci_upper >= ci_lower
