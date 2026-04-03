"""SST Hypothesis Q1: Does entanglement topology influence decoherence pathways?

This experiment tests the first operational hypothesis of the Structured Substrate
Thesis (SST): that entanglement topology creates preferential decoherence pathways.

Test Protocol:
- Prepare GHZ states (global entanglement topology)
- Apply depolarizing noise at various error rates
- Measure structured decoherence metrics (EEC, AI, PCR)

Pass Criterion:
- EEC > 0.3 for entangled states vs EEC ≈ 0 for product states
- AI > 0.1 indicating deviation from uniform distribution
- PCR > 1.5 indicating pathway concentration

This provides evidence for the "River" (structured) vs "Fog" (random) phenomenon.
"""

from __future__ import annotations

from typing import Any

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


class SSTHypothesisQ1(BaseExperiment):
    """SST Hypothesis Q1: Entanglement topology influences decoherence pathways.

    This is the primary SST experiment testing whether GHZ states under
    depolarizing noise exhibit structured decoherence patterns.

    Example:
        exp = SSTHypothesisQ1()

        # Single run with defaults
        result = exp.run()
        print(result.metrics_bundle.value("structure_score"))

        # Run with overrides
        result = exp.run({"num_qubits": 3, "error_rate": 0.1})

        # Parameter sweep over error rates
        results = exp.sweep({"error_rate": [0.01, 0.05, 0.1, 0.2]})
    """

    name = "sst_q1"
    description = "Test whether entanglement topology influences decoherence pathways"

    def default_config(self) -> ExperimentConfig:
        """Default configuration for SST Q1 experiment."""
        return ExperimentConfig(
            num_qubits=4,
            state_type="GHZ",
            noise_enabled=True,
            noise_type="depolarizing",
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
        """Run a noise sweep experiment varying error_rate.

        This is the canonical SST Q1 protocol: sweep error rates from 0 to max
        and observe how structured decoherence metrics evolve.

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
sst_q1 = SSTHypothesisQ1()
