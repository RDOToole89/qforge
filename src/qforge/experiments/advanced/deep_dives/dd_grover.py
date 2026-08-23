"""Grover's Search — Find a needle in a quantum haystack.

What you'll learn:
  - How quantum amplitude amplification works
  - Why Grover's gives a quadratic speedup (√N vs N)
  - How the oracle marks the target state
  - How noise degrades the amplification

Grover's algorithm searches an unstructured database of N items
in O(√N) steps, compared to O(N) classically. It works by:
  1. Start in uniform superposition (all items equally likely)
  2. Oracle: flip the phase of the target item
  3. Diffusion: amplify the marked item's amplitude
  4. Repeat steps 2-3 about √N times
  5. Measure — target item appears with high probability

Try it:
    from qforge.experiments.advanced.grover import grover_experiment

    # Search 4 qubits (16 items) for item |1010⟩
    result = grover_experiment.run()

    # Search for a different target
    result = grover_experiment.run({"custom_params": {"target": "0110"}})

    # See how success probability changes with qubit count
    results = grover_experiment.CIRCUIT (4-qubit Grover, target |1010⟩):
  q0: ─H── [X─────MCX─────X] ── [H─X─────MCX─────X─H] ── M
  q1: ─H── [  ─────   ─────  ] ── [H─X─────   ─────X─H] ── M
  q2: ─H── [X─────MCX─────X] ── [H─X─────MCX─────X─H] ── M
  q3: ─H── [  ─H──   ──H──  ] ── [H─X──H──   ──H──X─H] ── M
            └── oracle ──────┘    └── diffusion ────────┘

  Repeat oracle + diffusion √N ≈ 3 times for 4 qubits.
  Target appears with >96% probability.

run_scaling()

WHAT YOU'LL EXPLORE:
  - How amplitude amplification boosts the target's probability
  - The optimal number of Grover iterations for different search space sizes
  - How success probability changes with qubit count (scaling)
  - Why too many iterations DECREASE success (over-rotation)

TRY IT:
    from qforge.experiments.advanced.deep_dives.dd_grover import grover_experiment

    # Search 16 items for |1010⟩
    result = grover_experiment.run()

    # See speedup at different sizes
    results = grover_experiment.run_scaling()
"""

from __future__ import annotations

from typing import Any

import numpy as np
from qiskit import QuantumCircuit

from qforge.engine.models import ExperimentConfig, ExperimentResult
from qforge.experiments.base import BaseExperiment


def _build_grover_circuit(
    n_qubits: int, target: str, n_iterations: int | None = None
) -> QuantumCircuit:
    """Build Grover's search circuit.

    Args:
        n_qubits: Number of qubits (searches 2^n_qubits items)
        target: Target bitstring to find (e.g., "1010")
        n_iterations: Number of Grover iterations (default: optimal √N)
    """
    if n_iterations is None:
        n_iterations = max(1, int(np.pi / 4 * np.sqrt(2**n_qubits)))

    qc = QuantumCircuit(n_qubits, n_qubits)

    # Initial superposition
    qc.h(range(n_qubits))

    for _ in range(n_iterations):
        # Oracle: flip phase of target state
        for i, bit in enumerate(target):
            if bit == "0":
                qc.x(i)
        qc.h(n_qubits - 1)
        qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
        qc.h(n_qubits - 1)
        for i, bit in enumerate(target):
            if bit == "0":
                qc.x(i)

        # Diffusion operator (amplify marked state)
        qc.h(range(n_qubits))
        qc.x(range(n_qubits))
        qc.h(n_qubits - 1)
        qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
        qc.h(n_qubits - 1)
        qc.x(range(n_qubits))
        qc.h(range(n_qubits))

    qc.measure(range(n_qubits), range(n_qubits))
    return qc


class GroverExperiment(BaseExperiment):
    """Grover's unstructured search algorithm.

    Demonstrates quadratic quantum speedup. Default: search
    16 items (4 qubits) for target |1010⟩.
    """

    name = "grover"
    description = "Grover's search — find a marked item with quadratic speedup"
    metrics_hint = (
        "The target bitstring should dominate. Concentration Index is the "
        "search-success meter."
    )
    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        target = "1010"
        circuit = _build_grover_circuit(len(target), target)
        return ExperimentConfig(
            num_qubits=len(target),
            visualization_type=["histogram", "circuit"],
            state_type="CUSTOM",
            shots=4096,
            noise_enabled=False,
            metrics=["concentration_index", "asymmetry_index"],
            custom_params={
                "source": "circuit",
                "circuit": circuit,
                "target": target,
            },
        )

    def run_scaling(
        self, qubit_range: list[int] | None = None, **overrides: Any
    ) -> list[ExperimentResult]:
        """Run at multiple qubit counts to see success probability scale."""
        qubits = qubit_range or [2, 3, 4, 5]
        targets = {2: "10", 3: "101", 4: "1010", 5: "10101"}
        results = []
        for n in qubits:
            target = targets.get(n, "1" * (n // 2) + "0" * (n - n // 2))
            r = self.run({"num_qubits": n, "custom_params": {"target": target}, **overrides})
            results.append(r)
        return results


grover_experiment = GroverExperiment()
