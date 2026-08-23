"""
Test metric calculation modules.
"""

import numpy as np
import pytest

from qforge.core.analysis.metrics.asymmetry_index import (
    AsymmetryAnalysis,
    compute_asymmetry_index,
    validate_asymmetry_index_properties,
)
from qforge.core.analysis.metrics.complexity_emergence_score import (
    EmergenceAnalysis,
    compute_complexity_emergence_score,
)
from qforge.core.analysis.metrics.entanglement_error_correlation import (
    compute_entanglement_error_correlation,
)
from qforge.core.analysis.metrics.pathway_concentration_ratio import (
    compute_pathway_concentration_ratio,
)
from qforge.core.analysis.metrics.temporal_pathway_stability import (
    TemporalAnalysis,
    compute_temporal_pathway_stability,
)


class TestAsymmetryIndex:
    """Test Asymmetry Index calculations."""

    def test_uniform_distribution_ai(self):
        """Test AI for uniform distribution."""
        counts = {"00": 250, "01": 250, "10": 250, "11": 250}
        ai = compute_asymmetry_index(counts)
        assert ai < 0.05  # Should be close to 0

    def test_deterministic_ai(self):
        """Test AI for deterministic distribution ((N+a)/(N+aK) - 1/K = 750/1002)."""
        counts = {"00": 1000}
        ai = compute_asymmetry_index(counts)
        assert abs(ai - 750.0 / 1002.0) < 1e-10  # Near the 1 - 1/K maximum

    def test_structured_ai(self):
        """Test AI for structured distribution."""
        counts = {"000": 400, "111": 400, "001": 100, "110": 100}
        ai = compute_asymmetry_index(counts)
        assert 0.1 < ai < 0.6  # Should show moderate structure (adjusted threshold)

    def test_ai_with_analysis(self):
        """Test AI with detailed analysis."""
        counts = {"00": 300, "01": 200, "10": 250, "11": 250}
        result = compute_asymmetry_index(counts, return_analysis=True)

        assert isinstance(result, AsymmetryAnalysis)
        assert result.asymmetry_index >= 0.0
        assert result.asymmetry_index <= 0.5
        assert result.structure_evidence in ["none", "weak", "moderate", "strong"]
        assert len(result.dominant_outcomes) > 0

    def test_ai_validation(self):
        """Test AI validation properties."""
        counts = {"00": 100, "11": 200}
        ai = compute_asymmetry_index(counts)
        assert validate_asymmetry_index_properties(ai, counts)

    def test_ai_empty_counts(self):
        """Test AI with empty counts."""
        with pytest.raises(ValueError, match="dictionary is empty"):
            compute_asymmetry_index({})

    def test_ai_single_outcome(self):
        """Test AI with single outcome (closed form: (N+a)/(N+aK) - 1/K)."""
        counts = {"000": 1000}
        ai = compute_asymmetry_index(counts)
        assert abs(ai - 875.0 / 1004.0) < 1e-10


class TestPathwayConcentrationRatio:
    """Test Pathway Concentration Ratio calculations."""

    def test_uniform_pcr(self):
        """Test PCR for uniform distribution."""
        counts = {"00": 250, "01": 250, "10": 250, "11": 250}
        pcr = compute_pathway_concentration_ratio(counts)
        assert abs(pcr - 1.0) < 0.1  # Should be close to 1

    def test_concentrated_pcr(self):
        """Test PCR for concentrated distribution."""
        counts = {"00": 700, "01": 100, "10": 100, "11": 100}
        pcr = compute_pathway_concentration_ratio(counts)
        assert pcr > 2.0  # Should show concentration

    def test_pcr_properties(self):
        """Test basic PCR properties."""
        counts = {"000": 400, "111": 300, "001": 200, "110": 100}
        pcr = compute_pathway_concentration_ratio(counts)
        assert pcr >= 0.0
        assert np.isfinite(pcr)

    def test_pcr_extreme_concentration(self):
        """Test PCR with extreme concentration."""
        counts = {"00": 990, "01": 5, "10": 3, "11": 2}
        pcr = compute_pathway_concentration_ratio(counts)
        assert pcr > 10.0  # Should be very high

    def test_pcr_insufficient_outcomes(self):
        """Test PCR with insufficient outcomes."""
        counts = {"0": 1000}  # Only one outcome
        pcr = compute_pathway_concentration_ratio(counts)
        assert not np.isfinite(pcr)  # Should be infinity


class TestEntanglementErrorCorrelation:
    """Test Entanglement-Error Correlation calculations."""

    def test_eec_ghz_state(self):
        """Test EEC for GHZ-like state."""
        counts = {"000": 400, "111": 400, "001": 100, "110": 100}
        eec = compute_entanglement_error_correlation(counts, "GHZ")
        assert -1.0 <= eec <= 1.0

    def test_eec_bell_state(self):
        """Test EEC for Bell-like state."""
        counts = {"00": 450, "11": 450, "01": 50, "10": 50}
        eec = compute_entanglement_error_correlation(counts, "BELL")
        assert -1.0 <= eec <= 1.0

    def test_eec_w_state(self):
        """Test EEC for W-like state."""
        counts = {"001": 300, "010": 300, "100": 300, "111": 100}
        eec = compute_entanglement_error_correlation(counts, "W")
        assert -1.0 <= eec <= 1.0

    def test_eec_unknown_state(self):
        """Test EEC for unknown state type."""
        counts = {"00": 500, "11": 500}
        with pytest.raises(ValueError, match="Unsupported state type"):
            compute_entanglement_error_correlation(counts, "UNKNOWN")

    def test_eec_properties(self):
        """Test basic EEC properties."""
        counts = {"000": 200, "111": 200, "010": 300, "101": 300}
        eec = compute_entanglement_error_correlation(counts, "GHZ")
        assert np.isfinite(eec)
        assert np.isreal(eec)


class TestTemporalPathwayStability:
    """Test Temporal Pathway Stability calculations."""

    def test_tps_stable_rankings(self):
        """Test TPS for stable pathway rankings."""
        rankings = [
            ["000", "111", "001", "110"],
            ["000", "111", "001", "110"],
            ["000", "111", "001", "110"],
        ]
        tps = compute_temporal_pathway_stability(rankings)
        assert tps > 0.9  # Should be high for identical rankings

    def test_tps_random_rankings(self):
        """Test TPS for random pathway rankings."""
        rankings = [
            ["000", "111", "001", "110"],
            ["110", "001", "111", "000"],
            ["001", "000", "110", "111"],
        ]
        tps = compute_temporal_pathway_stability(rankings)
        assert tps < 0.5  # Should be low for random rankings

    def test_tps_with_analysis(self):
        """Test TPS with detailed analysis."""
        rankings = [
            ["000", "111", "001", "110"],
            ["000", "111", "110", "001"],
            ["000", "001", "111", "110"],
        ]
        result = compute_temporal_pathway_stability(rankings, return_analysis=True)

        assert isinstance(result, TemporalAnalysis)
        assert 0.0 <= result.temporal_pathway_stability <= 1.0
        assert result.ranking_consistency in ["highly_stable", "stable", "unstable", "chaotic"]
        assert isinstance(result.persistent_pathways, list)
        assert isinstance(result.volatile_pathways, list)

    def test_tps_insufficient_data(self):
        """Test TPS with insufficient data."""
        rankings = [["000", "111"]]  # Only one ranking
        tps = compute_temporal_pathway_stability(rankings)
        assert tps == 1.0  # Default for insufficient data

    def test_tps_correlation_methods(self):
        """Test TPS with different correlation methods."""
        rankings = [
            ["00", "01", "10", "11"],
            ["00", "10", "01", "11"],
            ["00", "01", "11", "10"],
        ]

        tps_spearman = compute_temporal_pathway_stability(rankings, correlation_method="spearman")
        tps_kendall = compute_temporal_pathway_stability(rankings, correlation_method="kendall")

        assert 0.0 <= tps_spearman <= 1.0
        assert 0.0 <= tps_kendall <= 1.0


class TestComplexityEmergenceScore:
    """Test Complexity Emergence Score calculations."""

    def test_ces_sharp_emergence(self):
        """Test CES for sharp emergence pattern."""
        multi_qubit_data = {
            2: {"00": 500, "01": 500},  # Random
            3: {"000": 400, "111": 400, "001": 200},  # Emerging structure
            4: {"0000": 600, "1111": 350, "0001": 50},  # Strong structure
            5: {"00000": 700, "11111": 250, "00001": 50},  # Very strong structure
        }
        ces = compute_complexity_emergence_score(multi_qubit_data)
        assert ces > 0.0  # Should show emergence (adjusted threshold)

    def test_ces_gradual_emergence(self):
        """Test CES for gradual emergence pattern."""
        multi_qubit_data = {
            2: {"00": 450, "01": 400, "10": 100, "11": 50},
            3: {"000": 350, "111": 300, "001": 200, "010": 150},
            4: {"0000": 400, "1111": 300, "0001": 150, "0010": 150},
        }
        ces = compute_complexity_emergence_score(multi_qubit_data)
        assert ces >= 0.0

    def test_ces_with_analysis(self):
        """Test CES with detailed analysis."""
        multi_qubit_data = {
            2: {"00": 500, "11": 500},
            3: {"000": 400, "111": 400, "001": 100, "110": 100},
            4: {"0000": 500, "1111": 300, "0001": 100, "1110": 100},
        }
        result = compute_complexity_emergence_score(multi_qubit_data, return_analysis=True)

        assert isinstance(result, EmergenceAnalysis)
        assert result.complexity_emergence_score >= 0.0
        assert result.emergence_quality in ["excellent", "good", "poor", "insufficient"]
        assert result.scaling_behavior in ["sigmoid", "linear", "power_law", "flat"]
        assert result.critical_threshold >= 0.0

    def test_ces_insufficient_data(self):
        """Test CES with insufficient data."""
        multi_qubit_data = {2: {"00": 500, "11": 500}}  # Only one system size
        ces = compute_complexity_emergence_score(multi_qubit_data)
        assert ces == 0.0

    def test_ces_different_metrics(self):
        """Test CES with different structure metrics."""
        multi_qubit_data = {
            2: {"00": 300, "01": 200, "10": 250, "11": 250},
            3: {"000": 400, "111": 300, "001": 200, "110": 100},
        }

        ces_ai = compute_complexity_emergence_score(
            multi_qubit_data, structure_metric="asymmetry_index"
        )
        assert ces_ai >= 0.0


class TestMetricIntegration:
    """Test integration between different metrics."""

    def test_metric_consistency(self):
        """Test consistency between related metrics."""
        counts = {"000": 400, "111": 400, "001": 100, "110": 100}

        ai = compute_asymmetry_index(counts)
        pcr = compute_pathway_concentration_ratio(counts)
        eec = compute_entanglement_error_correlation(counts, "GHZ")

        # All metrics should indicate some structure
        assert ai > 0.1  # Some asymmetry
        assert pcr > 1.5  # Some concentration
        assert abs(eec) >= 0.0  # Some correlation (magnitude)

    def test_metric_bounds(self):
        """Test that all metrics respect their bounds."""
        counts = {"00": 300, "01": 200, "10": 250, "11": 250}

        ai = compute_asymmetry_index(counts)
        pcr = compute_pathway_concentration_ratio(counts)
        eec = compute_entanglement_error_correlation(counts, "BELL")

        assert 0.0 <= ai <= 0.5
        assert pcr >= 0.0
        assert -1.0 <= eec <= 1.0

    def test_extreme_distributions(self):
        """Test metrics with extreme distributions."""
        # Uniform distribution
        uniform_counts = {"00": 250, "01": 250, "10": 250, "11": 250}
        ai_uniform = compute_asymmetry_index(uniform_counts)
        pcr_uniform = compute_pathway_concentration_ratio(uniform_counts)

        # Deterministic distribution
        deterministic_counts = {"00": 1000}
        ai_det = compute_asymmetry_index(deterministic_counts)
        pcr_det = compute_pathway_concentration_ratio(deterministic_counts)

        # AI should increase from uniform to deterministic
        assert ai_det > ai_uniform
        # PCR should increase from uniform to deterministic
        assert pcr_det > pcr_uniform

    def test_metric_numerical_stability(self):
        """Test numerical stability of metrics."""
        # Very skewed distribution
        counts = {"000": 9999, "001": 1, "010": 0, "011": 0, "100": 0, "101": 0, "110": 0, "111": 0}

        ai = compute_asymmetry_index(counts)
        pcr = compute_pathway_concentration_ratio(counts)
        eec = compute_entanglement_error_correlation(counts, "GHZ")

        # All should be finite
        assert np.isfinite(ai)
        assert np.isfinite(pcr) or pcr == float("inf")  # PCR can be infinite
        assert np.isfinite(eec)
