"""Step 4: Quantum Teleportation — Entanglement as a resource.

WHAT YOU'LL LEARN:
  Steps 1-3 showed quantum giving you computational superpowers.
  Now we shift: entanglement is not just a phenomenon to observe —
  it's a RESOURCE you can USE.

  Teleportation uses a shared Bell pair to transfer an unknown
  quantum state from Alice to Bob. No physical qubit moves.
  The original state is destroyed (no-cloning theorem).

THE PROTOCOL:
  1. Alice and Bob share a Bell pair (pre-distributed)
  2. Alice has input state |ψ⟩ she wants to send
  3. Alice does Bell measurement on her two qubits → gets 2 classical bits
  4. Alice sends the 2 bits to Bob (classical channel, speed of light)
  5. Bob applies corrections based on Alice's bits
  6. Bob's qubit is now |ψ⟩

WHY THIS MATTERS FOR EXPERIMENTS:
  Teleportation is the foundation of quantum networks, error
  correction (syndrome extraction uses teleportation-like circuits),
  and measurement-based quantum computing. Understanding it unlocks
  all of these.

FRAMEWORK SKILL:
  You'll learn to build multi-step quantum protocols as circuits
  and interpret results where different measurement outcomes
  correspond to different branches of the protocol.

CIRCUIT:
  q0: ─H─────────────●──H── M ──     ← input state |+⟩
           ░                          ░
  q1: ─────░──H──●────X───── M ──     ← Alice's Bell half
           ░     │                    ░
  q2: ─────░─────X─────────── M ──     ← Bob's half (receives state)

  Step 1: Prepare |+⟩ on q0
  Step 2: Create Bell pair on q1-q2
  Step 3: Bell measurement on q0-q1
  Step 4: Bob's qubit (q2) now holds the teleported state

TRY IT:
    from src.experiments.advanced.steps.step04_teleportation import teleportation

    results = teleportation.run_three_states()
"""

from __future__ import annotations

from qiskit import QuantumCircuit

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


def _teleport_circuit(state: str = "+") -> QuantumCircuit:
    """Build teleportation circuit for input state."""
    qc = QuantumCircuit(3, 3)

    if state == "1":
        qc.x(0)
    elif state == "+":
        qc.h(0)
    elif state == "-":
        qc.x(0)
        qc.h(0)

    qc.barrier()
    qc.h(1)
    qc.cx(1, 2)
    qc.barrier()
    qc.cx(0, 1)
    qc.h(0)
    qc.barrier()
    qc.measure([0, 1, 2], [0, 1, 2])
    return qc


class TeleportationExperiment(BaseExperiment):
    """Step 4: Quantum teleportation — use entanglement to transfer state."""

    name = "adv_04_teleportation"
    description = "Step 4: Quantum teleportation — entanglement as a communication resource"

    def default_config(self) -> ExperimentConfig:
        circuit = _teleport_circuit("+")
        return ExperimentConfig(
            num_qubits=3,
            state_type="CUSTOM",
            shots=4096,
            noise_enabled=False,
            custom_params={"source": "circuit", "circuit": circuit},
            visualization_type=["histogram", "circuit"],)

    def run_three_states(self) -> list[ExperimentResult]:
        """Teleport |0⟩, |1⟩, and |+⟩."""
        results = []
        for state in ["0", "1", "+"]:
            circuit = _teleport_circuit(state)
            results.append(self.run({
                "custom_params": {"source": "circuit", "circuit": circuit},
            }))
        return results


teleportation = TeleportationExperiment()
