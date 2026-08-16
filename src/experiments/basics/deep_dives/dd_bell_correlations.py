"""Deep Dive: Bell Correlations — Quantum vs classical bounds.

This experiment tests quantum correlations in Bell states - the foundational
demonstration that quantum mechanics violates classical correlation bounds.

Question:
    Do Bell states maintain quantum correlations under noise, and how do
    they compare to classical correlation bounds?

Background:
    Bell states exhibit perfect correlations that cannot be explained classically.
    For |Φ+⟩ = (|00⟩ + |11⟩)/√2:
    - Quantum prediction: P(same) = 1.0, P(different) = 0.0
    - Classical bound: P(same) ≤ 0.75 (for hidden variable theories)

    Under noise, quantum correlations decay. This experiment measures:
    - Correlation coefficient: (P_same - P_diff)
    - Bell state fidelity: overlap with ideal state
    - Classical violation: how much quantum exceeds classical bounds

CIRCUIT (Bell Φ+):
  q0: ─H──●── M
  q1: ────X── M

  Measures quantum correlation strength across all 4 Bell variants.
  Quantum correlations exceed classical bounds (Bell inequality violation).

WHAT YOU'LL EXPLORE:
  - Correlation coefficient across all 4 Bell state variants
  - Whether quantum correlations exceed the classical bound of 0.5
  - How noise erodes the quantum advantage in correlation strength

TRY IT:
    from src.experiments.basics.deep_dives.dd_bell_correlations import bell_correlation

    result, metrics = bell_correlation.run_with_bell_metrics()
    print(f"Correlation: {metrics.correlation_coefficient:.3f}")
    print(f"Exceeds classical: {metrics.exceeds_classical}")
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


@dataclass
class BellCorrelationMetrics:
    """Metrics specific to Bell correlation experiments."""

    correlation_coefficient: float  # (P_00 + P_11) - (P_01 + P_10), range [-1, 1]
    fidelity: float  # Overlap with ideal Bell state, range [0, 1]
    p_same: float  # P(00) + P(11) for Φ states, P(01) + P(10) for Ψ states
    p_different: float  # Complementary probability
    exceeds_classical: bool  # True if correlation > 0.5 (classical bound)
    variant: str  # Which Bell state variant


def compute_bell_metrics(
    counts: dict[str, int], variant: str = "phi_plus"
) -> BellCorrelationMetrics:
    """Compute Bell state correlation metrics from measurement counts.

    Args:
        counts: Measurement outcomes {"00": n00, "01": n01, "10": n10, "11": n11}
        variant: Bell state variant ("phi_plus", "phi_minus", "psi_plus", "psi_minus")

    Returns:
        BellCorrelationMetrics with correlation analysis
    """
    total = sum(counts.values())
    if total == 0:
        raise ValueError("No measurement counts provided")

    # Extract probabilities (handle missing keys)
    p00 = counts.get("00", 0) / total
    p01 = counts.get("01", 0) / total
    p10 = counts.get("10", 0) / total
    p11 = counts.get("11", 0) / total

    # For Φ states (phi_plus, phi_minus): same = 00, 11
    # For Ψ states (psi_plus, psi_minus): same = 01, 10
    if variant in ["phi_plus", "phi_minus"]:
        p_same = p00 + p11
        p_different = p01 + p10
        # Fidelity for Φ+ is 2*(P00 + P11) - but we need to account for phase
        # For computational basis measurement, Φ+ and Φ- look identical
        fidelity = p_same  # Simplified fidelity estimate
    else:  # psi_plus, psi_minus
        p_same = p01 + p10
        p_different = p00 + p11
        fidelity = p_same

    # Correlation coefficient: ranges from -1 (anti-correlated) to +1 (correlated)
    # For Φ states: +1 means perfect 00/11 correlation
    # For Ψ states: +1 means perfect 01/10 correlation
    if variant in ["phi_plus", "phi_minus"]:
        correlation = (p00 + p11) - (p01 + p10)
    else:
        correlation = (p01 + p10) - (p00 + p11)

    # Classical hidden variable theories are bounded by correlation ≤ 0.5
    # (this is a simplified version of the CHSH bound)
    exceeds_classical = p_same > 0.75  # Classical bound for same-outcome probability

    return BellCorrelationMetrics(
        correlation_coefficient=correlation,
        fidelity=fidelity,
        p_same=p_same,
        p_different=p_different,
        exceeds_classical=exceeds_classical,
        variant=variant,
    )


class BellCorrelation(BaseExperiment):
    """Deep Dive: Bell Correlations — Quantum vs classical bounds.

    Tests quantum correlations in Bell states and compares to classical bounds.
    This demonstrates that the framework supports non-SST experiments.

    Example:
        exp = BellCorrelation()

        # Run with default Φ+ state
        result = exp.run()

        # Test different Bell state variants
        result = exp.run({"custom_params": {"variant": "psi_minus"}})

        # Sweep over noise levels
        results = exp.run_noise_sweep(noise_steps=10, max_error_rate=0.3)

        # Compare all four Bell states
        results = exp.compare_variants(error_rate=0.1)
    """

    name = "bell_correlation"
    description = "Bell state correlation test - quantum vs classical bounds"

    def default_config(self) -> ExperimentConfig:
        """Default configuration for Bell correlation experiment."""
        return ExperimentConfig(
            num_qubits=2,  # Bell states are strictly 2-qubit
            state_type="BELL",
            custom_params={"variant": "phi_plus"},
            noise_enabled=True,
            noise_type="depolarizing",
            error_rate=0.05,
            shots=4096,
            # metrics=None is the default — this experiment computes its own
        )

    def run(self, overrides: Mapping[str, Any] | None = None) -> ExperimentResult:
        """Run Bell correlation experiment and compute Bell-specific metrics.

        Returns standard ExperimentResult. Access Bell metrics via:
            result.analysis.counts → compute_bell_metrics(counts, variant)
        """
        return super().run(overrides)

    def run_with_bell_metrics(
        self, overrides: dict[str, Any] | None = None
    ) -> tuple[ExperimentResult, BellCorrelationMetrics]:
        """Run experiment and return both ExperimentResult and Bell metrics.

        Args:
            overrides: Config overrides

        Returns:
            Tuple of (ExperimentResult, BellCorrelationMetrics)
        """
        result = self.run(overrides)

        # Extract counts from result
        counts = {}
        if result.analysis and result.analysis.measurement_results:
            counts = result.analysis.measurement_results.raw_counts

        # Get variant from config
        config = self.default_config()
        if overrides:
            config_dict = config.model_dump()
            config_dict.update(overrides)
            custom_params = config_dict.get("custom_params", {})
        else:
            custom_params = config.custom_params or {}

        variant = custom_params.get("variant", "phi_plus")

        # Compute Bell metrics
        bell_metrics = compute_bell_metrics(counts, variant)

        return result, bell_metrics

    def run_noise_sweep(
        self,
        noise_steps: int = 10,
        max_error_rate: float = 0.5,
        **overrides: Any,
    ) -> list[tuple[float, ExperimentResult, BellCorrelationMetrics]]:
        """Sweep over noise levels and track correlation decay.

        Args:
            noise_steps: Number of error rate steps
            max_error_rate: Maximum error rate to test
            **overrides: Additional config overrides

        Returns:
            List of (error_rate, ExperimentResult, BellCorrelationMetrics) tuples
        """
        import numpy as np

        error_rates = np.linspace(0.0, max_error_rate, noise_steps).tolist()
        results = []

        for error_rate in error_rates:
            combined_overrides = {**overrides, "error_rate": error_rate}
            result, bell_metrics = self.run_with_bell_metrics(combined_overrides)
            results.append((error_rate, result, bell_metrics))

        return results

    def compare_variants(
        self, error_rate: float = 0.05, **overrides: Any
    ) -> dict[str, tuple[ExperimentResult, BellCorrelationMetrics]]:
        """Compare all four Bell state variants at a given noise level.

        Args:
            error_rate: Noise level to test
            **overrides: Additional config overrides

        Returns:
            Dict mapping variant name to (ExperimentResult, BellCorrelationMetrics)
        """
        variants = ["phi_plus", "phi_minus", "psi_plus", "psi_minus"]
        results = {}

        for variant in variants:
            combined_overrides = {
                **overrides,
                "error_rate": error_rate,
                "custom_params": {"variant": variant},
            }
            result, bell_metrics = self.run_with_bell_metrics(combined_overrides)
            results[variant] = (result, bell_metrics)

        return results


# Module-level instance for convenience
bell_correlation = BellCorrelation()
