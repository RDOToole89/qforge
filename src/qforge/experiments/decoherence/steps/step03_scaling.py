"""Step 3: Scaling — Does structure grow with system size?

WHAT YOU'LL LEARN:
  Adding qubits to an entangled system doubles the outcome space (2^N),
  but the ideal GHZ distribution always has support on just 2 outcomes.
  How does the Structure Score of the measured distribution change as
  the outcome space grows around those 2 peaks?

  This step measures Structure Score and Total Correlation across a
  ladder of system sizes so you can see the trend yourself.

THE EXPERIMENT:
  Run GHZ from 2 to 6 qubits with depolarizing noise.
  Track Structure Score and Total Correlation at each size.

WHAT TO LOOK FOR:
  - How Structure Score changes with qubit count
  - How Total Correlation changes as qubits are added
  - Fidelity decreases with size (more qubits, more noise exposure) —
    compare that against what the distribution-shape metrics do

CIRCUIT (GHZ at increasing sizes):
  2q: q0: ─H──●── M           4q: q0: ─H──●──●──●── M
      q1: ────X── M               q1: ────X──┼──┼── M
                                   q2: ───────X──┼── M
                                   q3: ──────────X── M

  Same pattern, more qubits. Watch how the metrics change.

TRY IT:
    from qforge.experiments.decoherence.steps.step03_scaling import scaling

    results = scaling.run_ghz_ladder()
"""

from __future__ import annotations

from typing import Any

from qforge.engine.models import ExperimentConfig, ExperimentResult
from qforge.experiments.base import BaseExperiment


class ScalingExperiment(BaseExperiment):
    """Step 3: GHZ scaling ladder with structure metrics."""

    name = "dec_03_scaling"
    description = "Step 3: How distribution metrics change with system size"

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
            metrics="decoherence",
            visualization_type=["histogram", "metrics_summary"],
        )

    def run_ghz_ladder(
        self, qubit_range: list[int] | None = None, **overrides: Any
    ) -> list[ExperimentResult]:
        """Run GHZ at 2-6 qubits."""
        qubits = qubit_range or [2, 3, 4, 5, 6]
        return self.sweep(parameter_ranges={"num_qubits": qubits}, **overrides)


scaling = ScalingExperiment()
