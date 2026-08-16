"""
Null Model Distribution Tests

Verify that metrics behave as expected under the null hypothesis (random/uniform
distributions). This validates that our metrics can distinguish structured data
from noise.

Key Tests:
- Asymmetry Index under null: Mean near 0, low variance
- Structure Score separation: Structured data >> null data
- Total Correlation under null: Near 0 for independent qubits
- Effect size: Cohen's d for structured vs null comparison

These tests ensure our metrics have discriminative power for publication.
"""

import numpy as np
import pytest

from src.core.analysis.core.information_theory import total_correlation
from src.core.analysis.metrics.asymmetry_index import compute_asymmetry_index


class TestNullModelAI:
    """Test Asymmetry Index under null hypothesis (uniform distributions)."""

    @pytest.mark.slow
    def test_ai_null_distribution_mean(self):
        """
        AI for uniform distributions should have mean near 0.

        Method:
        1. Generate N uniform distributions (null hypothesis)
        2. Compute AI for each
        3. Assert mean(AI) < threshold

        The null hypothesis is that data comes from a uniform distribution,
        which should have AI ≈ 0 (no asymmetry).
        """
        n_trials = 200
        n_qubits = 3
        n_shots = 1000
        rng = np.random.default_rng(42)

        ai_values = []

        for _ in range(n_trials):
            # Generate uniform distribution over all 2^n outcomes
            n_outcomes = 2**n_qubits
            # Multinomial with equal probabilities
            raw_counts = rng.multinomial(n_shots, [1 / n_outcomes] * n_outcomes)

            # Convert to counts dict
            counts = {format(i, f"0{n_qubits}b"): int(c) for i, c in enumerate(raw_counts) if c > 0}

            ai = compute_asymmetry_index(counts)
            ai_values.append(ai)

        mean_ai = np.mean(ai_values)

        # For uniform distributions, AI should be very close to 0
        assert mean_ai < 0.1, (
            f"Mean AI for null distribution too high: {mean_ai:.4f}. "
            f"Expected < 0.1 for uniform samples."
        )

    @pytest.mark.slow
    def test_ai_null_distribution_percentiles(self):
        """
        AI null distribution should have tight percentiles.

        Method:
        1. Generate N uniform distributions
        2. Compute AI for each
        3. Assert 90th percentile < threshold

        This ensures that even the "worst" random samples don't
        look too structured.
        """
        n_trials = 200
        n_qubits = 3
        n_shots = 1000
        rng = np.random.default_rng(123)

        ai_values = []

        for _ in range(n_trials):
            n_outcomes = 2**n_qubits
            raw_counts = rng.multinomial(n_shots, [1 / n_outcomes] * n_outcomes)
            counts = {format(i, f"0{n_qubits}b"): int(c) for i, c in enumerate(raw_counts) if c > 0}
            ai = compute_asymmetry_index(counts)
            ai_values.append(ai)

        p90 = np.percentile(ai_values, 90)

        # 90th percentile should still be low
        assert p90 < 0.15, (
            f"90th percentile of null AI too high: {p90:.4f}. Expected < 0.15 for uniform samples."
        )

    @pytest.mark.slow
    def test_ai_structured_vs_null_separation(self):
        """
        Structured data should have clearly higher AI than null.

        This is the key test for discriminative power: we need to
        distinguish structured quantum states from random noise.

        Method:
        1. Generate null samples (uniform)
        2. Generate structured samples (GHZ-like, biased)
        3. Compare distributions
        4. Assert clear separation (effect size)
        """
        n_trials = 100
        n_qubits = 3
        n_shots = 1000
        rng = np.random.default_rng(456)

        null_ai_values = []
        structured_ai_values = []

        for _ in range(n_trials):
            # Null: uniform distribution
            n_outcomes = 2**n_qubits
            null_counts = rng.multinomial(n_shots, [1 / n_outcomes] * n_outcomes)
            null_dict = {
                format(i, f"0{n_qubits}b"): int(c) for i, c in enumerate(null_counts) if c > 0
            }
            null_ai_values.append(compute_asymmetry_index(null_dict))

            # Structured: GHZ-like (mostly |000> and |111>)
            # With some noise
            ghz_probs = np.zeros(n_outcomes)
            ghz_probs[0] = 0.4  # |000>
            ghz_probs[-1] = 0.4  # |111>
            # Spread remaining 20% as noise
            remaining = 0.2 / (n_outcomes - 2)
            for i in range(1, n_outcomes - 1):
                ghz_probs[i] = remaining

            structured_counts = rng.multinomial(n_shots, ghz_probs)
            structured_dict = {
                format(i, f"0{n_qubits}b"): int(c) for i, c in enumerate(structured_counts) if c > 0
            }
            structured_ai_values.append(compute_asymmetry_index(structured_dict))

        mean_null = np.mean(null_ai_values)
        mean_structured = np.mean(structured_ai_values)

        # Compute effect size (Cohen's d)
        pooled_std = np.sqrt((np.var(null_ai_values) + np.var(structured_ai_values)) / 2)
        if pooled_std > 0:
            cohens_d = (mean_structured - mean_null) / pooled_std
        else:
            cohens_d = float("inf") if mean_structured > mean_null else 0

        # We want clear separation
        assert mean_structured > mean_null, (
            f"Structured AI ({mean_structured:.4f}) should exceed null AI ({mean_null:.4f})"
        )

        # Effect size should be large (d > 0.8 is "large" by convention)
        assert cohens_d > 0.8, (
            f"Effect size (Cohen's d) too small: {cohens_d:.2f}. "
            f"Expected > 0.8 for clear separation between structured and null."
        )


class TestNullModelTC:
    """Test Total Correlation under null hypothesis."""

    @pytest.mark.slow
    def test_tc_product_state_near_zero(self):
        """
        TC for product (independent) distributions should be near 0.

        Method:
        1. Generate product distributions (independent marginals)
        2. Compute TC for each
        3. Assert mean(TC) < threshold
        """
        n_trials = 100
        n_qubits = 2
        n_shots = 1000
        rng = np.random.default_rng(789)

        tc_values = []

        for _ in range(n_trials):
            # Generate product distribution
            # Each qubit independently 50/50
            outcomes = []
            for _ in range(n_shots):
                bits = "".join(str(rng.choice([0, 1])) for _ in range(n_qubits))
                outcomes.append(bits)

            # Count outcomes
            counts = {}
            for outcome in outcomes:
                counts[outcome] = counts.get(outcome, 0) + 1

            tc = total_correlation(counts)
            tc_values.append(tc)

        mean_tc = np.mean(tc_values)

        # TC should be near 0 for independent qubits
        assert mean_tc < 0.1, (
            f"Mean TC for product state too high: {mean_tc:.4f}. "
            f"Expected < 0.1 for independent qubits."
        )

    @pytest.mark.slow
    def test_tc_correlated_vs_product_separation(self):
        """
        Correlated states should have clearly higher TC than product states.
        """
        n_trials = 50
        n_qubits = 2
        n_shots = 1000
        rng = np.random.default_rng(101)

        product_tc_values = []
        correlated_tc_values = []

        for _ in range(n_trials):
            # Product: independent qubits
            outcomes = []
            for _ in range(n_shots):
                bits = "".join(str(rng.choice([0, 1])) for _ in range(n_qubits))
                outcomes.append(bits)
            product_counts = {}
            for outcome in outcomes:
                product_counts[outcome] = product_counts.get(outcome, 0) + 1
            product_tc_values.append(total_correlation(product_counts))

            # Correlated: Bell-like (00 and 11 only)
            bell_outcomes = rng.choice(["00", "11"], size=n_shots)
            bell_counts = {
                "00": int(np.sum(bell_outcomes == "00")),
                "11": int(np.sum(bell_outcomes == "11")),
            }
            correlated_tc_values.append(total_correlation(bell_counts))

        mean_product = np.mean(product_tc_values)
        mean_correlated = np.mean(correlated_tc_values)

        # Correlated should be much higher
        assert mean_correlated > mean_product + 0.5, (
            f"Correlated TC ({mean_correlated:.4f}) should exceed "
            f"product TC ({mean_product:.4f}) by at least 0.5 bits."
        )


class TestEffectSizes:
    """Test that metrics provide sufficient effect sizes to be usable."""

    def test_ai_effect_size_deterministic_vs_uniform(self):
        """
        Deterministic state vs uniform should have very large effect size.

        This is a sanity check that our metric can distinguish extremes.
        """
        # Deterministic: AI = 0.5
        deterministic_counts = {"0000": 1000}
        ai_deterministic = compute_asymmetry_index(deterministic_counts)

        # Uniform: AI ≈ 0
        uniform_counts = {f"{i:04b}": 62 + (1 if i < 8 else 0) for i in range(16)}
        ai_uniform = compute_asymmetry_index(uniform_counts)

        # Should be clearly different
        difference = ai_deterministic - ai_uniform
        assert difference > 0.4, (
            f"AI difference between deterministic ({ai_deterministic:.4f}) "
            f"and uniform ({ai_uniform:.4f}) too small: {difference:.4f}"
        )

    def test_tc_effect_size_bell_vs_product(self):
        """
        Bell state vs product state should have clear TC difference.
        """
        # Bell: TC = 1.0 bit
        bell_counts = {"00": 500, "11": 500}
        tc_bell = total_correlation(bell_counts)

        # Product: TC ≈ 0
        product_counts = {"00": 250, "01": 250, "10": 250, "11": 250}
        tc_product = total_correlation(product_counts)

        # Should differ by approximately 1 bit
        difference = tc_bell - tc_product
        assert difference > 0.8, (
            f"TC difference between Bell ({tc_bell:.4f}) "
            f"and product ({tc_product:.4f}) too small: {difference:.4f}"
        )
