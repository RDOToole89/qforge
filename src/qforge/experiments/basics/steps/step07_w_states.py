"""Step 7: W States — A different kind of entanglement.

WHAT YOU'LL LEARN:
  GHZ is "all-or-nothing" entanglement. W is "shared excitation"
  entanglement — fundamentally different.

  W state = (|100...0⟩ + |010...0⟩ + ... + |000...1⟩) / √N
  Exactly one qubit is |1⟩, but you don't know WHICH one until
  you measure. The excitation is shared equally.

HOW W DIFFERS FROM GHZ:
  - GHZ: lose one qubit → all entanglement destroyed
  - W: lose one qubit → remaining qubits STAY entangled
  - GHZ: 2 peaks in measurement, high inter-qubit correlation
  - W: N peaks in measurement, lower correlation per pair

THE EXPERIMENT:
  Run W states at 3, 4, 5, 6 qubits. Compare the measurement
  distribution with GHZ at the same sizes.

WHAT TO LOOK FOR:
  - W-3: three peaks (100, 010, 001) at ~33% each
  - W-6: six peaks (100000 through 000001) at ~17% each
  - Plus a small |000...0⟩ peak (excitation lost to noise floor)
  - Compare with GHZ: 2 peaks vs N peaks

WHY THIS MATTERS:
  W states are more robust than GHZ — they survive qubit loss.
  This makes them candidates for quantum communication protocols
  where some qubits might be lost in transit.

CIRCUIT (simplified view — actual uses Givens rotations):
  The W state preparation distributes one excitation equally:
  |W₃⟩ = (|100⟩ + |010⟩ + |001⟩) / √3

  Uses a cascade of controlled rotations to split the excitation
  probability equally across all qubits. More complex than GHZ
  but produces a fundamentally different entanglement structure.

TRY IT:
    from qforge.experiments.basics.step07_w_states import w_states

    results = w_states.run_scaling()
"""

from __future__ import annotations

from typing import Any

from qforge.engine.models import ExperimentConfig, ExperimentResult
from qforge.experiments.base import BaseExperiment


class WStatesExperiment(BaseExperiment):
    """Step 7: W states — distributed excitation entanglement."""

    name = "07_w_states"
    description = "Step 7: W states — shared excitation, a different entanglement topology"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        return ExperimentConfig(
            num_qubits=3,
            state_type="W",
            shots=4096,
            noise_enabled=False,
        )

    def run_scaling(
        self, qubit_range: list[int] | None = None, **overrides: Any
    ) -> list[ExperimentResult]:
        """Run W states at increasing qubit counts."""
        qubits = qubit_range or [3, 4, 5, 6]
        return self.sweep(parameter_ranges={"num_qubits": qubits}, **overrides)


w_states = WStatesExperiment()
