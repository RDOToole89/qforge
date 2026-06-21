"""Step 5: Superdense Coding — Send 2 bits using 1 qubit.

WHAT YOU'LL LEARN:
  Superdense coding is teleportation's mirror image.
  Teleportation: send 1 qubit using 2 classical bits + entanglement.
  Superdense: send 2 classical bits using 1 qubit + entanglement.

  Alice encodes 2 classical bits (00, 01, 10, or 11) by applying
  one of four gates (I, X, Z, XZ) to her half of a Bell pair,
  then sends her qubit to Bob. Bob measures in the Bell basis
  and recovers both bits perfectly.

WHY THIS IS PROFOUND:
  Normally 1 qubit can carry at most 1 classical bit (Holevo bound).
  But with pre-shared entanglement, you can beat this limit.
  Entanglement is a resource that enhances communication.

THE EXPERIMENT:
  Encode each of the four messages (00, 01, 10, 11) and verify
  that Bob correctly decodes all of them.

FRAMEWORK SKILL:
  You're now comfortable with entanglement as a resource, not just
  a phenomenon. This is the mindset shift needed for designing
  your own quantum protocols.

CIRCUIT (encoding message "01"):
  q0: ─H──●──── [encode: X] ────●──H── M
  q1: ────X──── [          ] ───X───── M

  Step 1: Create Bell pair (H + CNOT)
  Step 2: Alice encodes 2-bit message (I/X/Z/XZ on her qubit)
  Step 3: Bob decodes (reverse CNOT + H, then measure)

  00 → I (do nothing)    01 → X (bit flip)
  10 → Z (phase flip)    11 → XZ (both)

TRY IT:
    from src.experiments.advanced.steps.step05_superdense_coding import superdense

    results = superdense.run_all_messages()
"""

from __future__ import annotations

from qiskit import QuantumCircuit

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


def _superdense_circuit(message: str = "00") -> QuantumCircuit:
    """Build superdense coding circuit for a 2-bit message."""
    qc = QuantumCircuit(2, 2)

    # Create Bell pair
    qc.h(0)
    qc.cx(0, 1)
    qc.barrier()

    # Alice encodes message on her qubit (q0)
    if message == "01":
        qc.x(0)
    elif message == "10":
        qc.z(0)
    elif message == "11":
        qc.x(0)
        qc.z(0)
    # "00" → do nothing (identity)

    qc.barrier()

    # Bob decodes: reverse Bell circuit + measure
    qc.cx(0, 1)
    qc.h(0)
    qc.measure([0, 1], [0, 1])

    return qc


class SuperdenseCodingExperiment(BaseExperiment):
    """Step 5: Superdense coding — 2 classical bits from 1 qubit + entanglement."""

    name = "adv_05_superdense_coding"
    description = "Step 5: Superdense coding — send 2 bits using 1 qubit + entanglement"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        circuit = _superdense_circuit("00")
        return ExperimentConfig(
            num_qubits=2,
            state_type="CUSTOM",
            shots=1024,
            noise_enabled=False,
            custom_params={"source": "circuit", "circuit": circuit},
            visualization_type=["histogram", "circuit"],
        )

    def run_all_messages(self) -> list[ExperimentResult]:
        """Encode and decode all four 2-bit messages."""
        results = []
        for msg in ["00", "01", "10", "11"]:
            circuit = _superdense_circuit(msg)
            results.append(
                self.run(
                    {
                        "custom_params": {"source": "circuit", "circuit": circuit},
                    }
                )
            )
        return results


superdense = SuperdenseCodingExperiment()
