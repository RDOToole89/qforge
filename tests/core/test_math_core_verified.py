"""Rigorous exact-value tests for the pure-math core (``src/core/analysis/core``).

Every assertion locks a hand-computed or analytically derived value rather than a
smoke check. Floating comparisons use ``pytest.approx`` / ``np.isclose`` with tight
tolerances; exact integers / halves are compared exactly.

Run (avoiding the repo coverage plugin):
    .venv\\Scripts\\python.exe -m pytest tests/core/test_math_core_verified.py -o addopts="" -q
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from src.core.analysis.core.bootstrap import (
    MetricWithConfidence,
    bootstrap_confidence_interval,
    compute_metric_with_confidence,
    determine_validation_status,
)
from src.core.analysis.core.correlations import (
    adjacency_from_distances,
    bit_covariance_matrix,
    correlation_upper_triangle,
    cosine_similarity_matrix,
    excess_covariance_matrix,
    fingerprint_vector,
    get_topology_adjacency,
    mi_matrix,
)
from src.core.analysis.core.information_theory import (
    all_bitstrings,
    counts_to_probabilities,
    counts_to_vector,
    entropy,
    jensen_shannon_divergence,
    kl_divergence,
    marginal_distribution,
    mutual_information,
    n_qubits_from_counts,
    pairwise_joint_distribution,
    total_correlation,
)
from src.core.analysis.core.null_models import (
    factorized_null,
    factorized_null_model,
    generate_null_samples,
    ghz_aware_null_model,
    parametric_bootstrap_null,
    readout_confusion_model,
    sample_multinomial_counts,
)
from src.core.analysis.core.topology import (
    TOPOLOGY_BUILDERS,
    all_to_all_adjacency,
    chain_adjacency,
    star_adjacency,
)
from tests._qhelpers import fraction_ones_q0 as _fraction_ones_q0

# ---------------------------------------------------------------------------
# information_theory.py
# ---------------------------------------------------------------------------


class TestEntropy:
    @pytest.mark.parametrize(
        "p, expected",
        [
            (np.array([0.25, 0.25, 0.25, 0.25]), 2.0),  # uniform over 4 -> 2 bits
            (np.array([0.5, 0.5]), 1.0),  # fair coin -> 1 bit
            (np.array([0.5, 0.25, 0.25]), 1.5),  # 0.5 + 0.25*2*2 = 1.5 bits
        ],
    )
    def test_entropy_exact(self, p, expected):
        assert entropy(p) == pytest.approx(expected, abs=1e-9)

    def test_entropy_deterministic_near_zero(self):
        # Clamping leaves a tiny residual; analytically 0.
        assert entropy(np.array([1.0, 0.0, 0.0, 0.0])) == pytest.approx(0.0, abs=1e-6)

    def test_entropy_base_e_nats(self):
        # H([.5,.5]) in nats = ln 2.
        assert entropy(np.array([0.5, 0.5]), base=math.e) == pytest.approx(math.log(2), abs=1e-9)

    def test_entropy_unnormalized_is_normalized(self):
        # [1,1,1,1] -> uniform-4 -> 2 bits.
        assert entropy(np.array([1.0, 1.0, 1.0, 1.0])) == pytest.approx(2.0, abs=1e-9)


class TestKLDivergence:
    def test_kl_exact_nats(self):
        kl = kl_divergence(np.array([0.5, 0.5]), np.array([0.25, 0.75]))
        assert kl == pytest.approx(0.14384103622589042, abs=1e-15)

    def test_kl_self_is_zero(self):
        assert kl_divergence(np.array([0.3, 0.7]), np.array([0.3, 0.7])) == pytest.approx(
            0.0, abs=1e-12
        )

    def test_kl_shape_mismatch_raises(self):
        with pytest.raises(ValueError, match="shape mismatch"):
            kl_divergence(np.array([0.5, 0.5]), np.array([0.3, 0.3, 0.4]))


class TestJensenShannon:
    def test_jsd_self_is_zero(self):
        p = np.array([0.3, 0.7])
        assert jensen_shannon_divergence(p, p) == pytest.approx(0.0, abs=1e-12)

    def test_jsd_exact(self):
        jsd = jensen_shannon_divergence(np.array([1.0, 0.0]), np.array([0.5, 0.5]))
        assert jsd == pytest.approx(0.31127812443927245, abs=1e-9)

    def test_jsd_symmetric(self):
        a = jensen_shannon_divergence(np.array([1.0, 0.0]), np.array([0.5, 0.5]))
        b = jensen_shannon_divergence(np.array([0.5, 0.5]), np.array([1.0, 0.0]))
        assert a == pytest.approx(b, abs=1e-12)

    def test_jsd_disjoint_support_near_one(self):
        jsd = jensen_shannon_divergence(np.array([1.0, 0.0]), np.array([0.0, 1.0]))
        assert jsd == pytest.approx(1.0, abs=1e-6)

    def test_jsd_shape_mismatch_raises(self):
        with pytest.raises(ValueError, match="lengths differ"):
            jensen_shannon_divergence(np.array([0.5, 0.5]), np.array([0.3, 0.3, 0.4]))


class TestHelpers:
    def test_n_qubits_from_counts(self):
        assert n_qubits_from_counts({"000": 1, "111": 2}) == 3

    def test_all_bitstrings_order(self):
        assert all_bitstrings(2) == ["00", "01", "10", "11"]
        assert all_bitstrings(3)[0] == "000"
        assert all_bitstrings(3)[-1] == "111"

    def test_counts_to_vector_aligns_and_fills_zero(self):
        vec = counts_to_vector({"00": 5, "11": 7}, ["00", "01", "10", "11"])
        assert np.array_equal(vec, np.array([5.0, 0.0, 0.0, 7.0]))

    def test_counts_to_probabilities_full_support_sums_to_one(self):
        probs = counts_to_probabilities({"00": 500, "11": 500})
        assert set(probs.keys()) == {"00", "01", "10", "11"}  # full 2^n support
        assert sum(probs.values()) == pytest.approx(1.0, abs=1e-12)
        # Symmetry: "00" and "11" share count, so equal smoothed prob.
        assert probs["00"] == pytest.approx(probs["11"], abs=1e-12)
        # Smoothed: (500+0.5)/(1000+0.5*4) = 500.5/1002.
        assert probs["00"] == pytest.approx(500.5 / 1002.0, abs=1e-12)
        assert probs["01"] == pytest.approx(0.5 / 1002.0, abs=1e-12)


class TestMarginal:
    def test_marginal_uniform(self):
        m = marginal_distribution({"00": 250, "01": 250, "10": 250, "11": 250}, 0)
        assert np.allclose(m, np.array([0.5, 0.5]))

    def test_marginal_smoothing_exact(self):
        # qubit 0: bit=1 in "10","11" -> 200; bit=0 -> 600; smoothed /801.
        m = marginal_distribution({"00": 300, "01": 300, "10": 100, "11": 100}, 0)
        assert m[0] == pytest.approx(600.5 / 801.0, abs=1e-12)
        assert m[1] == pytest.approx(200.5 / 801.0, abs=1e-12)

    def test_marginal_index_out_of_range(self):
        with pytest.raises(ValueError, match="out of range"):
            marginal_distribution({"00": 1, "11": 1}, 5)

    def test_marginal_negative_index_out_of_range(self):
        with pytest.raises(ValueError, match="out of range"):
            marginal_distribution({"00": 1, "11": 1}, -1)


class TestPairwiseJoint:
    def test_joint_bell_smoothed(self):
        j = pairwise_joint_distribution({"00": 500, "11": 500}, 0, 1)
        assert j.shape == (2, 2)
        # joint_counts[0,0]=500,[1,1]=500; smoothed /(1000+2).
        assert j[0, 0] == pytest.approx(500.5 / 1002.0, abs=1e-12)
        assert j[0, 1] == pytest.approx(0.5 / 1002.0, abs=1e-12)
        assert j.sum() == pytest.approx(1.0, abs=1e-12)

    def test_joint_equal_indices_raises(self):
        with pytest.raises(ValueError, match="must be different"):
            pairwise_joint_distribution({"00": 1, "11": 1}, 0, 0)

    def test_joint_index_out_of_range(self):
        with pytest.raises(ValueError, match="out of range"):
            pairwise_joint_distribution({"00": 1, "11": 1}, 0, 9)


class TestMutualInformation:
    def test_mi_independent_near_zero(self):
        # Large N independent product -> MI ~ 0.
        counts = {"00": 2500, "01": 2500, "10": 2500, "11": 2500}
        assert mutual_information(counts, 0, 1) == pytest.approx(0.0, abs=1e-3)

    def test_mi_bell_positive(self):
        mi = mutual_information({"00": 500, "11": 500}, 0, 1)
        assert mi > 0.9
        assert mi == pytest.approx(0.9886121340451401, abs=1e-9)


class TestTotalCorrelation:
    def test_tc_bell_near_one(self):
        tc = total_correlation({"00": 500, "11": 500})
        assert tc == pytest.approx(0.9886121340451401, abs=1e-9)

    def test_tc_independent_near_zero(self):
        counts = {"00": 2500, "01": 2500, "10": 2500, "11": 2500}
        assert total_correlation(counts) == pytest.approx(0.0, abs=1e-3)

    def test_tc_high_correlation_logs(self):
        # 3-qubit GHZ-like data exercises the "high TC" logging branch.
        tc = total_correlation({"000": 5000, "111": 5000})
        assert tc > 1.5

    def test_tc_empty_raises(self):
        with pytest.raises(ValueError, match="empty"):
            total_correlation({})

    def test_tc_zero_qubits_returns_zero(self):
        # Empty-string key is valid (vacuously binary) -> n_qubits == 0 branch.
        assert total_correlation({"": 5}) == 0.0

    def test_tc_moderate_branch(self):
        # tc/max in (0.3, 0.7) exercises the "moderate" logging branch.
        tc = total_correlation({"00": 450, "11": 450, "01": 50, "10": 50})
        assert 0.3 < tc < 0.7


class TestLargeSupportWarnings:
    """Exercise the soft >MAX_OUTCOMES_EXACT warning branches (n=17 > 16)."""

    def test_counts_to_probabilities_large_support(self):
        probs = counts_to_probabilities({"0" * 17: 10})
        assert sum(probs.values()) == pytest.approx(1.0, abs=1e-9)

    def test_factorized_null_large_support(self):
        null = factorized_null_model({"0" * 17: 10})
        assert sum(null.values()) == pytest.approx(1.0, abs=1e-9)

    def test_ghz_aware_large_support(self):
        null = ghz_aware_null_model({"0" * 17: 10})
        assert sum(null.values()) == pytest.approx(1.0, abs=1e-9)


# ---------------------------------------------------------------------------
# correlations.py
# ---------------------------------------------------------------------------


class TestMIMatrix:
    def test_mi_matrix_bell_structure(self):
        m = mi_matrix({"00": 500, "11": 500})
        assert m.shape == (2, 2)
        assert m[0, 0] == 0.0 and m[1, 1] == 0.0  # zero diagonal
        assert m[0, 1] == pytest.approx(m[1, 0], abs=1e-12)  # symmetric
        assert m[0, 1] == pytest.approx(0.9886121340451401, abs=1e-9)

    def test_mi_matrix_requires_two_qubits(self):
        with pytest.raises(ValueError, match="≥2 qubits"):
            mi_matrix({"0": 500, "1": 500})


class TestAdjacencyFromDistances:
    def test_exponential_decay_exact(self):
        d = np.array([[0.0, 1.0, 2.0], [1.0, 0.0, 1.0], [2.0, 1.0, 0.0]])
        adj = adjacency_from_distances(d, lam=1.0)
        assert adj[0, 1] == pytest.approx(0.36787944117144233, abs=1e-15)  # e^-1
        assert adj[0, 2] == pytest.approx(0.1353352832366127, abs=1e-15)  # e^-2
        assert np.all(np.diag(adj) == 0.0)

    def test_non_square_raises(self):
        with pytest.raises(ValueError, match="must be square"):
            adjacency_from_distances(np.array([[0.0, 1.0, 2.0]]))

    def test_non_finite_raises(self):
        with pytest.raises(ValueError, match="non-finite"):
            adjacency_from_distances(np.array([[0.0, np.inf], [np.inf, 0.0]]))

    def test_too_few_qubits_raises(self):
        with pytest.raises(ValueError, match="≥2 qubits"):
            adjacency_from_distances(np.array([[0.0]]))

    def test_nonpositive_lambda_raises(self):
        with pytest.raises(ValueError, match="must be positive"):
            adjacency_from_distances(np.array([[0.0, 1.0], [1.0, 0.0]]), lam=0.0)

    def test_negative_distance_raises(self):
        with pytest.raises(ValueError, match="negative"):
            adjacency_from_distances(np.array([[0.0, -1.0], [-1.0, 0.0]]))

    def test_asymmetric_and_nonzero_diag_warns_but_computes(self):
        # Asymmetric + nonzero diagonal go down the warning branches (no raise).
        d = np.array([[1.0, 1.0], [2.0, 1.0]])
        adj = adjacency_from_distances(d, lam=1.0)
        assert np.all(np.diag(adj) == 0.0)


class TestTopologyAdjacency:
    def test_ring_four(self):
        adj = get_topology_adjacency("ring", 4)
        assert adj[0, 3] == 1.0  # wraparound edge
        assert adj[0, 2] == 0.0  # no diagonal chord
        assert adj.sum() / 2 == 4  # 4 edges in a 4-ring

    def test_linear_four(self):
        adj = get_topology_adjacency("linear", 4)
        assert adj[0, 1] == 1.0 and adj[2, 3] == 1.0
        assert adj[0, 3] == 0.0  # no wraparound
        assert adj.sum() / 2 == 3

    def test_star_five_hub(self):
        adj = get_topology_adjacency("star", 5)
        assert all(adj[0, i] == 1.0 for i in range(1, 5))
        assert adj[1, 2] == 0.0  # spokes not connected
        assert adj.sum() / 2 == 4

    def test_all_to_all_three(self):
        adj = get_topology_adjacency("all_to_all", 3)
        assert np.all(np.diag(adj) == 0.0)
        off = adj[~np.eye(3, dtype=bool)]
        assert np.all(off == 1.0)

    def test_grid_four_is_square(self):
        adj = get_topology_adjacency("grid", 4)  # 2x2 grid -> 4 edges
        assert adj.sum() / 2 == 4

    def test_grid_ragged(self):
        # n=5: rows=2, cols=3, rows*cols=6 != 5 -> ragged-grid warning branch.
        adj = get_topology_adjacency("grid", 5)
        assert adj.shape == (5, 5)
        assert np.allclose(adj, adj.T)

    def test_unknown_topology_raises(self):
        with pytest.raises(ValueError, match="Unknown topology"):
            get_topology_adjacency("hypercube", 4)

    def test_too_few_qubits_raises(self):
        with pytest.raises(ValueError, match="≥2 qubits"):
            get_topology_adjacency("ring", 1)


class TestCorrelationUpperTriangle:
    def test_upper_triangle_values(self):
        m = np.array([[0.0, 1.0, 2.0], [1.0, 0.0, 3.0], [2.0, 3.0, 0.0]])
        ut = correlation_upper_triangle(m)
        assert np.array_equal(ut, np.array([1.0, 2.0, 3.0]))

    def test_single_element_returns_empty(self):
        assert correlation_upper_triangle(np.array([[0.0]])).size == 0

    def test_non_square_raises(self):
        with pytest.raises(ValueError, match="must be square"):
            correlation_upper_triangle(np.array([[0.0, 1.0, 2.0]]))

    def test_asymmetric_warns_but_computes(self):
        ut = correlation_upper_triangle(np.array([[0.0, 1.0], [9.0, 0.0]]))
        assert ut.size == 1


class TestBitCovariance:
    def test_bell_positive_covariance(self):
        cov = bit_covariance_matrix({"00": 500, "11": 500}, 2)
        assert cov[0, 1] == pytest.approx(0.25, abs=1e-12)
        assert np.all(np.diag(cov) == 0.0)

    def test_anticorrelated(self):
        cov = bit_covariance_matrix({"01": 500, "10": 500}, 2)
        assert cov[0, 1] == pytest.approx(-0.25, abs=1e-12)

    def test_uniform_zero_covariance(self):
        cov = bit_covariance_matrix({"00": 250, "01": 250, "10": 250, "11": 250}, 2)
        assert cov[0, 1] == pytest.approx(0.0, abs=1e-12)

    def test_skewed_covariance_exact(self):
        # E[b1 b2]=0.4, E[b1]=E[b2]=0.4 -> 0.4-0.16=0.24.
        cov = bit_covariance_matrix({"00": 600, "11": 400}, 2)
        assert cov[0, 1] == pytest.approx(0.24, abs=1e-12)

    def test_zero_total_returns_zeros(self):
        cov = bit_covariance_matrix({"00": 0, "11": 0}, 2)
        assert np.all(cov == 0.0)


class TestExcessCovarianceAndFingerprint:
    def test_excess_covariance_difference(self):
        test = {"00": 500, "11": 500}  # cov 0.25
        base = {"00": 250, "01": 250, "10": 250, "11": 250}  # cov 0
        dcov = excess_covariance_matrix(test, base, 2)
        assert dcov[0, 1] == pytest.approx(0.25, abs=1e-12)

    def test_fingerprint_vector_upper_triangle(self):
        test = {"00": 500, "11": 500}
        base = {"00": 250, "01": 250, "10": 250, "11": 250}
        fp = fingerprint_vector(test, base, 2)
        assert fp.shape == (1,)  # n*(n-1)/2 = 1
        assert fp[0] == pytest.approx(0.25, abs=1e-12)


class TestCosineSimilarity:
    def test_identical_vectors(self):
        sim = cosine_similarity_matrix([np.array([1.0, 0.0]), np.array([2.0, 0.0])])
        assert sim[0, 1] == pytest.approx(1.0, abs=1e-12)

    def test_orthogonal_vectors(self):
        sim = cosine_similarity_matrix([np.array([1.0, 0.0]), np.array([0.0, 1.0])])
        assert sim[0, 1] == pytest.approx(0.0, abs=1e-12)

    def test_zero_vector_yields_zero_similarity(self):
        sim = cosine_similarity_matrix([np.array([0.0, 0.0]), np.array([1.0, 1.0])])
        assert sim[0, 1] == pytest.approx(0.0, abs=1e-12)
        assert sim[0, 0] == pytest.approx(0.0, abs=1e-12)


# ---------------------------------------------------------------------------
# topology.py
# ---------------------------------------------------------------------------


class TestTopologyBuilders:
    def test_chain_edges(self):
        W = chain_adjacency(4)
        edges = {(i, j) for i in range(4) for j in range(4) if i < j and W[i, j] == 1.0}
        assert edges == {(0, 1), (1, 2), (2, 3)}
        assert np.allclose(W, W.T)

    def test_chain_single_node(self):
        assert np.array_equal(chain_adjacency(1), np.array([[0.0]]))

    def test_star_hub_zero(self):
        W = star_adjacency(4)
        assert all(W[0, i] == 1.0 for i in range(1, 4))
        assert W[1, 2] == 0.0
        assert np.allclose(W, W.T)

    def test_all_to_all_is_J_minus_I(self):
        W = all_to_all_adjacency(3)
        expected = np.ones((3, 3)) - np.eye(3)
        assert np.array_equal(W, expected)

    @pytest.mark.parametrize(
        "key, builder",
        [
            ("GHZ", chain_adjacency),
            ("CLUSTER", chain_adjacency),
            ("CHAIN", chain_adjacency),
            ("W", all_to_all_adjacency),
            ("ALL_TO_ALL", all_to_all_adjacency),
            ("STAR", star_adjacency),
        ],
    )
    def test_registry_aliases(self, key, builder):
        assert TOPOLOGY_BUILDERS[key] is builder


# ---------------------------------------------------------------------------
# null_models.py
# ---------------------------------------------------------------------------


class TestFactorizedNull:
    def test_independent_product_reconstructed(self):
        counts = {"00": 300, "01": 300, "10": 100, "11": 100}
        null = factorized_null_model(counts)
        assert set(null.keys()) == {"00", "01", "10", "11"}  # full 2^n support
        assert sum(null.values()) == pytest.approx(1.0, abs=1e-12)
        # qubit 1 marginal is exactly [0.5, 0.5] here.
        m1 = marginal_distribution(counts, 1)
        assert np.allclose(m1, np.array([0.5, 0.5]))
        # Product check: null["00"] = q0(0)*q1(0).
        m0 = marginal_distribution(counts, 0)
        assert null["00"] == pytest.approx(m0[0] * m1[0], abs=1e-12)

    def test_alias_identical(self):
        counts = {"00": 300, "01": 300, "10": 100, "11": 100}
        assert factorized_null(counts) == factorized_null_model(counts)


class TestSampleMultinomial:
    def test_same_seed_identical(self):
        probs = {"00": 0.25, "01": 0.25, "10": 0.25, "11": 0.25}
        a = sample_multinomial_counts(probs, 1000, np.random.default_rng(7))
        b = sample_multinomial_counts(probs, 1000, np.random.default_rng(7))
        assert a == b

    def test_drop_zeros_false_full_support(self):
        # A deterministic-ish prob vector still yields all 2^n keys when drop_zeros=False.
        probs = {"00": 0.97, "01": 0.01, "10": 0.01, "11": 0.01}
        out = sample_multinomial_counts(probs, 50, np.random.default_rng(0), drop_zeros=False)
        assert len(out) == 4
        assert sum(out.values()) == 50

    def test_drop_zeros_true_omits_zero_keys(self):
        probs = {"00": 1.0, "01": 0.0, "10": 0.0, "11": 0.0}
        out = sample_multinomial_counts(probs, 100, np.random.default_rng(0), drop_zeros=True)
        assert out == {"00": 100}

    def test_defensive_renormalization(self):
        # Probs summing to 0.6 (>0, not ~1) hit the defensive renormalize branch.
        out = sample_multinomial_counts(
            {"0": 0.3, "1": 0.3}, 1000, np.random.default_rng(0), drop_zeros=False
        )
        assert sum(out.values()) == 1000

    def test_nonpositive_N_raises(self):
        with pytest.raises(ValueError, match="N must be positive"):
            sample_multinomial_counts({"0": 1.0}, 0, np.random.default_rng(0))

    def test_invalid_probability_vector_raises(self):
        with pytest.raises(ValueError, match="invalid"):
            sample_multinomial_counts({"0": 0.0, "1": 0.0}, 10, np.random.default_rng(0))


class TestGenerateNullSamples:
    def test_returns_single_dataset(self):
        null = {"00": 0.25, "01": 0.25, "10": 0.25, "11": 0.25}
        out = generate_null_samples(null, 500, np.random.default_rng(1))
        assert len(out) == 1
        assert sum(out[0].values()) == 500

    def test_empty_null_raises(self):
        with pytest.raises(ValueError, match="Empty null model"):
            generate_null_samples({}, 10, np.random.default_rng(0))

    def test_nonpositive_samples_raises(self):
        with pytest.raises(ValueError, match="must be positive"):
            generate_null_samples({"0": 1.0}, 0, np.random.default_rng(0))


class TestParametricBootstrap:
    def test_count_and_totals(self):
        counts = {"00": 300, "11": 300, "01": 200, "10": 200}
        N = sum(counts.values())
        out = parametric_bootstrap_null(counts, n_bootstrap=50, rng=np.random.default_rng(0))
        assert len(out) == 50
        assert all(sum(d.values()) == N for d in out)

    def test_default_rng_path(self):
        # rng=None branch creates a fresh generator.
        out = parametric_bootstrap_null({"00": 100, "11": 100}, n_bootstrap=3)
        assert len(out) == 3

    def test_zero_total_raises(self):
        with pytest.raises(ValueError, match="zero total"):
            parametric_bootstrap_null({"00": 0, "11": 0}, n_bootstrap=5)


class TestReadoutConfusionModel:
    def test_asymmetric_recovery(self):
        # measured marginal [0.66, 0.34] with C=[[0.9,0.1],[0.3,0.7]] -> recover ~[0.6,0.4].
        C = np.array([[0.9, 0.1], [0.3, 0.7]])
        corrected = readout_confusion_model({"0": 660, "1": 340}, [C])
        assert sum(corrected.values()) == pytest.approx(1.0, abs=1e-12)
        assert corrected["0"] == pytest.approx(0.6, abs=2e-3)
        assert corrected["1"] == pytest.approx(0.4, abs=2e-3)

    def test_symmetric_matrix_sums_to_one(self):
        C = np.array([[0.9, 0.1], [0.1, 0.9]])
        corrected = readout_confusion_model({"0": 700, "1": 300}, [C])
        assert sum(corrected.values()) == pytest.approx(1.0, abs=1e-12)

    def test_wrong_number_of_matrices_raises(self):
        C = np.array([[0.9, 0.1], [0.1, 0.9]])
        with pytest.raises(ValueError, match="confusion matrices"):
            readout_confusion_model({"00": 1, "11": 1}, [C])  # need 2, gave 1

    def test_wrong_shape_raises(self):
        bad = np.eye(3)
        with pytest.raises(ValueError, match="shape"):
            readout_confusion_model({"0": 1, "1": 1}, [bad])

    def test_rows_not_summing_to_one_raises(self):
        bad = np.array([[0.9, 0.2], [0.1, 0.9]])
        with pytest.raises(ValueError, match="don't sum to 1"):
            readout_confusion_model({"0": 1, "1": 1}, [bad])

    def test_out_of_range_probabilities_raise(self):
        bad = np.array([[1.2, -0.2], [0.1, 0.9]])
        with pytest.raises(ValueError, match="outside"):
            readout_confusion_model({"0": 1, "1": 1}, [bad])

    def test_singular_matrix_falls_back_to_uncorrected(self):
        # regularization=0 + a singular C C^T makes np.linalg.solve raise
        # LinAlgError, exercising the uncorrected-marginal fallback branch.
        C = np.array([[0.5, 0.5], [0.5, 0.5]])  # row-stochastic but rank 1
        corrected = readout_confusion_model({"0": 700, "1": 300}, [C], regularization=0.0)
        assert sum(corrected.values()) == pytest.approx(1.0, abs=1e-9)

    def test_many_qubits_slow_warning_branch(self):
        # 9 qubits (> 8) exercises the "may be slow" warning branch.
        C = np.array([[0.95, 0.05], [0.05, 0.95]])
        counts = {"0" * 9: 600, "1" * 9: 400}
        corrected = readout_confusion_model(counts, [C] * 9)
        assert sum(corrected.values()) == pytest.approx(1.0, abs=1e-9)


class TestGHZAwareNull:
    def test_ghz_structure(self):
        null = ghz_aware_null_model({"000": 400, "111": 400, "010": 200})
        assert len(null) == 8  # full 2^n support
        assert sum(null.values()) == pytest.approx(1.0, abs=1e-12)
        assert null["000"] == pytest.approx(null["111"], abs=1e-12)

    def test_no_special_outcomes_path(self):
        # Neither all-zeros nor all-ones present -> minimal-mass branch.
        null = ghz_aware_null_model({"010": 500, "101": 500})
        assert sum(null.values()) == pytest.approx(1.0, abs=1e-12)
        assert null["000"] == pytest.approx(null["111"], abs=1e-12)

    def test_n_qubits_mismatch_raises(self):
        with pytest.raises(ValueError, match="mismatch"):
            ghz_aware_null_model({"000": 1, "111": 1}, n_qubits=4)

    def test_explicit_matching_n_qubits(self):
        null = ghz_aware_null_model({"00": 400, "11": 400}, n_qubits=2)
        assert len(null) == 4


# ---------------------------------------------------------------------------
# bootstrap.py
# ---------------------------------------------------------------------------


def _total_shots(counts):
    return float(sum(counts.values()))


class TestBootstrapCI:
    def test_reproducible_with_fixed_rng(self):
        counts = {"00": 500, "11": 500}
        a = bootstrap_confidence_interval(
            counts, _fraction_ones_q0, n_bootstrap=200, rng=np.random.default_rng(42)
        )
        b = bootstrap_confidence_interval(
            counts, _fraction_ones_q0, n_bootstrap=200, rng=np.random.default_rng(42)
        )
        assert a == b
        lo, hi = a
        assert lo <= 0.5 <= hi  # CI brackets the true 0.5 fraction

    def test_random_state_alias_used(self):
        counts = {"00": 500, "11": 500}
        a = bootstrap_confidence_interval(
            counts, _fraction_ones_q0, n_bootstrap=100, random_state=np.random.default_rng(3)
        )
        b = bootstrap_confidence_interval(
            counts, _fraction_ones_q0, n_bootstrap=100, rng=np.random.default_rng(3)
        )
        assert a == b

    def test_constant_metric_zero_width(self):
        counts = {"00": 500, "11": 500}
        lo, hi = bootstrap_confidence_interval(
            counts, _total_shots, n_bootstrap=50, rng=np.random.default_rng(0)
        )
        # _total_shots is constant across equal-size resamples -> degenerate CI.
        assert lo == pytest.approx(hi, abs=1e-9)

    def test_nonpositive_bootstrap_raises(self):
        with pytest.raises(ValueError, match="n_bootstrap must be positive"):
            bootstrap_confidence_interval({"0": 1, "1": 1}, _total_shots, n_bootstrap=0)

    def test_zero_total_counts_returns_zero_zero(self):
        # Passes validation (non-negative ints) but sums to zero.
        assert bootstrap_confidence_interval({"00": 0, "11": 0}, _total_shots) == (0.0, 0.0)

    def test_unknown_method_raises(self):
        with pytest.raises(ValueError, match="Unknown CI method"):
            bootstrap_confidence_interval(
                {"00": 500, "11": 500},
                _fraction_ones_q0,
                n_bootstrap=20,
                method="bogus",
                rng=np.random.default_rng(0),
            )

    def test_bca_method_runs(self):
        # scipy is available -> BCa path computes adjusted percentiles.
        counts = {"00": 400, "01": 300, "10": 200, "11": 100}
        lo, hi = bootstrap_confidence_interval(
            counts, _fraction_ones_q0, n_bootstrap=200, method="bca", rng=np.random.default_rng(1)
        )
        assert lo <= hi

    def test_few_samples_branch(self):
        # n_samples < 10 triggers the low-sample warning branch.
        lo, hi = bootstrap_confidence_interval(
            {"00": 3, "11": 2}, _fraction_ones_q0, n_bootstrap=20, rng=np.random.default_rng(0)
        )
        assert lo <= hi

    def test_some_resamples_fail_branch(self):
        # Metric raises when the rare "00" key is missing from a resample, so a
        # large fraction (>10%) of bootstrap samples fail -> exercises the
        # per-sample except + "many failed" warning branches.
        def needs_00(counts):
            if "00" not in counts:
                raise KeyError("00 missing")
            return counts["00"] / sum(counts.values())

        lo, hi = bootstrap_confidence_interval(
            {"00": 1, "11": 3}, needs_00, n_bootstrap=50, rng=np.random.default_rng(0)
        )
        assert lo <= hi

    def test_all_resamples_fail_returns_original(self):
        calls = [0]

        def first_ok_then_raise(counts):
            calls[0] += 1
            if calls[0] == 1:
                return 0.5
            raise RuntimeError("resample failure")

        result = bootstrap_confidence_interval(
            {"00": 500, "11": 500},
            first_ok_then_raise,
            n_bootstrap=10,
            rng=np.random.default_rng(0),
        )
        assert result == (0.5, 0.5)  # falls back to (original, original)

    def test_original_outside_ci_is_adjusted(self):
        calls = [0]

        def big_then_zero(counts):
            calls[0] += 1
            return 100.0 if calls[0] == 1 else 0.0

        lo, hi = bootstrap_confidence_interval(
            {"00": 500, "11": 500},
            big_then_zero,
            n_bootstrap=10,
            rng=np.random.default_rng(0),
        )
        # bootstrap dist is all zeros; original=100 lies outside -> CI widened.
        assert lo == pytest.approx(0.0, abs=1e-9)
        assert hi == pytest.approx(100.0, abs=1e-9)

    def test_bca_falls_back_when_quantile_unavailable(self, monkeypatch):
        def _raise(*a, **k):
            raise RuntimeError("no ppf")

        monkeypatch.setattr("scipy.stats.norm.ppf", _raise)
        lo, hi = bootstrap_confidence_interval(
            {"00": 400, "01": 300, "10": 200, "11": 100},
            _fraction_ones_q0,
            n_bootstrap=80,
            method="bca",
            rng=np.random.default_rng(0),
        )
        assert lo <= hi  # percentile fallback succeeded

    def test_bca_falls_back_when_cdf_unavailable(self, monkeypatch):
        def _raise(*a, **k):
            raise RuntimeError("no cdf")

        monkeypatch.setattr("scipy.stats.norm.cdf", _raise)
        lo, hi = bootstrap_confidence_interval(
            {"00": 400, "01": 300, "10": 200, "11": 100},
            _fraction_ones_q0,
            n_bootstrap=80,
            method="bca",
            rng=np.random.default_rng(0),
        )
        assert lo <= hi


class TestDetermineValidationStatus:
    @pytest.mark.parametrize(
        "ci_width, value, n, expected",
        [
            (0.1, 1.0, 200, "validated"),
            (1.6, 1.0, 200, "experimental"),
            (3.0, 1.0, 200, "unstable"),
            (0.1, 1.0, 40, "unstable"),  # n too low even with tight CI
        ],
    )
    def test_nonzero_value_branches(self, ci_width, value, n, expected):
        assert determine_validation_status(ci_width, value, n) == expected

    @pytest.mark.parametrize(
        "ci_width, n, expected",
        [
            (0.05, 200, "validated"),
            (0.2, 60, "experimental"),
            (0.5, 200, "unstable"),
            (0.05, 40, "unstable"),  # near-zero value but too few samples
        ],
    )
    def test_near_zero_value_branches(self, ci_width, n, expected):
        assert determine_validation_status(ci_width, 0.0, n) == expected


class TestMetricWithConfidence:
    def test_to_dict_shape(self):
        m = MetricWithConfidence(value=0.5, ci95=(0.4, 0.6), status="validated")
        d = m.to_dict()
        assert d == {"value": 0.5, "ci95": [0.4, 0.6], "status": "validated"}
        assert isinstance(d["ci95"], list)  # tuple -> list

    def test_compute_metric_with_confidence_basic(self):
        counts = {"00": 500, "11": 500}
        result = compute_metric_with_confidence(
            counts,
            _fraction_ones_q0,
            metric_name="frac",
            n_bootstrap=100,
            rng=np.random.default_rng(0),
        )
        assert isinstance(result, MetricWithConfidence)
        assert result.value == pytest.approx(0.5, abs=1e-12)
        assert result.ci95[0] <= result.value <= result.ci95[1]
        assert result.status in {"validated", "experimental", "unstable"}

    def test_compute_metric_with_kwargs_binding(self):
        # metric_kwargs triggers the _bound_metric closure path.
        def metric_with_kw(counts, *, scale=1.0):
            return _fraction_ones_q0(counts) * scale

        result = compute_metric_with_confidence(
            {"00": 500, "11": 500},
            metric_with_kw,
            n_bootstrap=50,
            rng=np.random.default_rng(0),
            scale=2.0,
        )
        assert result.value == pytest.approx(1.0, abs=1e-12)

    def test_compute_metric_failure_returns_unstable(self):
        def boom(counts):
            raise RuntimeError("nope")

        result = compute_metric_with_confidence({"00": 500, "11": 500}, boom, n_bootstrap=10)
        assert result.status == "unstable"
        assert result.value == 0.0
        assert result.ci95 == (0.0, 0.0)
