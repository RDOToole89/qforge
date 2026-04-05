"""Step 9: Noise — What happens when qubits interact with the environment.

WHAT YOU'LL LEARN:
  Real quantum computers are noisy. Qubits interact with their
  environment (thermal vibrations, stray fields, imperfect controls)
  and gradually lose their quantum properties. This is decoherence.

  Noise turns pure states into mixed states. A qubit that was
  perfectly on the Bloch sphere surface drifts toward the center
  (the maximally mixed state — complete randomness).

THE EXPERIMENT:
  Take a single qubit in the |+⟩ state and apply increasing
  depolarizing noise. Watch how the measurement statistics change
  from 50/50 (pure superposition) toward random.

  Depolarizing noise: with probability p, the qubit gets replaced
  by a completely random state. With probability (1-p), it's fine.

WHAT TO LOOK FOR:
  - At 0% noise: perfect 50/50 split (|+⟩ state)
  - At 5% noise: still ~50/50 but slightly messier
  - At 20% noise: starting to deviate
  - At 50% noise: significant deviation from ideal
  - At 100% noise: completely random (50/50 but from randomness, not superposition)

  The STATISTICS look the same at 0% and 100% (both 50/50)! But the
  physical state is completely different. At 0%, the qubit is in a
  definite superposition. At 100%, it's a classical random coin flip.

CIRCUIT:
  q: ─H─ [NOISE] ─ M ───

  The H gate creates |+⟩ (superposition).
  The noise is applied by the engine after circuit creation.
  Depolarizing noise randomly applies X, Y, or Z with probability p.

TRY IT:
    from src.experiments.basics.step09_noise_intro import noise_intro

    results = noise_intro.run_noise_sweep()
"""

from __future__ import annotations

from typing import Any

import numpy as np

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


class NoiseIntroExperiment(BaseExperiment):
    """Step 9: Introduction to quantum noise on a single qubit."""

    name = "09_noise_intro"
    description = "Step 9: Watch noise gradually destroy a quantum state"

    def default_config(self) -> ExperimentConfig:
        return ExperimentConfig(
            num_qubits=1,
            state_type="SUPERPOSITION",
            shots=4096,
            noise_enabled=True,
            noise_type="depolarizing",
            error_rate=0.05,
        )

    def run_noise_sweep(self, steps: int = 8, **overrides: Any) -> list[ExperimentResult]:
        """Sweep noise from 0% to 30% and watch the state degrade."""
        rates = np.linspace(0.001, 0.3, steps).tolist()
        return self.sweep(parameter_ranges={"error_rate": rates}, **overrides)


noise_intro = NoiseIntroExperiment()
