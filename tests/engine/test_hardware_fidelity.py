"""Tests for counts-based fidelity estimation (hardware mode)."""

from src.engine.fidelity import _compute_fidelity_from_counts


class TestCountsBasedFidelity:
    """Test Bhattacharyya coefficient fidelity from measurement counts."""

    def test_perfect_ghz_2qubit(self):
        """Perfect GHZ counts give fidelity near 1.0."""
        counts = {"00": 5000, "11": 5000}
        f = _compute_fidelity_from_counts(counts, "GHZ", 2)
        assert f is not None
        assert f > 0.95

    def test_perfect_ghz_3qubit(self):
        """Perfect 3-qubit GHZ counts give fidelity near 1.0."""
        counts = {"000": 5000, "111": 5000}
        f = _compute_fidelity_from_counts(counts, "GHZ", 3)
        assert f is not None
        assert f > 0.95

    def test_uniform_random_low_fidelity(self):
        """Uniform random counts should give low fidelity for GHZ."""
        counts = {f"{i:03b}": 125 for i in range(8)}
        f = _compute_fidelity_from_counts(counts, "GHZ", 3)
        assert f is not None
        assert f < 0.6

    def test_noisy_ghz(self):
        """Noisy GHZ (some errors) gives intermediate fidelity."""
        counts = {"00": 4000, "11": 4000, "01": 500, "10": 500}
        f = _compute_fidelity_from_counts(counts, "GHZ", 2)
        assert f is not None
        assert 0.6 < f < 1.0

    def test_empty_counts_returns_none(self):
        """Empty counts dict returns None."""
        f = _compute_fidelity_from_counts({}, "GHZ", 2)
        assert f is None

    def test_zero_total_shots_returns_none(self):
        """Zero-count entries sum to 0 → None."""
        f = _compute_fidelity_from_counts({"00": 0, "11": 0}, "GHZ", 2)
        assert f is None

    def test_fidelity_bounded_0_1(self):
        """Fidelity must always be in [0, 1]."""
        for counts in [
            {"00": 100, "11": 100},
            {"000": 1000},
            {"01": 50, "10": 50, "00": 50, "11": 50},
        ]:
            n = len(next(iter(counts)))
            f = _compute_fidelity_from_counts(counts, "GHZ", n)
            if f is not None:
                assert 0.0 <= f <= 1.0

    def test_superposition_state(self):
        """Superposition state: all outcomes equally likely → high fidelity when uniform."""
        counts = {f"{i:02b}": 250 for i in range(4)}
        f = _compute_fidelity_from_counts(counts, "SUPERPOSITION", 2)
        assert f is not None
        assert f > 0.9
