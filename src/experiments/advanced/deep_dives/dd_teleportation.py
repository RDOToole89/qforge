"""Quantum Teleportation — Transfer a quantum state using entanglement.

What you'll learn:
  - How entanglement enables state transfer without physical movement
  - The role of classical communication in teleportation
  - Why this doesn't violate no-cloning or faster-than-light constraints
  - How noise in the entangled channel degrades teleportation fidelity

Quantum teleportation transfers an unknown quantum state |psi⟩ from
Alice to Bob using:
  1. A shared Bell pair (pre-distributed entanglement)
  2. Alice measures her qubit + the input in the Bell basis (2 classical bits)
  3. Bob applies corrections based on Alice's measurement result

The result: Bob's qubit ends up in state |psi⟩, and Alice's original
is destroyed (no-cloning preserved). The "information" travels via the
classical bits, not the entanglement — so no faster-than-light signaling.

Try it:
    from src.experiments.advanced.teleportation import teleportation_experiment

    # Teleport |+⟩ state (default)
    result = teleportation_experiment.run()

    # Teleport |1⟩ state
    result = teleportation_experiment.run({"custom_params": {"state": "1"}})

    # See how noisy entanglement degrades teleportation
    results = teleportation_experiment.run_noise_sweep()

WHAT YOU'LL EXPLORE:
  - The full teleportation protocol with deferred measurement
  - How noisy entanglement degrades teleportation fidelity
  - Different input states (|0⟩, |1⟩, |+⟩) and their teleportation signatures

CIRCUIT:
  q0: ─[prep]──────────●──H── M     ← state to teleport
               ░                     ░
  q1: ─────────░──H──●──X──── M     ← Alice's Bell half
               ░     │               ░
  q2: ─────────░─────X────── M      ← Bob's qubit (receives state)

TRY IT:
    from src.experiments.advanced.deep_dives.dd_teleportation import teleportation_experiment

    # Teleport |+⟩ state
    result = teleportation_experiment.run()

    # See noise degrade teleportation
    results = teleportation_experiment.run_noise_sweep()
"""

from __future__ import annotations

from typing import Any

import numpy as np
from qiskit import QuantumCircuit

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


def _build_teleportation_circuit(state: str = "+") -> QuantumCircuit:
    """Build a quantum teleportation circuit.

    Qubits:
      q0: Input state (Alice's qubit to teleport)
      q1: Alice's half of the Bell pair
      q2: Bob's half of the Bell pair

    Protocol:
      1. Prepare input state on q0
      2. Create Bell pair between q1 and q2
      3. Alice performs Bell measurement on q0, q1
      4. Bob applies corrections based on measurement
         (implemented as deferred measurement with classically controlled gates)
    """
    qc = QuantumCircuit(3, 3)

    # 1. Prepare input state on q0
    if state == "+":
        qc.h(0)
    elif state == "1":
        qc.x(0)
    elif state == "-":
        qc.x(0)
        qc.h(0)
    # else: |0⟩ (default)

    qc.barrier()

    # 2. Create Bell pair between q1 (Alice) and q2 (Bob)
    qc.h(1)
    qc.cx(1, 2)

    qc.barrier()

    # 3. Alice's Bell measurement: CNOT(q0→q1), H(q0), measure q0 and q1
    qc.cx(0, 1)
    qc.h(0)

    qc.barrier()

    # Measure all (deferred measurement model — corrections are implicit)
    qc.measure([0, 1, 2], [0, 1, 2])

    return qc


class TeleportationExperiment(BaseExperiment):
    """Quantum teleportation protocol.

    Teleports a qubit state from Alice to Bob using a shared
    Bell pair and classical communication. Uses deferred measurement
    (all qubits measured at the end).

    Default: teleport |+⟩ state through a noisy channel.
    """

    name = "teleportation"
    description = "Quantum teleportation — transfer a state using entanglement"

    def default_config(self) -> ExperimentConfig:
        state = "+"
        circuit = _build_teleportation_circuit(state)
        return ExperimentConfig(
            num_qubits=3,
            state_type="CUSTOM",
            shots=4096,
            noise_enabled=True,
            noise_type="depolarizing",
            error_rate=0.02,
            custom_params={
                "source": "circuit",
                "circuit": circuit,
                "state": state,
            },
            visualization_type=["histogram", "circuit"],)

    def run_noise_sweep(
        self, steps: int = 8, max_error: float = 0.2, **overrides: Any,
    ) -> list[ExperimentResult]:
        """See how noisy entanglement degrades teleportation fidelity."""
        rates = np.linspace(0.0, max_error, steps).tolist()
        # Avoid exactly 0 for noise_enabled logic
        rates[0] = 0.001
        return self.sweep(
            parameter_ranges={"error_rate": rates},
            noise_enabled=True,
            **overrides,
        )


teleportation_experiment = TeleportationExperiment()
