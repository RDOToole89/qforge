"""Exact-value tests for INTERMEDIARY math helpers in ``src/core/analysis/metrics``.

These functions / analysis-object fields are computed during normal metric
evaluation but their numeric outputs were never directly asserted. Each value
below was confirmed by running the code and locking the result. Values that come
out of an optimizer (scipy curve_fit / AIC selection) are marked
``# regression-locked (optimizer output)`` and compared with a relative tolerance.

Run (avoiding the repo coverage plugin):
    pytest tests/core/test_metrics_intermediates_verified.py
"""

from __future__ import annotations

import numpy as np
import pytest

from src.core.analysis.constants import ALPHA
from src.core.analysis.metrics.asymmetry_index import (
    compute_asymmetry_index,
    compute_asymmetry_index_with_null_comparison,
)
from src.core.analysis.metrics.asymmetry_index import compute_asymmetry_index as _cai
from src.core.analysis.metrics.complexity_emergence_score import (
    _calculate_ces_from_fit,
    _fit_best_emergence_model,
    _fit_emergence_model,
    _fit_logistic_emergence,
)
from src.core.analysis.metrics.entanglement_error_correlation import (
    _compute_error_correlation_matrix,
    _compute_kway_entanglement_weight,
    _compute_kway_error_frequency,
    _construct_entanglement_topology,
    compute_multiway_entanglement_correlation,
)
from src.core.analysis.metrics.noise_topology_correlation import (
    noise_topology_correlation,
)
from src.core.analysis.metrics.pathway_concentration_ratio import (
    compute_pathway_concentration_ratio,
)
from src.core.analysis.metrics.temporal_pathway_stability import (
    compute_pathway_persistence_scores,
    compute_temporal_pathway_stability,
    compute_temporal_transition_matrix,
)

GHZ_3Q = {"000": 400, "111": 400, "001": 100, "110": 100}
STRUCTURED_4Q = {"0000": 400, "1111": 400, "0011": 100, "1100": 100}

# The SHARP CES series reuses the same multi-size fixture as the existing
# metrics tests; the (n_qubits -> counts) inputs produce the AI series below.
SHARP_SERIES = {
    2: {"00": 990, "01": 10},
    3: {"000": 500, "111": 480, "001": 20},
    4: {"0000": 600, "1111": 350, "0001": 50},
    5: {"00000": 700, "11111": 250, "00001": 50},
}


# ---------------------------------------------------------------------------
# Asymmetry Index analysis-object intermediates
# ---------------------------------------------------------------------------


class TestAsymmetryIntermediates:
    def test_analysis_uniform_deviation_and_entropy_reduction(self):
        a = compute_asymmetry_index(GHZ_3Q, return_analysis=True)
        # L-infinity deviation from uniform on full 2^n support.
        assert a.uniform_deviation == pytest.approx(0.2739043824701195, abs=1e-15)
        # (H_max - H_obs) / H_max in bits.
        assert float(a.entropy_reduction) == pytest.approx(0.4185272463877047, abs=1e-15)

    def test_null_comparison_factorized_and_uniform(self):
        ai_u, ai_f, interp = compute_asymmetry_index_with_null_comparison({"00": 600, "01": 400})
        # AI vs uniform (closed form) and AI vs factorized null.
        assert ai_u == pytest.approx(0.499001996007984, abs=1e-15)
        assert ai_f == pytest.approx(0.0004985034925154347, abs=1e-15)
        assert interp == "marginal_bias_only"


# ---------------------------------------------------------------------------
# Pathway Concentration Ratio: _generate_concentration_analysis fields
# ---------------------------------------------------------------------------


class TestPCRIntermediates:
    def test_concentration_analysis_shares_and_gini(self):
        counts = {"000": 600, "111": 300, "001": 50, "010": 30, "011": 20}
        a = compute_pathway_concentration_ratio(counts, return_analysis=True)
        assert float(a.gini_coefficient) == pytest.approx(0.5720000000000001, abs=1e-15)
        assert a.top_quartile_share == pytest.approx(0.6, abs=1e-15)
        assert a.bottom_quartile_share == pytest.approx(0.02, abs=1e-15)


# ---------------------------------------------------------------------------
# Complexity Emergence Score: logistic fit + AIC model selection + scalings
# ---------------------------------------------------------------------------


class TestCESIntermediates:
    def _series(self):
        x = np.array([2.0, 3.0, 4.0, 5.0])
        # AI series built from SHARP_SERIES (reused fixture).
        y = np.array([float(_cai(SHARP_SERIES[int(n)])) for n in x])
        return x, y

    def test_ai_series_matches_expected(self):
        _, y = self._series()
        expected = [0.73852295, 0.72709163, 0.81845238, 0.89197835]
        assert y == pytest.approx(expected, abs=1e-6)

    def test_logistic_fit_parameters(self):
        x, y = self._series()
        fit = _fit_logistic_emergence(x, y)
        p = fit["parameters"]
        # regression-locked (optimizer output)
        assert p["amplitude"] == pytest.approx(0.15918138573734011, rel=1e-3)
        assert p["sharpness"] == pytest.approx(9.999999914979135, rel=1e-3)
        assert p["threshold"] == pytest.approx(3.9847502592935484, rel=1e-3)
        assert p["baseline"] == pytest.approx(0.7328035174867374, rel=1e-3)
        assert fit["r_squared"] == pytest.approx(0.99631402652948, rel=1e-3)

    def test_best_model_is_logistic_with_locked_aic(self):
        x, y = self._series()
        best = _fit_best_emergence_model(x, y)
        assert best["model"] == "logistic"
        # regression-locked (optimizer output)
        assert best["aic"] == pytest.approx(-36.08306419222251, rel=1e-3)

    def test_linear_and_power_law_ces_scalings(self):
        x, y = self._series()
        lin = _fit_emergence_model(x, y, "linear")
        pl = _fit_emergence_model(x, y, "power_law")
        # CES scalings: linear -> |slope|*0.1, power_law -> alpha*A*0.1.
        # regression-locked (optimizer output)
        assert _calculate_ces_from_fit(lin, "linear") == pytest.approx(
            0.005517269245808753, rel=1e-3
        )
        assert _calculate_ces_from_fit(pl, "power_law") == pytest.approx(
            0.00026620528346171817, rel=1e-3
        )


# ---------------------------------------------------------------------------
# Entanglement-Error Correlation: topology / error / k-way intermediates
# ---------------------------------------------------------------------------


def _upper_triangle(m: np.ndarray) -> np.ndarray:
    n = m.shape[0]
    mask = np.triu(np.ones((n, n), dtype=bool), k=1)
    return m[mask]


class TestEECIntermediates:
    def test_ghz_topology_upper_triangle_ring_wrap(self):
        W = _construct_entanglement_topology(4, "GHZ", {})
        ut = _upper_triangle(W)
        # Ring distances: (0,1)=1,(0,2)=2,(0,3)=1 [wrap],(1,2)=1,(1,3)=2,(2,3)=1.
        expected = [
            0.36787944117144233,  # e^-1  (0,1)
            0.1353352832366127,  # e^-2  (0,2)
            0.36787944117144233,  # e^-1  (0,3) ring wrap
            0.36787944117144233,  # e^-1  (1,2)
            0.1353352832366127,  # e^-2  (1,3)
            0.36787944117144233,  # e^-1  (2,3)
        ]
        assert ut.tolist() == pytest.approx(expected, abs=1e-12)

    def test_error_correlation_matrix_upper_triangle(self):
        E = _compute_error_correlation_matrix(STRUCTURED_4Q, 4, ALPHA)
        ut = _upper_triangle(E)
        expected = [
            0.988612134,
            0.276875916,
            0.276875916,
            0.276875916,
            0.276875916,
            0.988612134,
        ]
        assert ut.tolist() == pytest.approx(expected, abs=1e-6)

    def test_kway_entanglement_weights(self):
        assert _compute_kway_entanglement_weight((0, 1), "GHZ", 4) == pytest.approx(
            0.36787944117144233, abs=1e-15
        )
        assert _compute_kway_entanglement_weight((0, 2), "GHZ", 4) == pytest.approx(
            0.1353352832366127, abs=1e-15
        )
        assert _compute_kway_entanglement_weight((0, 1, 2), "GHZ", 4) == pytest.approx(
            0.2635971381157268, abs=1e-15
        )

    def test_kway_error_frequencies(self):
        assert _compute_kway_error_frequency((0, 1), STRUCTURED_4Q) == pytest.approx(0.0, abs=1e-15)
        assert _compute_kway_error_frequency((0, 2), STRUCTURED_4Q) == pytest.approx(0.2, abs=1e-15)

    def test_multiway_correlation_zero_variance(self):
        out = compute_multiway_entanglement_correlation(
            {"000": 400, "111": 400, "010": 100, "101": 100}, "GHZ", 3
        )
        assert out == {2: 0.0, 3: 0.0}


# ---------------------------------------------------------------------------
# Noise Topology Correlation: effect_size + excess means + p-value
# ---------------------------------------------------------------------------


def _ntc_baseline_3q():
    return {format(i, "03b"): 125 for i in range(8)}


def _ntc_correlated_3q():
    counts = {}
    for i in range(8):
        bs = format(i, "03b")
        counts[bs] = 200 if bs[0] == bs[1] else 50
    return counts


class TestNoiseTopologyIntermediates:
    def test_effect_size_and_excess_means(self):
        W = np.zeros((3, 3))
        W[0, 1] = W[1, 0] = 1.0
        res = noise_topology_correlation(
            _ntc_correlated_3q(),
            _ntc_baseline_3q(),
            W,
            3,
            rng=np.random.default_rng(0),
        )
        # Effect size standardizes observed selectivity against the permutation
        # null; for this exhaustive (3! = 6) test it equals sqrt(2).
        assert res["effect_size"] == pytest.approx(np.sqrt(2), abs=1e-12)
        assert res["edge_excess_mean"] == pytest.approx(0.15, abs=1e-12)
        assert res["non_edge_excess_mean"] == pytest.approx(0.0, abs=1e-12)
        # Exhaustive permutation p-value = 2/6.
        assert res["p_value"] == pytest.approx(1.0 / 3.0, abs=1e-12)


# ---------------------------------------------------------------------------
# Temporal Pathway Stability: partial stability + persistence + transitions
# ---------------------------------------------------------------------------


class TestTemporalIntermediates:
    def test_partial_stability_value(self):
        rankings = [
            ["a", "b", "c", "d", "e"],
            ["a", "b", "c", "d", "e"],
            ["a", "b", "d", "c", "e"],  # last two swapped
        ]
        tps = compute_temporal_pathway_stability(rankings)
        assert tps == pytest.approx(0.9473684210526315, abs=1e-12)

    def test_pathway_persistence_scores(self):
        scores = compute_pathway_persistence_scores(
            [["a", "b", "c"], ["a", "c", "b"], ["a", "b", "c"]]
        )
        assert scores["a"] == pytest.approx(1.0, abs=1e-12)
        assert scores["b"] == pytest.approx(0.6464466094067263, abs=1e-12)
        assert scores["c"] == pytest.approx(0.7171572875253810, abs=1e-12)

    def test_temporal_transition_matrix(self):
        T = compute_temporal_transition_matrix(
            [["a", "b", "c"], ["a", "c", "b"], ["b", "a", "c"]], top_k=2
        )
        expected = np.array([[0.5, 0.5, 0.0], [0.0, 0.0, 1.0], [0.5, 0.5, 0.0]])
        assert T == pytest.approx(expected, abs=1e-12)
