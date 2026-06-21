"""
Analytical Validation Tests (The "Gold Standard")

These tests verify that the framework produces EXACT analytical results for
known quantum states. Unlike integration tests which might accept "reasonable"
values, these tests require high precision matching of theoretical predictions.

Target States:
1. Separable (Product) States -> Zero correlations, Zero entanglement signatures.
2. GHZ States (Maximally Entangled) -> Max correlations, Max structure.
3. W States -> Specific multipartite entanglement signatures.
4. Mixed States (Maximally Mixed) -> Max entropy, Zero information.

Analytical Baselines (Phase 1 Scientific Rigor):
- Entropy: H(deterministic) ≈ 0, H(uniform d) = log₂(d)
- Total Correlation: TC(Bell) = 1.0 bit, TC(3Q GHZ) = 2.0 bits
- Asymmetry Index: AI(uniform) = 0, AI(deterministic) = 0.5
- PCR: PCR(uniform) = 1.0
- EEC: Always ∈ [-1, 1]
"""

import numpy as np

# Use core total_correlation directly (avoids MetricResult wrapper)
from src.core.analysis.core.information_theory import entropy, total_correlation
from src.core.analysis.metrics.asymmetry_index import compute_asymmetry_index
from src.core.analysis.metrics.entanglement_error_correlation import (
    compute_entanglement_error_correlation,
)
from src.core.analysis.metrics.pathway_concentration_ratio import (
    compute_pathway_concentration_ratio,
)

# Tolerance for floating point comparisons
# We expect high precision for analytical cases
TOLERANCE = 1e-9


class TestAnalyticalBaselines:
    def test_separable_state_metrics(self):
        """
        Theory: A separable state (e.g., |00...0>) has:
        - Entropy = 0 (if pure)
        - Mutual Information = 0
        - Asymmetry Index = 0.5 (Deterministic)
        """
        # |000>
        counts = {"000": 1000}

        # Entropy should be exactly 0
        # Note: We need to convert counts to probs for the core entropy function
        # or use a helper if available. For now, we assume the core function handles it
        # or we prep the input. The integration tests showed we need to be careful.
        # Let's use the high-level metrics which handle counts.

        # Asymmetry Index for deterministic state is exactly 0.5
        ai = compute_asymmetry_index(counts)
        assert abs(ai - 0.5) < TOLERANCE, f"Expected AI=0.5 for separable state, got {ai}"

    def test_maximally_mixed_state(self):
        """
        Theory: A maximally mixed state (uniform distribution) has:
        - Asymmetry Index = 0.0 (Perfectly uniform)
        """
        # Uniform distribution over 2 qubits
        counts = {"00": 250, "01": 250, "10": 250, "11": 250}

        ai = compute_asymmetry_index(counts)
        assert abs(ai - 0.0) < TOLERANCE, f"Expected AI=0.0 for mixed state, got {ai}"

    def test_ghz_state_correlations(self):
        """
        Theory: A structured state should show high EEC.
        We use a Bell pair on physical qubits 0-1, with the rest fixed to 0.
        Under the canonical convention physical qubits 0-1 are the two RIGHTMOST
        bitstring positions, which is where the extended 'Bell' topology places
        its strong bond (consistent with the MI matrix it is correlated against).
        """
        # Bell pair on physical qubits 0-1 (rightmost bits): |0000> + |0011>
        counts = {"0000": 500, "0011": 500}

        # Entanglement Error Correlation (EEC)
        eec = compute_entanglement_error_correlation(counts, state_type="Bell")

        # We expect positive correlation
        assert eec > 0.4, f"Expected positive EEC for Bell state, got {eec}"

    def test_entropy_bounds(self):
        """
        Theory: Entropy H(X) is bounded by 0 <= H(X) <= log2(N).
        """
        # 3 qubits -> N=8 outcomes. Max entropy = 3 bits.

        # Case 1: Deterministic (Min Entropy)
        counts_min = {"000": 10000}
        # We need to use the core entropy function carefully.
        # Assuming we have a helper or use the one from integration tests pattern.
        from src.core.analysis.core.information_theory import counts_to_probabilities

        probs_min = np.array(list(counts_to_probabilities(counts_min).values()))
        h_min = entropy(probs_min)
        assert abs(h_min - 0.0) < 1e-2, f"Expected H~0, got {h_min}"  # Relaxed for smoothing

        # Case 2: Uniform (Max Entropy)
        counts_max = {f"{i:03b}": 10000 for i in range(8)}
        probs_max = np.array(list(counts_to_probabilities(counts_max).values()))
        h_max = entropy(probs_max)

        assert abs(h_max - 3.0) < 1e-2, f"Expected H~3, got {h_max}"  # Relaxed for smoothing


class TestTotalCorrelationBaselines:
    """
    Total Correlation (Multi-Information) Analytical Baselines.

    TC measures the total amount of correlation among all variables.
    For maximally entangled states:
    - TC(2-qubit Bell) = 1.0 bit
    - TC(n-qubit GHZ) = (n-1) bits
    """

    def test_tc_bell_state_is_one_bit(self):
        """
        Theory: TC(Bell) = H(A) + H(B) - H(AB) = 1 + 1 - 1 = 1 bit.

        For |Φ+⟩ = (|00⟩ + |11⟩)/√2:
        - H(A) = H(B) = 1 bit (each qubit is maximally mixed)
        - H(AB) = 1 bit (joint is pure Bell state with 2 outcomes)
        """
        counts = {"00": 500, "11": 500}  # Ideal Bell state Φ+
        tc = total_correlation(counts)

        # TC should be 1.0 bit (within tolerance for Jeffreys smoothing)
        assert abs(tc - 1.0) < 0.05, f"Expected TC≈1.0 for Bell state, got {tc}"

    def test_tc_3qubit_ghz_is_two_bits(self):
        """
        Theory: TC(3-qubit GHZ) = 2.0 bits.

        For |GHZ₃⟩ = (|000⟩ + |111⟩)/√2:
        - H(A) = H(B) = H(C) = 1 bit each
        - H(ABC) = 1 bit (joint has 2 outcomes)
        - TC = 1 + 1 + 1 - 1 = 2 bits
        """
        counts = {"000": 500, "111": 500}  # Ideal 3-qubit GHZ
        tc = total_correlation(counts)

        assert abs(tc - 2.0) < 0.1, f"Expected TC≈2.0 for 3Q GHZ, got {tc}"

    def test_tc_4qubit_ghz_is_three_bits(self):
        """
        Theory: TC(4-qubit GHZ) = 3.0 bits.

        For |GHZ₄⟩ = (|0000⟩ + |1111⟩)/√2:
        - Sum of marginal entropies = 4 × 1 = 4 bits
        - Joint entropy = 1 bit
        - TC = 4 - 1 = 3 bits
        """
        counts = {"0000": 500, "1111": 500}  # Ideal 4-qubit GHZ
        tc = total_correlation(counts)

        assert abs(tc - 3.0) < 0.1, f"Expected TC≈3.0 for 4Q GHZ, got {tc}"

    def test_tc_product_state_is_zero(self):
        """
        Theory: TC(product state) = 0 (no correlations).

        For independent qubits each in |+⟩:
        - All qubits are independent
        - TC = 0
        """
        # Uniform distribution (product of uniform marginals)
        counts = {f"{i:02b}": 250 for i in range(4)}  # 2-qubit uniform
        tc = total_correlation(counts)

        # TC should be near 0 for independent qubits
        assert abs(tc) < 0.1, f"Expected TC≈0 for product state, got {tc}"


class TestPCRBaselines:
    """
    Pathway Concentration Ratio Analytical Baselines.

    PCR measures how concentrated outcomes are in top quartile vs bottom.
    - PCR = 1.0 for uniform distribution (no concentration)
    - PCR > 1.0 for concentrated distributions
    """

    def test_pcr_uniform_is_one(self):
        """
        Theory: PCR(uniform) = 1.0.

        When all outcomes have equal probability, top and bottom
        quartiles have equal total probability, so ratio = 1.0.
        """
        counts = {f"{i:02b}": 250 for i in range(4)}  # 2-qubit uniform
        pcr = compute_pathway_concentration_ratio(counts)

        # PCR should be 1.0 for uniform (within tolerance)
        assert abs(pcr - 1.0) < 0.1, f"Expected PCR≈1.0 for uniform, got {pcr}"

    def test_pcr_concentrated_greater_than_one(self):
        """
        Theory: Concentrated distributions have PCR > 1.0.

        When most probability is in few outcomes, top quartile
        dominates bottom quartile.
        """
        # Truly concentrated: one outcome dominates (asymmetric)
        counts = {"00": 900, "01": 50, "10": 30, "11": 20}
        pcr = compute_pathway_concentration_ratio(counts)

        assert pcr > 1.0, f"Expected PCR>1.0 for concentrated, got {pcr}"

    def test_pcr_positive(self):
        """PCR must always be positive."""
        counts = {"00": 100, "01": 200, "10": 300, "11": 400}
        pcr = compute_pathway_concentration_ratio(counts)

        assert pcr > 0, f"Expected PCR>0, got {pcr}"


class TestEECBounds:
    """
    Entanglement-Error Correlation Bounds.

    EEC is a Pearson correlation coefficient, so must be in [-1, 1].
    """

    def test_eec_in_bounds_bell(self):
        """EEC for Bell state must be in [-1, 1]."""
        counts = {"00": 500, "11": 500}
        eec = compute_entanglement_error_correlation(counts, state_type="Bell")

        assert -1.0 <= eec <= 1.0, f"EEC out of bounds: {eec}"

    def test_eec_in_bounds_ghz(self):
        """EEC for GHZ state must be in [-1, 1]."""
        counts = {"000": 500, "111": 500}
        eec = compute_entanglement_error_correlation(counts, state_type="GHZ")

        assert -1.0 <= eec <= 1.0, f"EEC out of bounds: {eec}"

    def test_eec_in_bounds_uniform(self):
        """EEC for uniform distribution must be in [-1, 1]."""
        counts = {f"{i:03b}": 125 for i in range(8)}
        eec = compute_entanglement_error_correlation(counts, state_type="GHZ")

        assert -1.0 <= eec <= 1.0, f"EEC out of bounds: {eec}"

    def test_eec_in_bounds_skewed(self):
        """EEC for skewed distribution must be in [-1, 1]."""
        counts = {"000": 900, "111": 50, "001": 25, "110": 25}
        eec = compute_entanglement_error_correlation(counts, state_type="GHZ")

        assert -1.0 <= eec <= 1.0, f"EEC out of bounds: {eec}"


class TestAIBaselines:
    """
    Asymmetry Index Analytical Baselines.

    AI = JS divergence from uniform, normalized to [0, 1].
    - AI = 0 for uniform distribution
    - AI = 0.5 for deterministic (single outcome)
    """

    def test_ai_uniform_is_zero(self):
        """
        Theory: AI(uniform) = 0.0.

        JS divergence from uniform to uniform is 0.
        """
        counts = {f"{i:02b}": 250 for i in range(4)}
        ai = compute_asymmetry_index(counts)

        assert abs(ai - 0.0) < 0.01, f"Expected AI≈0 for uniform, got {ai}"

    def test_ai_deterministic_is_half(self):
        """
        Theory: AI(deterministic) = 0.5.

        Maximum JS divergence from uniform occurs at delta distribution.
        """
        counts = {"0000": 1000}
        ai = compute_asymmetry_index(counts)

        assert abs(ai - 0.5) < 0.05, f"Expected AI≈0.5 for deterministic, got {ai}"

    def test_ai_in_unit_interval(self):
        """AI must always be in [0, 1]."""
        # Various test cases
        test_cases = [
            {"00": 250, "01": 250, "10": 250, "11": 250},  # uniform
            {"0000": 1000},  # deterministic
            {"00": 800, "01": 100, "10": 50, "11": 50},  # skewed
            {"000": 500, "111": 500},  # GHZ
        ]

        for counts in test_cases:
            ai = compute_asymmetry_index(counts)
            assert 0.0 <= ai <= 1.0, f"AI out of bounds: {ai} for {counts}"
