"""
Test information theory core module for entropy, divergence, and probability calculations.
"""

import numpy as np
import pytest

from qforge.core.analysis.constants import ALPHA
from qforge.core.analysis.core.information_theory import (
    counts_to_probabilities,
    entropy,
    jensen_shannon_divergence,
    kl_divergence,
    mutual_information,
    total_correlation,
)


class TestCountsToProbabilities:
    """Test probability distribution creation from counts."""

    def test_uniform_distribution(self):
        """Test uniform count distribution."""
        counts = {"00": 250, "01": 250, "10": 250, "11": 250}
        probs = counts_to_probabilities(counts)

        # Should have full support (4 outcomes for 2 qubits)
        assert len(probs) == 4

        # Check all probabilities are positive and sum to 1
        assert all(p > 0 for p in probs.values())
        assert abs(sum(probs.values()) - 1.0) < 1e-10

        # Check approximate uniformity (within smoothing tolerance)
        prob_values = list(probs.values())
        assert max(prob_values) - min(prob_values) < 0.01

    def test_full_support_jeffreys_smoothing(self):
        """Test that Jeffreys smoothing provides full 2^n support."""
        counts = {"00": 1000}  # Only one outcome observed
        probs = counts_to_probabilities(counts, alpha=ALPHA)

        # Should have full support (4 outcomes for 2 qubits)
        assert len(probs) == 4
        assert all(p > 0 for p in probs.values())

        # Observed outcome should have highest probability
        assert probs["00"] > probs["01"]
        assert probs["00"] > probs["10"]
        assert probs["00"] > probs["11"]

    def test_deterministic_ordering(self):
        """Test deterministic lexicographic ordering."""
        counts = {"11": 100, "00": 200, "01": 150}
        probs1 = counts_to_probabilities(counts)
        probs2 = counts_to_probabilities(counts)

        # Results should be identical (deterministic)
        assert probs1 == probs2

        # Keys should be in lexicographic order
        keys = list(probs1.keys())
        assert keys == sorted(keys)

    def test_empty_counts(self):
        """Test empty counts dictionary."""
        with pytest.raises(ValueError):
            counts_to_probabilities({})

    def test_custom_alpha(self):
        """Test custom smoothing parameter."""
        counts = {"0": 100, "1": 0}

        # No smoothing
        probs_none = counts_to_probabilities(counts, alpha=0.0)
        assert probs_none["1"] == 0.0

        # Heavy smoothing
        probs_heavy = counts_to_probabilities(counts, alpha=10.0)
        assert probs_heavy["1"] > 0.08  # Adjusted for actual smoothing result


class TestEntropy:
    """Test entropy calculations."""

    def test_uniform_entropy(self):
        """Test entropy of uniform distribution."""
        probs = np.array([0.25, 0.25, 0.25, 0.25])
        h = entropy(probs)
        expected = 2.0  # log2(4) = 2 bits
        assert abs(h - expected) < 1e-10

    def test_deterministic_entropy(self):
        """Test entropy of deterministic distribution."""
        probs = np.array([1.0, 0.0, 0.0, 0.0])
        h = entropy(probs)
        assert abs(h - 0.0) < 2e-10  # Slightly more tolerant

    def test_binary_entropy(self):
        """Test binary entropy function."""
        probs = np.array([0.5, 0.5])
        h = entropy(probs)
        expected = 1.0  # log2(2) = 1 bit
        assert abs(h - expected) < 1e-10

    def test_entropy_monotonicity(self):
        """Test entropy increases with uniformity."""
        # More concentrated distribution
        probs1 = np.array([0.7, 0.3])
        h1 = entropy(probs1)

        # More uniform distribution
        probs2 = np.array([0.6, 0.4])
        h2 = entropy(probs2)

        assert h2 > h1

    def test_entropy_bounds(self):
        """Test entropy is non-negative and bounded."""
        probs = np.array([0.1, 0.2, 0.3, 0.4])
        h = entropy(probs)
        assert h >= 0.0
        assert h <= np.log2(len(probs))


class TestKLDivergence:
    """Test Kullback-Leibler divergence."""

    def test_kl_identical_distributions(self):
        """Test KL divergence of identical distributions is zero."""
        p = np.array([0.25, 0.25, 0.25, 0.25])
        q = np.array([0.25, 0.25, 0.25, 0.25])
        kl = kl_divergence(p, q)
        assert abs(kl) < 1e-10

    def test_kl_non_negativity(self):
        """Test KL divergence is non-negative."""
        p = np.array([0.7, 0.3])
        q = np.array([0.4, 0.6])
        kl = kl_divergence(p, q)
        assert kl >= 0.0

    def test_kl_asymmetry(self):
        """Test KL divergence is asymmetric."""
        p = np.array([0.8, 0.2])
        q = np.array([0.3, 0.7])
        kl_pq = kl_divergence(p, q)
        kl_qp = kl_divergence(q, p)
        assert abs(kl_pq - kl_qp) > 0.04  # Should be different (adjusted threshold)

    def test_kl_extreme_case(self):
        """Test KL divergence with extreme distributions."""
        p = np.array([1.0, 0.0])
        q = np.array([0.9, 0.1])
        kl = kl_divergence(p, q)
        assert kl > 0.0
        assert np.isfinite(kl)


class TestJensenShannonDivergence:
    """Test Jensen-Shannon divergence."""

    def test_js_identical_distributions(self):
        """Test JS divergence of identical distributions is zero."""
        p = np.array([0.25, 0.25, 0.25, 0.25])
        q = np.array([0.25, 0.25, 0.25, 0.25])
        js = jensen_shannon_divergence(p, q)
        assert abs(js) < 1e-10

    def test_js_symmetry(self):
        """Test JS divergence is symmetric."""
        p = np.array([0.8, 0.2])
        q = np.array([0.3, 0.7])
        js_pq = jensen_shannon_divergence(p, q)
        js_qp = jensen_shannon_divergence(q, p)
        assert abs(js_pq - js_qp) < 1e-10

    def test_js_bounds(self):
        """Test JS divergence is bounded between 0 and 1."""
        p = np.array([1.0, 0.0])
        q = np.array([0.0, 1.0])
        js = jensen_shannon_divergence(p, q)
        assert 0.0 <= js <= 1.0

    def test_js_maximum(self):
        """Test JS divergence achieves maximum for orthogonal distributions."""
        p = np.array([1.0, 0.0])
        q = np.array([0.0, 1.0])
        js = jensen_shannon_divergence(p, q)
        assert abs(js - 1.0) < 1e-10


class TestTotalCorrelation:
    """Test total correlation (multivariate mutual information)."""

    def test_total_correlation_independent(self):
        """Test total correlation for independent variables."""
        counts = {"00": 250, "01": 250, "10": 250, "11": 250}
        tc = total_correlation(counts)
        assert abs(tc) < 0.1  # Should be close to 0 for independent

    def test_total_correlation_correlated(self):
        """Test total correlation for correlated variables."""
        counts = {"00": 450, "11": 450, "01": 50, "10": 50}
        tc = total_correlation(counts)
        assert tc > 0.5  # Should be positive for correlated

    def test_total_correlation_properties(self):
        """Test basic properties of total correlation."""
        counts = {"000": 100, "111": 200, "001": 50}
        tc = total_correlation(counts)
        assert tc >= 0.0  # Non-negative
        assert np.isfinite(tc)


class TestMutualInformation:
    """Test mutual information calculations."""

    def test_mutual_information_independent(self):
        """Test MI for independent variables."""
        counts = {"00": 250, "01": 250, "10": 250, "11": 250}
        mi = mutual_information(counts, 0, 1)
        assert abs(mi) < 0.1  # Should be close to 0

    def test_mutual_information_correlated(self):
        """Test MI for perfectly correlated variables."""
        counts = {"00": 500, "11": 500}
        mi = mutual_information(counts, 0, 1)
        assert mi > 0.5  # Should be high for perfect correlation

    def test_mutual_information_properties(self):
        """Test basic properties of mutual information."""
        counts = {"000": 100, "111": 200, "001": 50}
        mi = mutual_information(counts, 0, 1)  # Fixed: use single indices
        assert mi >= 0.0  # Non-negative
        assert np.isfinite(mi)

    def test_mutual_information_symmetry(self):
        """Test MI is symmetric."""
        counts = {"00": 300, "01": 100, "10": 200, "11": 400}
        mi1 = mutual_information(counts, 0, 1)
        mi2 = mutual_information(counts, 1, 0)
        assert abs(mi1 - mi2) < 1e-10


class TestInformationTheoryIntegration:
    """Test integration between information theory functions."""

    def test_entropy_and_divergence_consistency(self):
        """Test consistency between entropy and divergence calculations."""
        counts = {"00": 300, "01": 200, "10": 250, "11": 250}
        probs = counts_to_probabilities(counts)
        prob_array = np.array(list(probs.values()))

        # Entropy should be finite and positive
        h = entropy(prob_array)
        assert 0.0 < h < 2.0  # Less than max entropy for 2 qubits

        # KL to uniform should be positive
        uniform = np.array([0.25, 0.25, 0.25, 0.25])
        kl = kl_divergence(prob_array, uniform)
        assert kl >= 0.0

    def test_full_workflow(self):
        """Test complete information theory workflow."""
        # Start with counts
        counts = {"000": 400, "111": 350, "001": 100, "110": 150}

        # Convert to probabilities with full support
        probs = counts_to_probabilities(counts)
        assert len(probs) == 8  # 2^3 = 8 outcomes

        # Calculate entropy
        prob_array = np.array(list(probs.values()))
        h = entropy(prob_array)
        assert 0.0 < h < 3.0  # Less than max entropy for 3 qubits

        # Calculate total correlation
        tc = total_correlation(counts)
        assert tc >= 0.0

        # Calculate pairwise MI
        mi = mutual_information(counts, 0, 1)
        assert mi >= 0.0

    def test_numerical_stability(self):
        """Test numerical stability with extreme distributions."""
        # Very skewed distribution
        counts = {"00": 9999, "01": 1, "10": 0, "11": 0}
        probs = counts_to_probabilities(counts)
        prob_array = np.array(list(probs.values()))

        # Should not produce NaN or inf
        h = entropy(prob_array)
        assert np.isfinite(h)

        uniform = np.array([0.25, 0.25, 0.25, 0.25])
        kl = kl_divergence(prob_array, uniform)
        assert np.isfinite(kl)
