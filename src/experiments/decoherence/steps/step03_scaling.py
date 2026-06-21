"""Step 3: Scaling — Does structure grow with system size?

WHAT YOU'LL LEARN:
  Adding qubits to an entangled system doubles the outcome space (2^N).
  Naively, more outcomes should mean MORE randomness. But our hypothesis
  is the opposite: MORE qubits = DEEPER river.

  This step tests whether Structure Score increases monotonically
  with qubit count, and whether GHZ and W scale differently.

THE EXPERIMENT:
  Run GHZ from 2 to 6 qubits with depolarizing noise.
  Track Structure Score and Total Correlation at each size.

WHAT TO LOOK FOR:
  - SS increases: 2q (~0.45) → 3q (~0.67) → 4q (~0.75) → 5q (~0.80) → 6q (~0.80)
  - TC increases linearly: ~+0.7 per qubit added
  - Fidelity DECREASES (more qubits = more noise)
  - But structure INCREASES — counterintuitive!

  Two scaling modes (compare with W in the deep dive):
  - GHZ: AMPLIFICATION — entropy stays flat, probability compresses into fewer peaks
  - W: REDISTRIBUTION — entropy grows with N, each qubit adds a new pathway

CIRCUIT (GHZ at increasing sizes):
  2q: q0: ─H──●── M           4q: q0: ─H──●──●──●── M
      q1: ────X── M               q1: ────X──┼──┼── M
                                   q2: ───────X──┼── M
                                   q3: ──────────X── M

  Same pattern, more qubits. Watch the metrics climb.

TRY IT:
    from src.experiments.decoherence.steps.step03_scaling import scaling

    results = scaling.run_ghz_ladder()
"""

from __future__ import annotations

from typing import Any

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


class ScalingExperiment(BaseExperiment):
    """Step 3: GHZ scaling ladder with structure metrics."""

    name = "dec_03_scaling"
    description = "Step 3: Does structure grow with qubits? Run the scaling ladder"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        return ExperimentConfig(
            num_qubits=4,
            state_type="GHZ",
            shots=4096,
            noise_enabled=True,
            noise_type="depolarizing",
            error_rate=0.05,
            rng_seed=42,
            metrics="structured_decoherence",
            visualization_type=["histogram", "metrics_summary"],
        )

    def run_ghz_ladder(
        self, qubit_range: list[int] | None = None, **overrides: Any
    ) -> list[ExperimentResult]:
        """Run GHZ at 2-6 qubits."""
        qubits = qubit_range or [2, 3, 4, 5, 6]
        return self.sweep(parameter_ranges={"num_qubits": qubits}, **overrides)


scaling = ScalingExperiment()
