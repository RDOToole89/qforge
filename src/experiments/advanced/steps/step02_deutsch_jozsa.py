"""Step 2: Deutsch-Jozsa — Your first quantum speedup.

WHAT YOU'LL LEARN:
  The Deutsch-Jozsa algorithm is the simplest demonstration of
  quantum advantage. Given a black-box function f(x) that is either:
  - CONSTANT: f(x) = 0 for all x, or f(x) = 1 for all x
  - BALANCED: f(x) = 0 for half the inputs, f(x) = 1 for the other half

  Classically: you need to check at least N/2 + 1 inputs (worst case).
  Quantumly: ONE query is enough. Always. Guaranteed.

  This is exponential speedup for a specific problem.

HOW IT WORKS:
  1. Put all qubits in superposition (query ALL inputs simultaneously)
  2. Apply the oracle (black box function)
  3. Interfere the results with another Hadamard layer
  4. Measure: all zeros = constant, anything else = balanced

THE EXPERIMENT:
  We implement both constant and balanced oracles and verify that
  a single measurement correctly distinguishes them every time.

FRAMEWORK SKILL:
  You'll learn the "oracle model" — a pattern used in Grover's,
  Simon's, and many other quantum algorithms.

CIRCUIT (3-qubit input, balanced oracle):
  q0: ─H──────── oracle ──H── M     ← input register
  q1: ─H──────── oracle ──H── M     ← input register
  q2: ─H──────── oracle ──H── M     ← input register
  q3: ─X──H───── oracle ──────      ← output qubit (|−⟩)

  Oracle (balanced): CNOT from q0 to q3
  If constant → all zeros. If balanced → non-zero output.

TRY IT:
    from src.experiments.advanced.steps.step02_deutsch_jozsa import deutsch_jozsa

    constant, balanced = deutsch_jozsa.run_both_oracles()
"""

from __future__ import annotations

from qiskit import QuantumCircuit

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


def _dj_circuit(n: int, oracle_type: str = "balanced") -> QuantumCircuit:
    """Build Deutsch-Jozsa circuit with constant or balanced oracle."""
    qc = QuantumCircuit(n + 1, n)  # n input qubits + 1 output qubit

    # Initialize output qubit to |−⟩
    qc.x(n)
    qc.h(n)

    # Superposition on input qubits
    for i in range(n):
        qc.h(i)

    qc.barrier()

    # Oracle
    if oracle_type == "constant":
        pass  # f(x) = 0 for all x → do nothing
    elif oracle_type == "balanced":
        # f(x) = x[0] — balanced function using first bit
        qc.cx(0, n)

    qc.barrier()

    # Final Hadamard on input qubits
    for i in range(n):
        qc.h(i)

    # Measure input qubits only
    qc.measure(range(n), range(n))
    return qc


class DeutschJozsaExperiment(BaseExperiment):
    """Step 2: Deutsch-Jozsa — distinguish constant from balanced in one query."""

    name = "adv_02_deutsch_jozsa"
    description = "Step 2: Deutsch-Jozsa — exponential speedup for function classification"

    def default_config(self) -> ExperimentConfig:
        circuit = _dj_circuit(4, "balanced")
        return ExperimentConfig(
            num_qubits=5,
            state_type="CUSTOM",
            shots=1024,
            noise_enabled=False,
            custom_params={"source": "circuit", "circuit": circuit},
        )

    def run_both_oracles(self) -> tuple[ExperimentResult, ExperimentResult]:
        """Run with constant and balanced oracles, compare outcomes."""
        const_circuit = _dj_circuit(4, "constant")
        bal_circuit = _dj_circuit(4, "balanced")

        constant = self.run({
            "custom_params": {"source": "circuit", "circuit": const_circuit},
        })
        balanced = self.run({
            "custom_params": {"source": "circuit", "circuit": bal_circuit},
        })
        return constant, balanced


deutsch_jozsa = DeutschJozsaExperiment()
