# src/analysis/symmetry.py

"""
Symmetry analysis for quantum states.

This module provides functions to analyze various types of symmetry
in quantum states, including SU(2), SU(3), and parity symmetries.
"""

import numpy as np
import logging
from typing import Dict
from qiskit.quantum_info import partial_trace, Pauli, DensityMatrix

logger = logging.getLogger("QuantumExperiment.Analysis.Symmetry")


def compute_su2_symmetry(counts: Dict, num_qubits: int, shots: float) -> Dict:
    """
    Computes SU(2) symmetry metrics based on ZZ correlations.

    SU(2) symmetry in quantum states refers to rotational invariance
    around the Bloch sphere. This function analyzes how well the state
    preserves this symmetry by examining ZZ correlations.

    Args:
        counts (Dict): Measurement counts.
        num_qubits (int): Number of qubits.
        shots (float): Total number of shots.

    Returns:
        Dict: SU(2) symmetry metrics including correlations and variance.
    """
    correlations = {"XX": {}, "YY": {}, "ZZ": {}}
    for i in range(num_qubits):
        for j in range(i + 1, num_qubits):
            zz_corr = 0.0
            for bitstring, count in counts.items():
                bit_i, bit_j = int(bitstring[i]), int(bitstring[j])
                zz_value = (-1) ** (bit_i + bit_j)
                zz_corr += zz_value * (int(count) / shots)
            correlations["ZZ"][(i, j)] = zz_corr
    zz_values = list(correlations["ZZ"].values())
    su2_symmetry = np.var(zz_values) if zz_values else 0.0
    return {"correlations": correlations, "su2_symmetry": su2_symmetry}


def compute_su3_symmetry(density_matrix: np.ndarray, num_qubits: int) -> float:
    """
    Computes Z-symmetry variance across all qubits (not true SU(3) symmetry).

    This function analyzes the variance of Pauli Z expectations across qubits,
    which provides a measure of how symmetric the state is with respect to
    Z-axis rotations.

    Args:
        density_matrix (np.ndarray): The density matrix of the quantum state.
        num_qubits (int): Number of qubits.

    Returns:
        float: Variance of Pauli Z expectations across qubits.
    """
    if num_qubits < 1:
        return 0.0

    # Convert to DensityMatrix object
    density_matrix = DensityMatrix(density_matrix)
    # Compute Pauli Z expectations for each qubit (up to num_qubits)
    expectations = []
    pauli_z = Pauli("Z").to_matrix()
    for qubit in range(num_qubits):  # Loop over available qubits
        # Trace out all qubits except the current qubit
        qubits_to_trace_out = [k for k in range(num_qubits) if k != qubit]
        rho_qubit = partial_trace(density_matrix, qargs=qubits_to_trace_out)
        # Compute expectation value of Pauli Z for this qubit
        expectation = np.trace(rho_qubit.data @ pauli_z).real
        expectations.append(expectation)
    # Return the variance of the Pauli Z expectations as a symmetry metric
    return np.var(expectations) if expectations else 0.0


def compute_parity_distribution(counts: Dict, num_qubits: int) -> Dict:
    """
    Computes the parity distribution (even/odd) of measurement outcomes.

    Parity symmetry refers to the invariance of the state under
    bit-flip operations. This function analyzes how the measurement
    outcomes are distributed between even and odd parity states.

    Args:
        counts (Dict): Measurement counts.
        num_qubits (int): Number of qubits.

    Returns:
        Dict: Parity distribution {'even': float, 'odd': float}.
    """
    parity_counts = {"even": 0, "odd": 0}
    shots = sum(int(count) for count in counts.values())
    if shots == 0:
        return parity_counts
    for bitstring, count in counts.items():
        parity = sum(int(bit) for bit in bitstring) % 2
        parity_counts["even" if parity == 0 else "odd"] += int(count) / shots
    return parity_counts


def analyze_symmetry_breaking(
    initial_symmetry: float, final_symmetry: float, threshold: float = 0.1
) -> Dict:
    """
    Analyzes symmetry breaking between initial and final states.

    Args:
        initial_symmetry (float): Symmetry measure of initial state.
        final_symmetry (float): Symmetry measure of final state.
        threshold (float): Threshold for significant symmetry breaking.

    Returns:
        Dict: Analysis of symmetry breaking.
    """
    symmetry_change = abs(final_symmetry - initial_symmetry)
    significant_breaking = symmetry_change > threshold

    return {
        "initial_symmetry": initial_symmetry,
        "final_symmetry": final_symmetry,
        "symmetry_change": symmetry_change,
        "significant_breaking": significant_breaking,
        "breaking_direction": (
            "increased" if final_symmetry > initial_symmetry else "decreased"
        ),
    }


def compute_permutation_invariance(correlations: Dict, num_qubits: int) -> float:
    """
    Computes permutation invariance of correlations.

    This function analyzes how invariant the correlations are under
    permutations of qubit labels, which is a measure of the state's
    permutation symmetry.

    Args:
        correlations (Dict): Dictionary of correlations {(i,j): corr}.
        num_qubits (int): Number of qubits.

    Returns:
        float: Measure of permutation invariance (lower = more invariant).
    """
    if not correlations:
        return 0.0

    corr_values = list(correlations.values())
    if len(corr_values) < 2:
        return 0.0

    # Compute variance as a measure of invariance
    # Lower variance means more permutation invariant
    variance = np.var(corr_values)
    return variance
