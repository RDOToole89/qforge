"""
Property-Based Tests for Metric Invariants

Uses the hypothesis library to test mathematical invariants that must hold
for ALL valid inputs, not just specific test cases. This provides much
stronger guarantees than example-based testing.

Invariants Tested:
- Entropy: H(p) >= 0, H(p) <= log₂(d)
- Mutual Information: MI(X;Y) >= 0, MI(A;B) == MI(B;A)
- Asymmetry Index: AI ∈ [0, 1]
- PCR: PCR > 0 for non-degenerate distributions
- EEC: EEC ∈ [-1, 1]
"""

import math

import numpy as np
from hypothesis import given, settings
from hypothesis import strategies as st

from src.core.analysis.core.information_theory import (
    counts_to_probabilities,
    entropy,
    mutual_information,
)
from src.core.analysis.metrics.asymmetry_index import compute_asymmetry_index
from src.core.analysis.metrics.entanglement_error_correlation import (
    compute_entanglement_error_correlation,
)
from src.core.analysis.metrics.pathway_concentration_ratio import (
    compute_pathway_concentration_ratio,
)

# =============================================================================
# Hypothesis Strategies for Quantum Measurement Data
# =============================================================================


@st.composite
def measurement_counts(
    draw, min_qubits=2, max_qubits=4, min_total=100, max_total=10000, min_outcomes=1
):
    """
    Generate valid quantum measurement counts.

    Creates a dict {bitstring: count} where bitstrings are n-qubit binary strings
    and counts are non-negative integers summing to at least min_total.

    Args:
        min_outcomes: Minimum number of distinct outcomes (default 1)
    """
    n_qubits = draw(st.integers(min_value=min_qubits, max_value=max_qubits))
    n_outcomes = 2**n_qubits

    # Generate counts for each possible outcome
    # Use a mix of zero and non-zero counts for realistic sparsity
    counts_list = draw(
        st.lists(
            st.integers(min_value=0, max_value=max_total // 4),
            min_size=n_outcomes,
            max_size=n_outcomes,
        )
    )

    # Ensure at least min_total total counts
    total = sum(counts_list)
    if total < min_total:
        # Add enough to the first non-zero index (or index 0)
        deficit = min_total - total
        idx = next((i for i, c in enumerate(counts_list) if c > 0), 0)
        counts_list[idx] += deficit

    # Build counts dict with proper bitstring keys
    counts = {}
    for i, count in enumerate(counts_list):
        if count > 0:
            key = format(i, f"0{n_qubits}b")
            counts[key] = count

    # Ensure at least one outcome
    if not counts:
        counts["0" * n_qubits] = min_total

    # Ensure minimum number of outcomes (for PCR tests that need >=2)
    while len(counts) < min_outcomes and len(counts) < n_outcomes:
        # Add a small count to a missing outcome
        for i in range(n_outcomes):
            key = format(i, f"0{n_qubits}b")
            if key not in counts:
                counts[key] = 10  # Small count
                break

    return counts


@st.composite
def measurement_counts_multiple_outcomes(draw, min_qubits=2, max_qubits=4):
    """Generate counts with at least 2 different outcomes (for PCR tests)."""
    return draw(measurement_counts(min_qubits=min_qubits, max_qubits=max_qubits, min_outcomes=2))


@st.composite
def probability_array(draw, min_size=2, max_size=16):
    """
    Generate valid probability distributions as numpy arrays.

    Ensures non-negative values that sum to 1.
    """
    size = draw(st.integers(min_value=min_size, max_value=max_size))

    # Generate raw values
    raw = draw(
        st.lists(
            st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
            min_size=size,
            max_size=size,
        )
    )

    # Normalize to sum to 1 (handle all-zero case)
    total = sum(raw)
    if total == 0:
        raw[0] = 1.0
        total = 1.0

    probs = np.array([r / total for r in raw])
    return probs


# =============================================================================
# Entropy Invariant Tests
# =============================================================================


class TestEntropyInvariants:
    """Mathematical invariants for Shannon entropy."""

    @given(probs=probability_array())
    @settings(max_examples=200)
    def test_entropy_non_negative(self, probs):
        """H(p) >= 0 for all probability distributions."""
        h = entropy(probs)
        assert h >= -1e-10, f"Entropy negative: {h}"

    @given(probs=probability_array())
    @settings(max_examples=200)
    def test_entropy_upper_bounded(self, probs):
        """H(p) <= log₂(d) where d = number of outcomes."""
        h = entropy(probs)
        d = len(probs)
        max_entropy = math.log2(d)
        assert h <= max_entropy + 0.01, f"Entropy {h} > max {max_entropy}"

    @given(counts=measurement_counts())
    @settings(max_examples=200)
    def test_entropy_from_counts_non_negative(self, counts):
        """H computed from counts is non-negative."""
        probs = np.array(list(counts_to_probabilities(counts).values()))
        h = entropy(probs)
        assert h >= -1e-10, f"Entropy from counts negative: {h}"


# =============================================================================
# Mutual Information Invariant Tests
# =============================================================================


class TestMutualInformationInvariants:
    """Mathematical invariants for mutual information."""

    @given(counts=measurement_counts(min_qubits=2, max_qubits=4))
    @settings(max_examples=100)
    def test_mi_non_negative(self, counts):
        """MI(X;Y) >= 0 for all X, Y."""
        mi = mutual_information(counts, 0, 1)  # qubit indices are ints
        assert mi >= -1e-10, f"MI negative: {mi}"

    @given(counts=measurement_counts(min_qubits=2, max_qubits=4))
    @settings(max_examples=100)
    def test_mi_symmetric(self, counts):
        """MI(A;B) == MI(B;A) - mutual information is symmetric."""
        mi_ab = mutual_information(counts, 0, 1)
        mi_ba = mutual_information(counts, 1, 0)
        assert abs(mi_ab - mi_ba) < 1e-10, f"MI not symmetric: {mi_ab} != {mi_ba}"

    @given(counts=measurement_counts(min_qubits=3, max_qubits=4))
    @settings(max_examples=50)
    def test_mi_different_pairs(self, counts):
        """MI for different qubit pairs is non-negative."""
        mi_01 = mutual_information(counts, 0, 1)
        mi_02 = mutual_information(counts, 0, 2)
        mi_12 = mutual_information(counts, 1, 2)
        assert mi_01 >= -1e-10, f"MI(0,1) negative: {mi_01}"
        assert mi_02 >= -1e-10, f"MI(0,2) negative: {mi_02}"
        assert mi_12 >= -1e-10, f"MI(1,2) negative: {mi_12}"


# =============================================================================
# Asymmetry Index Invariant Tests
# =============================================================================


class TestAsymmetryIndexInvariants:
    """Mathematical invariants for Asymmetry Index."""

    @given(counts=measurement_counts())
    @settings(max_examples=200)
    def test_ai_in_unit_interval(self, counts):
        """AI ∈ [0, 1] for all valid inputs."""
        ai = compute_asymmetry_index(counts)
        assert 0.0 <= ai <= 1.0, f"AI out of bounds: {ai}"

    @given(counts=measurement_counts())
    @settings(max_examples=200)
    def test_ai_is_finite(self, counts):
        """AI is always a finite number (no NaN or Inf)."""
        ai = compute_asymmetry_index(counts)
        assert math.isfinite(ai), f"AI not finite: {ai}"


# =============================================================================
# PCR Invariant Tests
# =============================================================================


class TestPCRInvariants:
    """Mathematical invariants for Pathway Concentration Ratio."""

    @given(counts=measurement_counts())
    @settings(max_examples=200)
    def test_pcr_positive(self, counts):
        """PCR > 0 for all distributions (may be infinite for single outcome)."""
        pcr = compute_pathway_concentration_ratio(counts)
        assert pcr > 0, f"PCR not positive: {pcr}"

    @given(counts=measurement_counts_multiple_outcomes())
    @settings(max_examples=200)
    def test_pcr_is_finite_with_multiple_outcomes(self, counts):
        """PCR is finite when there are at least 2 distinct outcomes."""
        pcr = compute_pathway_concentration_ratio(counts)
        assert math.isfinite(pcr), f"PCR not finite: {pcr}"

    def test_pcr_is_infinite_for_single_outcome(self):
        """PCR is infinity for single-outcome distributions (expected behavior)."""
        counts = {"00": 100}
        pcr = compute_pathway_concentration_ratio(counts)
        assert pcr == float("inf"), f"Expected PCR=inf for single outcome, got {pcr}"


# =============================================================================
# EEC Invariant Tests
# =============================================================================


class TestEECInvariants:
    """Mathematical invariants for Entanglement-Error Correlation."""

    @given(counts=measurement_counts(min_qubits=2, max_qubits=4))
    @settings(max_examples=100)
    def test_eec_in_correlation_bounds(self, counts):
        """EEC ∈ [-1, 1] as it's a Pearson correlation."""
        eec = compute_entanglement_error_correlation(counts, state_type="GHZ")
        assert -1.0 <= eec <= 1.0, f"EEC out of bounds: {eec}"

    @given(counts=measurement_counts(min_qubits=2, max_qubits=4))
    @settings(max_examples=100)
    def test_eec_is_finite(self, counts):
        """EEC is always a finite number."""
        eec = compute_entanglement_error_correlation(counts, state_type="GHZ")
        assert math.isfinite(eec), f"EEC not finite: {eec}"
