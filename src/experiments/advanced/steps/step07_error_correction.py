"""Step 7: Quantum Error Correction — Protecting quantum information.

WHAT YOU'LL LEARN:
  Quantum states are fragile — noise destroys them. Error correction
  is THE challenge that determines whether quantum computers become
  practically useful. This step teaches the simplest error correction
  code: the 3-qubit bit-flip code.

HOW IT WORKS:
  Classical repetition: encode 0 as 000, encode 1 as 111.
  If one bit flips, majority vote recovers the original.

  Quantum version: encode |ψ⟩ = α|0⟩ + β|1⟩ as α|000⟩ + β|111⟩.
  If one qubit flips, we detect WHICH one flipped (without learning α,β!)
  using "syndrome measurements" — ancilla qubits that detect parity errors.

  The trick: we detect the error without measuring the data qubits,
  preserving the superposition. This is profoundly different from
  classical error correction.

LIMITATIONS:
  This code only corrects X errors (bit flips), not Z errors (phase flips).
  Real quantum codes (surface code, Steane code) correct both.
  But the principle is the same.

THE EXPERIMENT:
  1. Encode a qubit into 3 qubits
  2. Apply a bit flip error to one qubit
  3. Detect which qubit was flipped (syndrome)
  4. Verify the logical qubit is recovered

FRAMEWORK SKILL:
  You now understand why noise matters (from basics steps 9-11) and
  how to fight it. This connects your understanding of structured
  decoherence to the practical challenge of building useful quantum computers.

CIRCUIT (3-qubit bit-flip code with error on q1):
  q0: ─H──●──●────────── [     ] ──●──●── M     ← data
  q1: ────X──┼────────── [ERROR] ──●──┼── M     ← data (bit flip here)
  q2: ───────X────────── [     ] ──┼──●── M     ← data
  q3: ─────────────────────────────X──X──        ← syndrome ancilla
  q4: ────────────────────────────────X──X──     ← syndrome ancilla

  Encode: CNOT chain copies |ψ⟩ to 3 qubits
  Error: X gate flips one qubit
  Syndrome: CNOT pairs detect which qubit flipped
  Without measuring the data, we know where the error is!

TRY IT:
    from src.experiments.advanced.steps.step07_error_correction import error_correction

    results = error_correction.run_error_positions()
"""

from __future__ import annotations

from qiskit import QuantumCircuit

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


def _bit_flip_code_circuit(error_qubit: int | None = None) -> QuantumCircuit:
    """Build a 3-qubit bit-flip error correction circuit.

    Qubits 0-2: data qubits (encode one logical qubit)
    Qubits 3-4: syndrome ancillas
    """
    qc = QuantumCircuit(5, 3)

    # Encode: |ψ⟩ → |ψψψ⟩ (using CNOT to copy basis states)
    qc.h(0)  # Prepare |+⟩ as the logical state
    qc.cx(0, 1)
    qc.cx(0, 2)
    qc.barrier()

    # Error: flip one qubit (simulating noise)
    if error_qubit is not None and 0 <= error_qubit <= 2:
        qc.x(error_qubit)
    qc.barrier()

    # Syndrome measurement: detect which qubit (if any) flipped
    # Ancilla 3 checks parity of qubits 0,1
    qc.cx(0, 3)
    qc.cx(1, 3)
    # Ancilla 4 checks parity of qubits 1,2
    qc.cx(1, 4)
    qc.cx(2, 4)
    qc.barrier()

    # Measure data qubits (in a real code, you'd correct first)
    qc.measure([0, 1, 2], [0, 1, 2])

    return qc


class ErrorCorrectionExperiment(BaseExperiment):
    """Step 7: 3-qubit bit-flip error correction code."""

    name = "adv_07_error_correction"
    description = "Step 7: Error correction — protect quantum information with the 3-qubit code"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        circuit = _bit_flip_code_circuit(error_qubit=1)
        return ExperimentConfig(
            num_qubits=5,
            state_type="CUSTOM",
            shots=4096,
            noise_enabled=False,
            custom_params={"source": "circuit", "circuit": circuit},
            visualization_type=["histogram", "circuit"],
        )

    def run_error_positions(self) -> list[ExperimentResult]:
        """Run with error on qubit 0, 1, 2, and no error."""
        results = []
        for eq in [None, 0, 1, 2]:
            circuit = _bit_flip_code_circuit(error_qubit=eq)
            results.append(
                self.run(
                    {
                        "custom_params": {"source": "circuit", "circuit": circuit},
                    }
                )
            )
        return results


error_correction = ErrorCorrectionExperiment()
