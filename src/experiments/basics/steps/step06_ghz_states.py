"""Step 6: GHZ States — Scaling entanglement to many qubits.

WHAT YOU'LL LEARN:
  A Bell state entangles 2 qubits. A GHZ state entangles N qubits.
  GHZ = (|000...0⟩ + |111...1⟩)/√2 — all qubits are 0 or all are 1,
  never a mix. This is "all-or-nothing" entanglement.

  As you add qubits, the number of POSSIBLE outcomes doubles (2^N),
  but GHZ concentrates all probability in just 2 outcomes.

THE EXPERIMENT:
  Run GHZ states at 2, 3, 4, 5, and 6 qubits.
  Watch how the measurement distribution stays concentrated
  even as the outcome space explodes.

WHAT TO LOOK FOR:
  - 2 qubits: 4 possible outcomes, only 00 and 11 appear
  - 3 qubits: 8 possible outcomes, only 000 and 111 appear
  - 6 qubits: 64 possible outcomes, only 000000 and 111111 appear
  - The concentration GROWS — this is the beginning of
    "structured decoherence" (more in steps 12-14)

WHY THIS MATTERS:
  GHZ states are the standard probe for studying multi-party
  entanglement. They're also extremely fragile — losing just
  one qubit destroys the entanglement entirely.

CIRCUIT (4-qubit GHZ):
  q0: ─H──●──●──●── M
  q1: ────X──┼──┼── M
  q2: ───────X──┼── M
  q3: ──────────X── M

  H creates superposition on q0.
  CNOT chain copies the state to all other qubits.
  Result: (|0000⟩ + |1111⟩) / √2

TRY IT:
    from src.experiments.basics.step06_ghz_states import ghz_states

    results = ghz_states.run_scaling()
"""

from __future__ import annotations

from typing import Any

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


class GHZStatesExperiment(BaseExperiment):
    """Step 6: GHZ states from 2 to 6 qubits."""

    name = "06_ghz_states"
    description = "Step 6: GHZ states — scale entanglement from 2 to 6 qubits"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        return ExperimentConfig(
            num_qubits=3,
            state_type="GHZ",
            shots=4096,
            noise_enabled=False,
        )

    def run_scaling(
        self, qubit_range: list[int] | None = None, **overrides: Any
    ) -> list[ExperimentResult]:
        """Run GHZ at increasing qubit counts."""
        qubits = qubit_range or [2, 3, 4, 5, 6]
        return self.sweep(parameter_ranges={"num_qubits": qubits}, **overrides)


ghz_states = GHZStatesExperiment()
