"""Deep Dive: Structure Scaling — Watch the River grow.

BEST AFTER: Step 11 (noise and entanglement / River vs Fog)

WHAT YOU'LL LEARN:
  In Step 11 you saw that entangled states show structured decoherence
  patterns (River) while unentangled states show uniform patterns (Fog).

  Now the question: does the structure GROW with system size?

  If you add more qubits to a GHZ state, does the "River" get deeper?
  Does the Structure Score increase? What about Total Correlation?

  This is the scaling experiment that produced one of the framework's
  key findings on real hardware: structure grows monotonically with
  qubit count, even as fidelity decreases.

THE EXPERIMENT:
  Run GHZ from 2 to 6 qubits with depolarizing noise and track
  Structure Score (SS) and Total Correlation (TC) at each size.

WHAT TO LOOK FOR:
  - SS increases: 2q (~0.45) → 3q (~0.67) → 4q (~0.75) → 5q (~0.80) → 6q (~0.80)
  - TC increases roughly linearly: ~+0.7 per qubit
  - Fidelity DECREASES (more qubits = more accumulated error)
  - But structure INCREASES — the noise becomes MORE organized, not less

  This is counterintuitive: more noise should mean more randomness.
  Instead, the entanglement network channels the noise into specific
  pathways. Wider river, deeper channel.

CIRCUITS (GHZ at each qubit count):
  2q: q0: ─H──●── M          3q: q0: ─H──●──●── M
      q1: ────X── M              q1: ────X──┼── M
                                  q2: ───────X── M

  4q: q0: ─H──●──●──●── M    6q: q0: ─H──●──●──●──●──●── M
      q1: ────X──┼──┼── M        q1: ────X──┼──┼──┼──┼── M
      q2: ───────X──┼── M        ...
      q3: ──────────X── M        q5: ───────────────────X── M

  Same pattern, more qubits. Structure Score grows at each step.

TRY IT:
    from src.experiments.basics.deep_dives.dd_structure_scaling import structure_scaling

    results = structure_scaling.run_scaling()
"""

from __future__ import annotations

from typing import Any

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


class StructureScalingExperiment(BaseExperiment):
    """Deep Dive: GHZ scaling ladder with structure metrics."""

    name = "dd_structure_scaling"
    description = "Deep dive: Watch Structure Score grow with qubit count"

    def default_config(self) -> ExperimentConfig:
        return ExperimentConfig(
            num_qubits=4,
            state_type="GHZ",
            shots=4096,
            noise_enabled=True,
            noise_type="depolarizing",
            error_rate=0.05,
            rng_seed=42,
            metrics="structured_decoherence",
            visualization_type=["histogram", "metrics_summary"],)

    def run_scaling(self, qubit_range: list[int] | None = None, **overrides: Any) -> list[ExperimentResult]:
        """Run GHZ at 2-6 qubits and track structure metrics."""
        qubits = qubit_range or [2, 3, 4, 5, 6]
        return self.sweep(parameter_ranges={"num_qubits": qubits}, **overrides)


structure_scaling = StructureScalingExperiment()
