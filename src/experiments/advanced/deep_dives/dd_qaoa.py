"""QAOA — Quantum Approximate Optimization Algorithm.

What you'll learn:
  - How quantum algorithms solve combinatorial optimization problems
  - The cost/mixer operator structure of QAOA
  - Why QAOA is a leading candidate for near-term quantum advantage
  - How circuit depth (p layers) affects solution quality

QAOA solves combinatorial optimization problems (like MaxCut) by:
  1. Encode the problem as a cost Hamiltonian on qubits
  2. Apply alternating cost and mixer layers (parameterized)
  3. Measure and evaluate the cost function
  4. Classical optimizer adjusts parameters
  5. Repeat until the best solution is found

This experiment solves MaxCut on small graphs — find the partition
of vertices that maximizes the number of edges between groups.

Try it:
    from src.experiments.advanced.qaoa import qaoa_experiment

    # Solve MaxCut on a 4-vertex triangle+edge graph
    result = qaoa_experiment.run()

    # Increase QAOA depth for better solutions
    result = qaoa_experiment.run({"custom_params": {"p": 3}})

    # See how depth affects solution quality
    results = qaoa_experiment.CIRCUIT (4-qubit QAOA, p=1 layer):
  q0: ─H── [ZZ(γ)] ── [Rx(2β)] ── M
  q1: ─H── [ZZ(γ)] ── [Rx(2β)] ── M
  q2: ─H── [ZZ(γ)] ── [Rx(2β)] ── M
  q3: ─H── [ZZ(γ)] ── [Rx(2β)] ── M

  ZZ(γ): CNOT-Rz-CNOT for each edge in the graph
  Rx(2β): mixer rotation on all qubits
  More layers (higher p) = better solutions but deeper circuit.

run_depth_sweep()

Note:
  This is a simplified QAOA for learning. For production optimization,
  use Qiskit Optimization with full problem encoding.

WHAT YOU'LL EXPLORE:
  - How combinatorial optimization maps to a quantum Hamiltonian
  - The cost/mixer layer structure of QAOA
  - How increasing QAOA depth (p) improves solution quality
  - The MaxCut problem and its optimal solutions

TRY IT:
    from src.experiments.advanced.deep_dives.dd_qaoa import qaoa_experiment

    # MaxCut on 4-vertex graph
    result = qaoa_experiment.run()

    # See quality improve with depth
    results = qaoa_experiment.run_depth_sweep()
"""

from __future__ import annotations

from typing import Any

import numpy as np
from qiskit import QuantumCircuit

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


def _build_qaoa_circuit(
    n_qubits: int, edges: list[list[int]], p: int = 1,
    gamma: float = 0.5, beta: float = 0.5,
) -> QuantumCircuit:
    """Build a QAOA circuit for MaxCut.

    Args:
        n_qubits: Number of vertices in the graph
        edges: List of [i, j] edges
        p: Number of QAOA layers
        gamma: Cost layer parameter
        beta: Mixer layer parameter
    """
    qc = QuantumCircuit(n_qubits, n_qubits)

    # Initial superposition
    qc.h(range(n_qubits))

    for layer in range(p):
        # Cost layer: ZZ interaction for each edge
        for i, j in edges:
            qc.cx(i, j)
            qc.rz(gamma * (layer + 1) / p, j)
            qc.cx(i, j)

        # Mixer layer: X rotation on all qubits
        for q in range(n_qubits):
            qc.rx(2 * beta * (layer + 1) / p, q)

    qc.measure(range(n_qubits), range(n_qubits))
    return qc


class QAOAExperiment(BaseExperiment):
    """QAOA for MaxCut on small graphs.

    Demonstrates quantum approximate optimization on a 4-vertex graph.
    The default graph is a square (4 edges) — simple enough
    to verify the solution classically.
    """

    name = "qaoa"
    description = "QAOA — solve MaxCut combinatorial optimization with quantum circuits"

    def default_config(self) -> ExperimentConfig:
        edges = [[0, 1], [1, 2], [2, 3], [0, 3]]
        circuit = _build_qaoa_circuit(4, edges, p=1)
        return ExperimentConfig(
            num_qubits=4,
            state_type="CUSTOM",
            shots=4096,
            noise_enabled=False,
            custom_params={
                "source": "circuit",
                "circuit": circuit,
                "p": 1,
                "edges": edges,
            },
        )

    def run_depth_sweep(self, **overrides: Any) -> list[ExperimentResult]:
        """Run QAOA at increasing depths to see solution quality improve."""
        results = []
        for p in [1, 2, 3, 4, 5]:
            r = self.run({"custom_params": {"p": p, "edges": [[0, 1], [1, 2], [2, 3], [0, 3]]}, **overrides})
            results.append(r)
        return results


qaoa_experiment = QAOAExperiment()
