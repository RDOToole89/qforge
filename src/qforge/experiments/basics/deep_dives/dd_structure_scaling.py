"""Deep Dive: Structure Scaling — distribution metrics vs system size.

BEST AFTER: Step 11 (noise and entanglement)

WHAT YOU'LL LEARN:
  In Step 11 you saw that states with concentrated ideal distributions
  (GHZ) keep concentrated measured distributions under noise, while
  product states stay near-uniform.

  Now the question: how do the metrics change with system size?

  If you add more qubits to a GHZ state, what happens to the Structure
  Score? What about Total Correlation?

THE EXPERIMENT:
  Run GHZ from 2 to 6 qubits with depolarizing noise and track
  Structure Score (SS) and Total Correlation (TC) at each size.

WHAT TO LOOK FOR:
  - How SS changes as the outcome space (2^N) grows around the
    two ideal GHZ peaks
  - How TC changes as qubits are added
  - Fidelity decreases with size (more gates, more noise exposure) —
    compare that trend against the distribution-shape metrics

CIRCUITS (GHZ at each qubit count):
  2q: q0: ─H──●── M          3q: q0: ─H──●──●── M
      q1: ────X── M              q1: ────X──┼── M
                                  q2: ───────X── M

  4q: q0: ─H──●──●──●── M    6q: q0: ─H──●──●──●──●──●── M
      q1: ────X──┼──┼── M        q1: ────X──┼──┼──┼──┼── M
      q2: ───────X──┼── M        ...
      q3: ──────────X── M        q5: ───────────────────X── M

  Same pattern, more qubits. Watch how the metrics change.

TRY IT:
    from qforge.experiments.basics.deep_dives.dd_structure_scaling import structure_scaling

    results = structure_scaling.run_scaling()
"""

from __future__ import annotations

from typing import Any

from qforge.engine.models import ExperimentConfig, ExperimentResult
from qforge.experiments.base import BaseExperiment


class StructureScalingExperiment(BaseExperiment):
    """Deep Dive: GHZ scaling ladder with structure metrics."""

    name = "dd_structure_scaling"
    description = "Deep dive: Watch Structure Score grow with qubit count"
    metrics_hint = (
        "Sweep num_qubits — Structure Score typically grows as GHZ "
        "correlations involve more bits."
    )
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
            metrics=["structure_score", "concentration_index"],
            visualization_type=["histogram", "metrics_summary"],
        )

    def run_scaling(
        self, qubit_range: list[int] | None = None, **overrides: Any
    ) -> list[ExperimentResult]:
        """Run GHZ at 2-6 qubits and track structure metrics."""
        qubits = qubit_range or [2, 3, 4, 5, 6]
        return self.sweep(parameter_ranges={"num_qubits": qubits}, **overrides)


structure_scaling = StructureScalingExperiment()
