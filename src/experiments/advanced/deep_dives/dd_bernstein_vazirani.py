"""Deep Dive: Bernstein-Vazirani — Find a hidden string in one query.

BEST AFTER: Step 2 (Deutsch-Jozsa)

WHAT YOU'LL LEARN:
  Given a function f(x) = s·x (dot product with hidden string s),
  classically you need N queries to find s (one per bit).
  Quantumly: ONE query reveals the entire string.

  This is a more practical version of Deutsch-Jozsa — it finds
  specific information, not just a yes/no classification.

CIRCUIT (secret = "101"):
  q0: ─H──────── oracle ──H── M     ← input (secret bit 1)
  q1: ─H──────── oracle ──H── M     ← input (secret bit 0)
  q2: ─H──────── oracle ──H── M     ← input (secret bit 1)
  q3: ─X──H───── oracle ──────      ← output qubit

  Oracle: CNOT from each input qubit where secret bit = 1
  One measurement reveals the ENTIRE secret string.
  Classical: need N queries. Quantum: need 1.

TRY IT:
    from src.experiments.advanced.deep_dives.dd_bernstein_vazirani import bernstein_vazirani

    results = bernstein_vazirani.run_hidden_strings()
"""

from __future__ import annotations

from qiskit import QuantumCircuit

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


def _bv_circuit(secret: str) -> QuantumCircuit:
    """Build Bernstein-Vazirani circuit for a secret string."""
    n = len(secret)
    qc = QuantumCircuit(n + 1, n)

    qc.x(n)
    qc.h(n)
    for i in range(n):
        qc.h(i)

    qc.barrier()

    # Oracle: f(x) = s·x
    for i, bit in enumerate(secret):
        if bit == "1":
            qc.cx(i, n)

    qc.barrier()

    for i in range(n):
        qc.h(i)
    qc.measure(range(n), range(n))
    return qc


class BernsteinVaziraniExperiment(BaseExperiment):
    """Deep Dive: Find a hidden binary string in one quantum query."""

    name = "dd_bernstein_vazirani"
    description = "Deep dive: Bernstein-Vazirani — find a hidden string in one query"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        circuit = _bv_circuit("1011")
        return ExperimentConfig(
            num_qubits=5,
            state_type="CUSTOM",
            shots=1024,
            noise_enabled=False,
            custom_params={"source": "circuit", "circuit": circuit},
            visualization_type=["histogram", "circuit"],
        )

    def run_hidden_strings(self) -> list[ExperimentResult]:
        """Find several different hidden strings."""
        results = []
        for secret in ["101", "1011", "11001", "101010"]:
            circuit = _bv_circuit(secret)
            results.append(
                self.run(
                    {
                        "num_qubits": len(secret) + 1,
                        "custom_params": {"source": "circuit", "circuit": circuit},
                    }
                )
            )
        return results


bernstein_vazirani = BernsteinVaziraniExperiment()
