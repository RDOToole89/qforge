"""Step 3: Single-Qubit Gates — The building blocks.

WHAT YOU'LL LEARN:
  Quantum computation is built from gates — operations that transform
  qubit states. Each gate is a rotation on the Bloch sphere.

THE GATES:
  X gate (NOT):  Flips |0⟩ ↔ |1⟩. A 180° rotation around the X axis.
                 Like a classical NOT gate.

  H gate (Hadamard): Creates superposition. |0⟩ → |+⟩, |1⟩ → |−⟩.
                     A 180° rotation around the X+Z axis (diagonal).

  Z gate (Phase): Flips the phase. |+⟩ → |−⟩. No effect on |0⟩ or |1⟩.
                  A 180° rotation around the Z axis.

  Y gate: Combines X and Z. |0⟩ → i|1⟩. 180° rotation around Y axis.

  S gate: Quarter turn around Z axis. √Z. Adds a 90° phase.

  T gate: Eighth turn around Z axis. √S. The smallest standard rotation.
          Critical for universal quantum computation.

THE EXPERIMENT:
  We apply each gate to |0⟩ and measure. The results show what each
  gate does to the simplest possible input state.

WHAT TO LOOK FOR:
  - X on |0⟩ → always get 1 (bit flip)
  - H on |0⟩ → 50/50 (superposition)
  - Z on |0⟩ → always get 0 (phase flip invisible in Z-basis)
  - S, T on |0⟩ → always get 0 (phase gates don't affect |0⟩)

  The Z, S, and T gates look like they do nothing! That's because
  Z-basis measurement can't see phase changes. You'd need to add
  an H gate before measurement to see the phase in X-basis.

CIRCUITS (each gate applied to |0⟩):
  X gate:  q: ─X─ M ───     (flip: always 1)
  H gate:  q: ─H─ M ───     (superposition: 50/50)
  Z gate:  q: ─Z─ M ───     (phase flip: always 0, phase invisible)
  Y gate:  q: ─Y─ M ───     (flip + phase: always 1)
  S gate:  q: ─S─ M ───     (quarter turn: always 0)
  T gate:  q: ─T─ M ───     (eighth turn: always 0)

TRY IT:
    from src.experiments.basics.step03_single_gates import single_gates

    results = single_gates.run_all_gates()
"""

from __future__ import annotations

from qiskit import QuantumCircuit

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


class SingleGatesExperiment(BaseExperiment):
    """Step 3: Apply each fundamental gate to |0⟩ and see the result."""

    name = "03_single_gates"
    description = "Step 3: See what X, H, Z, Y, S, T gates do to a qubit"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        qc = QuantumCircuit(1, 1)
        qc.h(0)
        qc.measure(0, 0)
        return ExperimentConfig(
            num_qubits=1,
            state_type="CUSTOM",
            shots=1024,
            noise_enabled=False,
            custom_params={"source": "circuit", "circuit": qc},
        )

    def run_all_gates(self) -> list[ExperimentResult]:
        """Apply each gate to |0⟩ and compare outcomes."""
        gates = ["x", "h", "z", "y", "s", "t"]
        results = []
        for gate_name in gates:
            qc = QuantumCircuit(1, 1)
            getattr(qc, gate_name)(0)
            qc.measure(0, 0)
            r = self.run(
                {
                    "custom_params": {"source": "circuit", "circuit": qc},
                }
            )
            results.append(r)
        return results


single_gates = SingleGatesExperiment()
