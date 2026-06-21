"""Tests for fingerprint utilities in correlations.py."""

import numpy as np

from src.core.analysis.core.correlations import (
    cosine_similarity_matrix,
    excess_covariance_matrix,
    fingerprint_vector,
)


class TestExcessCovarianceMatrix:
    """Tests for excess_covariance_matrix."""

    def test_identical_counts_give_zero(self):
        counts = {"00": 500, "11": 500}
        result = excess_covariance_matrix(counts, counts, n_qubits=2)
        np.testing.assert_allclose(result, 0.0, atol=1e-15)

    def test_known_excess(self):
        # Baseline: uniform → Cov ≈ 0
        baseline = {"00": 250, "01": 250, "10": 250, "11": 250}
        # Test: correlated → Cov(0,1) > 0
        test = {"00": 500, "11": 500}
        result = excess_covariance_matrix(test, baseline, n_qubits=2)
        # test has positive covariance, baseline has ~0 → excess should be positive
        assert result[0, 1] > 0
        assert result[1, 0] > 0

    def test_symmetry(self):
        counts = {"000": 300, "111": 300, "010": 200, "101": 200}
        baseline = {"000": 250, "001": 250, "110": 250, "111": 250}
        result = excess_covariance_matrix(counts, baseline, n_qubits=3)
        np.testing.assert_allclose(result, result.T, atol=1e-15)

    def test_zero_diagonal(self):
        counts = {"00": 600, "11": 400}
        baseline = {"00": 400, "01": 100, "10": 100, "11": 400}
        result = excess_covariance_matrix(counts, baseline, n_qubits=2)
        np.testing.assert_allclose(np.diag(result), 0.0, atol=1e-15)


class TestFingerprintVector:
    """Tests for fingerprint_vector."""

    def test_length_2_qubits(self):
        counts = {"00": 500, "11": 500}
        baseline = {"00": 250, "01": 250, "10": 250, "11": 250}
        vec = fingerprint_vector(counts, baseline, n_qubits=2)
        assert len(vec) == 1  # 2*(2-1)/2 = 1

    def test_length_6_qubits(self):
        # All-zeros and all-ones for simplicity
        counts = {"000000": 500, "111111": 500}
        baseline = {"000000": 1000}
        vec = fingerprint_vector(counts, baseline, n_qubits=6)
        assert len(vec) == 15  # 6*(6-1)/2 = 15

    def test_zero_when_identical(self):
        counts = {"00": 500, "11": 500}
        vec = fingerprint_vector(counts, counts, n_qubits=2)
        np.testing.assert_allclose(vec, 0.0, atol=1e-15)


class TestCosineSimilarityMatrix:
    """Tests for cosine_similarity_matrix."""

    def test_identical_vectors_give_one(self):
        v = np.array([1.0, 2.0, 3.0])
        sim = cosine_similarity_matrix([v, v])
        np.testing.assert_allclose(sim, 1.0, atol=1e-10)

    def test_orthogonal_vectors_give_zero(self):
        v1 = np.array([1.0, 0.0])
        v2 = np.array([0.0, 1.0])
        sim = cosine_similarity_matrix([v1, v2])
        np.testing.assert_allclose(sim[0, 1], 0.0, atol=1e-10)
        np.testing.assert_allclose(sim[1, 0], 0.0, atol=1e-10)

    def test_zero_vector_gives_zero(self):
        v = np.array([1.0, 2.0])
        z = np.array([0.0, 0.0])
        sim = cosine_similarity_matrix([v, z])
        assert sim[0, 1] == 0.0
        assert sim[1, 0] == 0.0
        assert sim[1, 1] == 0.0

    def test_scaled_vectors_give_one(self):
        v1 = np.array([1.0, 2.0, 3.0])
        v2 = np.array([2.0, 4.0, 6.0])
        sim = cosine_similarity_matrix([v1, v2])
        np.testing.assert_allclose(sim[0, 1], 1.0, atol=1e-10)

    def test_opposite_vectors_give_negative_one(self):
        v1 = np.array([1.0, 0.0])
        v2 = np.array([-1.0, 0.0])
        sim = cosine_similarity_matrix([v1, v2])
        np.testing.assert_allclose(sim[0, 1], -1.0, atol=1e-10)

    def test_matrix_shape(self):
        vecs = [np.array([1.0, 0.0]), np.array([0.0, 1.0]), np.array([1.0, 1.0])]
        sim = cosine_similarity_matrix(vecs)
        assert sim.shape == (3, 3)
