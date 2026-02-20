"""
SST Hypothesis Q1 (Structured Noise): Amplitude Damping vs Depolarizing

This experiment tests the same hypothesis as Q1 but with structured noise
(Amplitude Damping) instead of depolarizing noise.

Hypothesis:
Structured noise (Amplitude Damping) will maintain higher PCR values
than Depolarizing noise at equivalent error rates, indicating
preferred decoherence pathways (|1> -> |0>).

This creates a natural comparison: depolarizing (random) vs amplitude damping
(structured) noise to demonstrate the "Fog vs River" phenomenon.
"""

from __future__ import annotations

from typing import Any

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


class SSTHypothesisQ1Structured(BaseExperiment):
    """
    SST Hypothesis Q1 with Amplitude Damping (structured) noise.

    Uses amplitude damping noise which creates structured errors (|1> -> |0>),
    in contrast to depolarizing noise which creates random errors.

    Example:
        exp = SSTHypothesisQ1Structured()

        # Single run with defaults
        result = exp.run()

        # Run with overrides
        result = exp.run({"num_qubits": 3, "error_rate": 0.1})

        # Noise sweep to observe metric evolution
        results = exp.run_noise_sweep(noise_steps=10, max_error_rate=0.3)
    """

    name = "sst_q1_structured"
    description = "SST Q1 with amplitude damping (structured) noise"

    def default_config(self) -> ExperimentConfig:
        """Default configuration for SST Q1 structured noise experiment."""
        return ExperimentConfig(
            num_qubits=4,
            state_type="GHZ",
            noise_enabled=True,
            noise_type="amplitude_damping",  # Structured noise, not depolarizing
            error_rate=0.05,
            shots=4096,
            metrics="structured_decoherence",
        )

    def run_noise_sweep(
        self,
        noise_steps: int = 20,
        max_error_rate: float = 0.5,
        **overrides: Any,
    ) -> list[ExperimentResult]:
        """
        Run a noise sweep experiment varying error_rate.

        Sweeps error rates from 0 to max_error_rate and observes how
        structured decoherence metrics evolve under amplitude damping noise.

        Compare results with SSTHypothesisQ1.run_noise_sweep() (depolarizing)
        to demonstrate the "Fog vs River" phenomenon.

        Args:
            noise_steps: Number of error rate steps
            max_error_rate: Maximum error rate to test
            **overrides: Additional config overrides (e.g., num_qubits=3)

        Returns:
            List of ExperimentResult, one per error rate
        """
        import numpy as np

        error_rates = np.linspace(0.0, max_error_rate, noise_steps).tolist()
        return self.sweep(parameter_ranges={"error_rate": error_rates}, **overrides)


# Module-level instance for convenience
sst_q1_structured = SSTHypothesisQ1Structured()
