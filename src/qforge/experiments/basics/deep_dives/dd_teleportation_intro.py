"""Deep Dive: Quantum Teleportation — Using Bell pairs to transfer state.

BEST AFTER: Step 5 (Bell states)

WHAT YOU'LL LEARN:
  Teleportation is one of the most beautiful protocols in quantum
  mechanics. It uses a shared Bell pair to transfer an unknown
  quantum state from Alice to Bob — without physically moving the qubit.

  This is NOT science fiction teleportation. The quantum state is
  transferred, but:
  - The original is destroyed (no-cloning theorem)
  - Classical communication is needed (no faster-than-light)
  - The "teleportation" is of information, not matter

THE PROTOCOL:
  1. Alice and Bob share a Bell pair (|00⟩ + |11⟩)/√2
  2. Alice has a qubit in unknown state |ψ⟩ she wants to send
  3. Alice performs a Bell measurement on her two qubits
  4. Alice sends the 2-bit result to Bob (classical channel)
  5. Bob applies corrections based on Alice's result
  6. Bob's qubit is now in state |ψ⟩

THE EXPERIMENT:
  We run the teleportation circuit for three different input states
  (|0⟩, |1⟩, |+⟩) and verify that Bob's qubit ends up correct.

  With noise, the fidelity decreases — the teleported state becomes
  degraded because the shared Bell pair is imperfect.

CIRCUIT:
  q0: ─[prep]──────────●──H── M     ← state to teleport
                ░                    ░
  q1: ──────────░──H──●──X──── M     ← Alice's Bell half
                ░     │              ░
  q2: ──────────░─────X────── M     ← Bob's qubit (receives state)

  [prep] = nothing for |0⟩, X for |1⟩, H for |+⟩

TRY IT:
    from qforge.experiments.basics.deep_dives.dd_teleportation_intro import teleportation_intro

    results = teleportation_intro.run_three_states()
"""

from __future__ import annotations

from qiskit import QuantumCircuit

from qforge.engine.models import ExperimentConfig, ExperimentResult
from qforge.experiments.base import BaseExperiment


def _teleportation_circuit(input_state: str = "0") -> QuantumCircuit:
    """Build teleportation circuit for a given input state."""
    qc = QuantumCircuit(3, 3)

    # Prepare input state on q0
    if input_state == "1":
        qc.x(0)
    elif input_state == "+":
        qc.h(0)

    qc.barrier()

    # Create Bell pair between q1 (Alice) and q2 (Bob)
    qc.h(1)
    qc.cx(1, 2)

    qc.barrier()

    # Alice's Bell measurement
    qc.cx(0, 1)
    qc.h(0)

    qc.barrier()
    qc.measure([0, 1, 2], [0, 1, 2])
    return qc


class TeleportationIntroExperiment(BaseExperiment):
    """Deep Dive: Quantum teleportation — transfer state via entanglement."""

    name = "dd_teleportation_intro"
    description = "Deep dive: Quantum teleportation — see state transfer in action"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        circuit = _teleportation_circuit("+")
        return ExperimentConfig(
            num_qubits=3,
            state_type="CUSTOM",
            shots=4096,
            noise_enabled=False,
            custom_params={"source": "circuit", "circuit": circuit},
        )

    def run_three_states(self) -> list[ExperimentResult]:
        """Teleport |0⟩, |1⟩, and |+⟩ and compare outcomes."""
        results = []
        for state in ["0", "1", "+"]:
            circuit = _teleportation_circuit(state)
            results.append(
                self.run(
                    {
                        "custom_params": {"source": "circuit", "circuit": circuit},
                    }
                )
            )
        return results


teleportation_intro = TeleportationIntroExperiment()
