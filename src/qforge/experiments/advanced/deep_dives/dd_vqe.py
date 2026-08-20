"""VQE — Variational Quantum Eigensolver for molecular simulation.

What you'll learn:
  - How variational algorithms combine quantum and classical computation
  - The parameterized circuit (ansatz) approach to quantum chemistry
  - Why VQE is considered a near-term quantum advantage candidate
  - How noise affects convergence of the optimization

VQE finds the ground state energy of a molecular Hamiltonian by:
  1. Prepare a parameterized quantum state (ansatz)
  2. Measure the energy expectation value on the quantum computer
  3. Use a classical optimizer to adjust parameters
  4. Repeat until convergence

This experiment uses a simplified 2-qubit H2 (hydrogen molecule)
Hamiltonian — the standard VQE benchmark.

Try it:
    from qforge.experiments.advanced.vqe import vqe_experiment

    # Run VQE for H2 at equilibrium bond distance
    result = vqe_experiment.run()

    # Sweep bond distances to trace the potential energy surface
    results = vqe_experiment.run_bond_sweep()

    # See how noise affects the ground state energy estimate
    results = vqe_experiment.CIRCUIT (2-qubit hardware-efficient ansatz):
  q0: ─Ry(θ)──●── M
  q1: ─Ry(θ)──X── M

  θ is the variational parameter, optimized classically.
  In a real VQE loop: measure → compute energy → update θ → repeat.
  The ansatz structure determines which states are reachable.

run_noise_sweep()

Note:
  This is a simplified, educational VQE implementation. For production
  molecular simulation, use Qiskit Nature with full Hamiltonian construction.

WHAT YOU'LL EXPLORE:
  - How parameterized quantum circuits (ansatz) encode molecular states
  - The hybrid quantum-classical optimization loop
  - How the H-H bond distance affects ground state energy
  - Why noise in the quantum circuit leads to energy estimation errors

TRY IT:
    from qforge.experiments.advanced.deep_dives.dd_vqe import vqe_experiment

    # H2 at equilibrium bond distance
    result = vqe_experiment.run()

    # Trace the potential energy surface
    results = vqe_experiment.run_bond_sweep()
"""

from __future__ import annotations

from typing import Any

import numpy as np
from qiskit import QuantumCircuit

from qforge.engine.models import ExperimentConfig, ExperimentResult
from qforge.experiments.base import BaseExperiment


def _build_vqe_ansatz(n_qubits: int = 2, depth: int = 1, theta: float = 0.0) -> QuantumCircuit:
    """Build a hardware-efficient VQE ansatz.

    A simple Ry + CNOT layered ansatz suitable for 2-qubit H2 simulation.
    In a real VQE loop, theta would be optimized classically.
    """
    qc = QuantumCircuit(n_qubits, n_qubits)

    for layer in range(depth):
        for q in range(n_qubits):
            qc.ry(theta + 0.5 * layer, q)
        for q in range(n_qubits - 1):
            qc.cx(q, q + 1)

    qc.measure(range(n_qubits), range(n_qubits))
    return qc


class VQEExperiment(BaseExperiment):
    """Variational Quantum Eigensolver for H2.

    Uses a hardware-efficient ansatz on 2 qubits to find the ground
    state energy of the hydrogen molecule at various bond distances.
    """

    name = "vqe"
    description = "VQE — find molecular ground state energy with a hybrid quantum-classical loop"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        circuit = _build_vqe_ansatz(n_qubits=2, depth=1, theta=0.5)
        return ExperimentConfig(
            num_qubits=2,
            state_type="CUSTOM",
            shots=4096,
            noise_enabled=False,
            custom_params={
                "source": "circuit",
                "circuit": circuit,
                "bond_distance": 0.735,
                "ansatz_depth": 1,
            },
            visualization_type=["histogram", "circuit"],
        )

    def run_bond_sweep(self, **overrides: Any) -> list[ExperimentResult]:
        """Sweep H-H bond distance to trace the potential energy surface."""
        distances = [0.3, 0.5, 0.735, 1.0, 1.5, 2.0, 2.5]
        results = []
        for d in distances:
            r = self.run({"custom_params": {"bond_distance": d, "ansatz_depth": 1}, **overrides})
            results.append(r)
        return results

    def run_noise_sweep(
        self,
        steps: int = 5,
        max_error: float = 0.1,
        **overrides: Any,
    ) -> list[ExperimentResult]:
        """See how noise affects the ground state energy estimate."""
        rates = np.linspace(0.001, max_error, steps).tolist()
        return self.sweep(
            parameter_ranges={"error_rate": rates},
            noise_enabled=True,
            noise_type="depolarizing",
            **overrides,
        )


vqe_experiment = VQEExperiment()
