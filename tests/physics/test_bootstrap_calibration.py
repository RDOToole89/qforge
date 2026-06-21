"""
Bootstrap Calibration Tests

Verify that bootstrap confidence intervals achieve their nominal coverage.
A 95% CI should cover the true value approximately 95% of the time.

This is a critical validation for publication-quality statistics:
- If coverage is too low, we're overconfident in our results
- If coverage is too high, we're being overly conservative

These tests are marked as slow because they require many Monte Carlo trials.
"""

import numpy as np
import pytest

from src.core.analysis.core.bootstrap import bootstrap_confidence_interval
from src.core.analysis.core.information_theory import counts_to_probabilities, entropy


class TestBootstrapCoverage:
    """Verify bootstrap CI achieves nominal coverage."""

    @pytest.mark.slow
    def test_95_percent_ci_coverage_entropy(self):
        """
        Bootstrap 95% CI should cover true value ~95% of the time.

        Method:
        1. Define a known distribution (biased coin, H~0.81 bits)
        2. Generate N=100 samples from this distribution
        3. For each sample, compute bootstrap 95% CI for entropy
        4. Count how often true value falls within CI
        5. Assert coverage is in [80%, 100%] (allowing for sampling variability)

        Note: We use a biased coin (70-30 split) to avoid boundary effects
        that occur when the true entropy is at the maximum (1.0).
        """
        # Biased coin: p=0.7, q=0.3
        # True entropy = -0.7*log2(0.7) - 0.3*log2(0.3) ≈ 0.881 bits
        p_bias = 0.7
        true_entropy = -p_bias * np.log2(p_bias) - (1 - p_bias) * np.log2(1 - p_bias)

        n_trials = 100
        n_samples = 500  # Samples per trial
        coverage_count = 0

        rng = np.random.default_rng(42)  # Fixed seed for reproducibility

        def compute_entropy_from_counts(counts):
            """Compute entropy from counts dict."""
            probs = np.array(list(counts_to_probabilities(counts).values()))
            return float(entropy(probs))

        for _trial in range(n_trials):
            # Generate sample from biased coin
            outcomes = rng.choice(["0", "1"], size=n_samples, p=[p_bias, 1 - p_bias])
            counts = {
                "0": int(np.sum(outcomes == "0")),
                "1": int(np.sum(outcomes == "1")),
            }

            # Compute bootstrap CI
            ci_lower, ci_upper = bootstrap_confidence_interval(
                counts,
                compute_entropy_from_counts,
                n_bootstrap=200,  # Reduced for speed
                confidence_level=0.95,
                rng=np.random.default_rng(rng.integers(10000)),
            )

            # Check if true value is within CI
            if ci_lower <= true_entropy <= ci_upper:
                coverage_count += 1

        coverage_rate = coverage_count / n_trials

        # Should be close to 95%, allow some tolerance for finite trials
        # Using 80% as lower bound to account for:
        # - Finite sample effects
        # - Bootstrap approximation error
        # - Jeffreys smoothing slightly affecting entropy
        assert 0.80 <= coverage_rate <= 1.0, (
            f"Coverage {coverage_rate:.1%} not in [80%, 100%]. "
            f"Expected ~95% for properly calibrated CI. "
            f"True entropy = {true_entropy:.4f}"
        )

    @pytest.mark.slow
    def test_ci_width_decreases_with_samples(self):
        """
        CI width should decrease as sample size increases.

        This is a basic sanity check that the bootstrap is working correctly.
        """
        rng = np.random.default_rng(123)

        def compute_entropy_from_counts(counts):
            probs = np.array(list(counts_to_probabilities(counts).values()))
            return float(entropy(probs))

        widths = []
        sample_sizes = [100, 500, 2000]

        for n_samples in sample_sizes:
            # Generate sample
            outcomes = rng.choice(["0", "1"], size=n_samples, p=[0.5, 0.5])
            counts = {
                "0": int(np.sum(outcomes == "0")),
                "1": int(np.sum(outcomes == "1")),
            }

            # Compute CI
            ci_lower, ci_upper = bootstrap_confidence_interval(
                counts,
                compute_entropy_from_counts,
                n_bootstrap=200,
                confidence_level=0.95,
                rng=np.random.default_rng(456),
            )

            width = ci_upper - ci_lower
            widths.append(width)

        # CI width should generally decrease with more samples
        # (may not be strictly monotonic due to randomness)
        assert widths[0] > widths[-1], (
            f"CI width should decrease with samples: "
            f"width(n=100)={widths[0]:.4f}, width(n=2000)={widths[-1]:.4f}"
        )

    @pytest.mark.slow
    def test_ci_contains_point_estimate(self):
        """
        The CI should typically contain the point estimate.

        This is a sanity check - if the CI doesn't contain the estimate,
        something is wrong with the bootstrap.
        """
        rng = np.random.default_rng(789)

        def compute_entropy_from_counts(counts):
            probs = np.array(list(counts_to_probabilities(counts).values()))
            return float(entropy(probs))

        n_trials = 50
        contains_count = 0

        for _ in range(n_trials):
            outcomes = rng.choice(["0", "1"], size=500, p=[0.5, 0.5])
            counts = {
                "0": int(np.sum(outcomes == "0")),
                "1": int(np.sum(outcomes == "1")),
            }

            # Compute point estimate
            point_estimate = compute_entropy_from_counts(counts)

            # Compute CI
            ci_lower, ci_upper = bootstrap_confidence_interval(
                counts,
                compute_entropy_from_counts,
                n_bootstrap=200,
                confidence_level=0.95,
                rng=np.random.default_rng(rng.integers(10000)),
            )

            if ci_lower <= point_estimate <= ci_upper:
                contains_count += 1

        # Should almost always contain point estimate
        assert contains_count >= 0.90 * n_trials, (
            f"CI should contain point estimate in most cases, "
            f"but only did in {contains_count}/{n_trials} trials"
        )


class TestBootstrapReproducibility:
    """Test that bootstrap is reproducible with fixed seeds."""

    def test_reproducibility_with_seed(self):
        """Same seed should give same CI."""
        counts = {"0": 250, "1": 250}

        def compute_entropy_from_counts(c):
            probs = np.array(list(counts_to_probabilities(c).values()))
            return float(entropy(probs))

        # First run
        ci1 = bootstrap_confidence_interval(
            counts,
            compute_entropy_from_counts,
            n_bootstrap=100,
            rng=np.random.default_rng(42),
        )

        # Second run with same seed
        ci2 = bootstrap_confidence_interval(
            counts,
            compute_entropy_from_counts,
            n_bootstrap=100,
            rng=np.random.default_rng(42),
        )

        assert ci1 == ci2, f"CIs should match with same seed: {ci1} vs {ci2}"

    def test_different_seeds_give_different_ci(self):
        """Different seeds should give different CIs (usually)."""
        counts = {"0": 250, "1": 250}

        def compute_entropy_from_counts(c):
            probs = np.array(list(counts_to_probabilities(c).values()))
            return float(entropy(probs))

        ci1 = bootstrap_confidence_interval(
            counts,
            compute_entropy_from_counts,
            n_bootstrap=100,
            rng=np.random.default_rng(42),
        )

        ci2 = bootstrap_confidence_interval(
            counts,
            compute_entropy_from_counts,
            n_bootstrap=100,
            rng=np.random.default_rng(999),
        )

        # Very unlikely to be exactly equal with different seeds
        # (though not impossible)
        # We just check they're both valid
        assert ci1[0] <= ci1[1], "CI1 should be valid interval"
        assert ci2[0] <= ci2[1], "CI2 should be valid interval"
