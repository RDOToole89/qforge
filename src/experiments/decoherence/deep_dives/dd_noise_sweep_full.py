"""Noise Sweep — How does structure respond to increasing noise?

Sweeps the error rate from 0% to 20% and tracks how Structure Score,
entropy, and KL divergence evolve. Tests whether the decoherence
structure degrades smoothly or collapses at a threshold.

Key finding (simulation):
  GHZ: Structure degrades slowly (SS 0.97 → 0.58 at 20% noise).
       The two-peak distribution is robust — simple structure is hard to destroy.

  W: Structure degrades faster (SS 0.90 → 0.22 at 20% noise).
     The six-peak distribution has more ways to break.

  Paradox: W survives deeper circuits on real hardware (depth 52 vs 24)
  but is more sensitive to noise magnitude. Circuit-depth resilience and
  noise-magnitude resilience are independent properties.

Usage:
    from src.experiments.decoherence import noise_sweep

    # Sweep GHZ under depolarizing noise
    results = noise_sweep.run_sweep()

    # Sweep W under amplitude damping
    results = noise_sweep.run_sweep(state_type="W", noise_type="amplitude_damping")

    # Compare noise models on the same state
    depol = noise_sweep.run_sweep(noise_type="depolarizing")
    amp = noise_sweep.run_sweep(noise_type="amplitude_damping")
"""

from __future__ import annotations

from typing import Any

import numpy as np

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


class NoiseSweep(BaseExperiment):
    """Sweep noise rate and observe structure degradation.

    Tests how decoherence structure responds to increasing noise,
    revealing the resilience properties of different entanglement topologies.
    """

    name = "noise_sweep"
    description = "Sweep noise rate to test decoherence structure resilience"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        return ExperimentConfig(
            num_qubits=6,
            state_type="GHZ",
            noise_enabled=True,
            noise_type="depolarizing",
            error_rate=0.05,
            shots=8192,
            rng_seed=42,
            metrics="structured_decoherence",
            visualization_type="all",
        )

    def run_sweep(
        self,
        steps: int = 10,
        max_error: float = 0.20,
        **overrides: Any,
    ) -> list[ExperimentResult]:
        """Sweep error rate from 0 to max_error."""
        rates = np.linspace(0.001, max_error, steps).tolist()
        return self.sweep(parameter_ranges={"error_rate": rates}, **overrides)


noise_sweep = NoiseSweep()
