"""Step 4: Noise Resilience — Does structure degrade smoothly or collapse?

WHAT YOU'LL LEARN:
  Steps 1-3 showed that structure exists and grows. But how ROBUST is it?
  If you increase the noise level from 0% to 20%, does the River erode
  gradually or suddenly flood into Fog?

  This matters for practical applications: if structure survives moderate
  noise, error correction could exploit it. If it collapses at a threshold,
  there's a critical noise level to stay below.

THE EXPERIMENT:
  Sweep depolarizing noise from 0% to 20% on GHZ-6.
  Track Structure Score at each noise level.

WHAT TO LOOK FOR:
  - SS at 0% noise: ~0.97 (nearly perfect structure)
  - SS at 5% noise: ~0.80 (most structure survives)
  - SS at 10% noise: ~0.71 (still significant)
  - SS at 20% noise: ~0.58 (reduced but still present)
  - The decay is SMOOTH — no sharp phase transition
  - GHZ structure is surprisingly robust to noise

  Compare with W (in deep dive): W degrades FASTER despite surviving
  deeper circuits. Circuit-depth resilience and noise-magnitude
  resilience are independent properties.

CIRCUIT:
  q0: ─H──●──●──●──●──●── [noise at p%] ── M
  q1: ────X──┼──┼──┼──┼── [noise at p%] ── M
  ...
  q5: ───────────────────X── [noise at p%] ── M

  Same circuit at every noise level. Only the error rate changes.

TRY IT:
    from src.experiments.decoherence.steps.step04_noise_resilience import noise_resilience

    results = noise_resilience.run_sweep()
"""

from __future__ import annotations

from typing import Any

import numpy as np

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


class NoiseResilienceExperiment(BaseExperiment):
    """Step 4: Sweep noise and observe structure degradation."""

    name = "dec_04_noise_resilience"
    description = "Step 4: How robust is structure? Sweep noise from 0% to 20%"

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
            metrics="structured_decoherence",
            visualization_type=["histogram", "metrics_summary"],
        )

    def run_sweep(
        self, steps: int = 8, max_error: float = 0.20, **overrides: Any
    ) -> list[ExperimentResult]:
        """Sweep noise rate and track structure."""
        rates = np.linspace(0.005, max_error, steps).tolist()
        return self.sweep(parameter_ranges={"error_rate": rates}, **overrides)


noise_resilience = NoiseResilienceExperiment()
