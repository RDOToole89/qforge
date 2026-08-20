"""Step 4: Noise Resilience — Does structure degrade smoothly or collapse?

WHAT YOU'LL LEARN:
  Steps 1-3 looked at concentrated distributions at a fixed noise level.
  This step asks how the concentration changes as noise increases:
  does the Structure Score decay gradually with the error rate, or
  drop off sharply at some level?

THE EXPERIMENT:
  Sweep depolarizing noise from 0% to 20% on GHZ-6.
  Track Structure Score at each noise level.

WHAT TO LOOK FOR:
  - Structure Score is highest at 0% noise, where the distribution is
    (up to shot noise) the ideal two-peak GHZ distribution.
  - As the error rate rises, probability leaks into neighboring
    outcomes and the Structure Score falls.
  - Plot the curve and judge its shape for yourself — is the decay
    smooth or does it have a knee?

CIRCUIT:
  q0: ─H──●──●──●──●──●── [noise at p%] ── M
  q1: ────X──┼──┼──┼──┼── [noise at p%] ── M
  ...
  q5: ───────────────────X── [noise at p%] ── M

  Same circuit at every noise level. Only the error rate changes.

TRY IT:
    from qforge.experiments.decoherence.steps.step04_noise_resilience import noise_resilience

    results = noise_resilience.run_sweep()
"""

from __future__ import annotations

from typing import Any

import numpy as np

from qforge.engine.models import ExperimentConfig, ExperimentResult
from qforge.experiments.base import BaseExperiment


class NoiseResilienceExperiment(BaseExperiment):
    """Step 4: Sweep noise and observe structure degradation."""

    name = "dec_04_noise_resilience"
    description = "Step 4: Sweep noise from 0% to 20% and track distribution structure"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        return ExperimentConfig(
            num_qubits=6,
            state_type="GHZ",
            shots=8192,
            noise_enabled=True,
            noise_type="depolarizing",
            error_rate=0.05,
            rng_seed=42,
            metrics="decoherence",
            visualization_type=["histogram", "metrics_summary"],
        )

    def run_sweep(
        self, steps: int = 8, max_error: float = 0.20, **overrides: Any
    ) -> list[ExperimentResult]:
        """Sweep noise rate and track structure."""
        rates = np.linspace(0.005, max_error, steps).tolist()
        return self.sweep(parameter_ranges={"error_rate": rates}, **overrides)


noise_resilience = NoiseResilienceExperiment()
