# src/analysis/bloch.py

"""
Bloch sphere analysis for quantum states.

This module provides functions to compute and analyze Bloch vectors
for quantum states, which represent the state on the Bloch sphere.
"""

import numpy as np
import logging
from typing import Union, List, Dict
from qiskit.quantum_info import Pauli, DensityMatrix

logger = logging.getLogger("QuantumExperiment.Analysis.Bloch")


def compute_bloch_vector(rho: Union[np.ndarray, DensityMatrix]) -> tuple:
    """
    Computes the Bloch vector for a single qubit density matrix.

    The Bloch vector represents the quantum state as a point on the
    Bloch sphere, with components (x, y, z) corresponding to the
    expectation values of Pauli X, Y, and Z operators.

    Args:
        rho (Union[np.ndarray, DensityMatrix]): Density matrix of a single qubit.

    Returns:
        tuple: (x, y, z) components of the Bloch vector.
    """
    pauli_x = Pauli("X").to_matrix()
    pauli_y = Pauli("Y").to_matrix()
    pauli_z = Pauli("Z").to_matrix()
    # If rho is a DensityMatrix, convert it to a NumPy array
    rho_array = rho.data if isinstance(rho, DensityMatrix) else rho
    x = np.trace(rho_array @ pauli_x).real
    y = np.trace(rho_array @ pauli_y).real
    z = np.trace(rho_array @ pauli_z).real
    return (x, y, z)


def compute_bloch_vectors_for_all_qubits(
    density_matrix: np.ndarray, num_qubits: int
) -> Dict[int, tuple]:
    """
    Computes Bloch vectors for all individual qubits in a multi-qubit state.

    Args:
        density_matrix (np.ndarray): Density matrix of the multi-qubit state.
        num_qubits (int): Number of qubits.

    Returns:
        Dict[int, tuple]: Dictionary mapping qubit index to Bloch vector (x, y, z).
    """
    from qiskit.quantum_info import partial_trace

    density_matrix = DensityMatrix(density_matrix)
    bloch_vectors = {}

    for qubit in range(num_qubits):
        # Trace out all qubits except the current qubit
        qubits_to_trace_out = [k for k in range(num_qubits) if k != qubit]
        rho_qubit = partial_trace(density_matrix, qargs=qubits_to_trace_out)
        bloch_vector = compute_bloch_vector(rho_qubit)
        bloch_vectors[qubit] = bloch_vector

    return bloch_vectors


def compute_bloch_trajectories(
    density_matrices: List[Dict], num_qubits: int
) -> List[Dict[int, tuple]]:
    """
    Computes Bloch vector trajectories over time for all qubits.

    Args:
        density_matrices (List[Dict]): List of density matrices over time.
        num_qubits (int): Number of qubits.

    Returns:
        List[Dict[int, tuple]]: List of Bloch vector dictionaries for each time step.
    """
    trajectories = []

    for data in density_matrices:
        if "density" in data:
            density_matrix = np.array(data["density"])
            bloch_vectors = compute_bloch_vectors_for_all_qubits(
                density_matrix, num_qubits
            )
            trajectories.append(bloch_vectors)

    return trajectories


def analyze_bloch_purity(bloch_vector: tuple) -> float:
    """
    Analyzes the purity of a quantum state based on its Bloch vector.

    Args:
        bloch_vector (tuple): (x, y, z) components of the Bloch vector.

    Returns:
        float: Purity of the state (0 = maximally mixed, 1 = pure).
    """
    x, y, z = bloch_vector
    # Purity = (1 + |r|²)/2 where |r| is the length of the Bloch vector
    r_squared = x**2 + y**2 + z**2
    purity = (1 + r_squared) / 2
    return min(purity, 1.0)  # Ensure purity ≤ 1


def compute_bloch_distance(bloch1: tuple, bloch2: tuple) -> float:
    """
    Computes the Euclidean distance between two Bloch vectors.

    Args:
        bloch1 (tuple): First Bloch vector (x, y, z).
        bloch2 (tuple): Second Bloch vector (x, y, z).

    Returns:
        float: Euclidean distance between the Bloch vectors.
    """
    x1, y1, z1 = bloch1
    x2, y2, z2 = bloch2
    distance = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)
    return distance


def analyze_bloch_evolution(
    bloch_trajectories: List[Dict[int, tuple]],
) -> Dict[int, Dict]:
    """
    Analyzes the evolution of Bloch vectors over time.

    Args:
        bloch_trajectories (List[Dict[int, tuple]]): Bloch vector trajectories.

    Returns:
        Dict[int, Dict]: Analysis for each qubit.
    """
    if not bloch_trajectories:
        return {}

    num_qubits = len(bloch_trajectories[0])
    analysis = {}

    for qubit in range(num_qubits):
        qubit_trajectory = [traj[qubit] for traj in bloch_trajectories]

        # Compute total distance traveled
        total_distance = 0.0
        for i in range(len(qubit_trajectory) - 1):
            distance = compute_bloch_distance(
                qubit_trajectory[i], qubit_trajectory[i + 1]
            )
            total_distance += distance

        # Compute average purity
        purities = [analyze_bloch_purity(bv) for bv in qubit_trajectory]
        avg_purity = np.mean(purities)

        # Compute final purity
        final_purity = purities[-1] if purities else 0.0

        analysis[qubit] = {
            "total_distance": total_distance,
            "avg_purity": avg_purity,
            "final_purity": final_purity,
            "purity_change": final_purity - purities[0] if purities else 0.0,
            "trajectory_length": len(qubit_trajectory),
        }

    return analysis
