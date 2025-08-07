# src/analysis/correlations.py

"""
Correlation analysis for quantum states.

This module provides functions to compute various types of correlations
in quantum states, including pairwise correlations, conditional correlations,
and permutation-symmetric correlations.
"""

import numpy as np
import logging
from typing import Dict, List
from qiskit.quantum_info import partial_trace, Pauli, DensityMatrix
from itertools import combinations

logger = logging.getLogger("QuantumExperiment.Analysis.Correlations")


def compute_pairwise_correlations(
    correlation_data: Dict, num_qubits: int, mode: str, shots: float = 1.0
) -> Dict:
    """
    Computes pairwise ZZ correlations between qubits.

    Args:
        correlation_data (Dict): Counts or density matrix data.
        num_qubits (int): Number of qubits.
        mode (str): 'qasm' or 'density'.
        shots (float): Total number of shots (for QASM mode).

    Returns:
        Dict: Pairwise correlations as a dictionary {(i,j): corr}.
    """
    correlations = {}
    if mode == "qasm":
        for i in range(num_qubits):
            for j in range(i + 1, num_qubits):
                zz_corr = 0.0
                for bitstring, count in correlation_data.items():
                    bit_i, bit_j = int(bitstring[i]), int(bitstring[j])
                    zz_value = (-1) ** (bit_i + bit_j)
                    zz_corr += zz_value * (count / shots)
                correlations[(i, j)] = zz_corr
    else:
        # Convert the NumPy array to a DensityMatrix object
        density_matrix = DensityMatrix(np.array(correlation_data["density"]))
        pauli_z = Pauli("Z").to_matrix()
        for i in range(num_qubits):
            for j in range(i + 1, num_qubits):
                # Indices to trace out: all qubits except i and j
                all_qubits = list(range(num_qubits))
                qubits_to_trace_out = [k for k in all_qubits if k not in [i, j]]
                rho_ij = partial_trace(
                    density_matrix, qargs=qubits_to_trace_out  # Trace out these qubits
                )
                # Convert rho_ij to a NumPy array for matrix multiplication
                zz_corr = np.trace(np.kron(pauli_z, pauli_z) @ rho_ij.data).real
                correlations[(i, j)] = zz_corr
    return correlations


def compute_conditional_correlations(
    density_matrix: np.ndarray, num_qubits: int
) -> Dict:
    """
    Computes conditional ZZ correlations between pairs of qubits.

    Args:
        density_matrix (np.ndarray): Density matrix.
        num_qubits (int): Number of qubits.

    Returns:
        Dict: Conditional correlations {(i,j): corr}.
    """
    conditional_corrs = {}
    # Convert to DensityMatrix object
    density_matrix = DensityMatrix(density_matrix)
    pauli_z = Pauli("Z").to_matrix()
    for i in range(num_qubits):
        for j in range(num_qubits):
            if i != j:
                # Indices to trace out: all qubits except i and j
                all_qubits = list(range(num_qubits))
                qubits_to_trace_out = [k for k in all_qubits if k not in [i, j]]
                rho_ij = partial_trace(
                    density_matrix, qargs=qubits_to_trace_out  # Trace out these qubits
                )
                # Convert rho_ij to a NumPy array for matrix multiplication
                zz_corr = np.trace(np.kron(pauli_z, pauli_z) @ rho_ij.data)
                conditional_corrs[(i, j)] = zz_corr.real
    return conditional_corrs


def compute_permutation_symmetric_correlations(
    counts: Dict, num_qubits: int, shots: float
) -> float:
    """
    Computes permutation-symmetric ZZ correlations.

    Args:
        counts (Dict): Measurement counts.
        num_qubits (int): Number of qubits.
        shots (float): Total number of shots.

    Returns:
        float: Average ZZ correlation across all pairs.
    """
    zz_symmetric = 0.0
    pairs = 0
    for i in range(num_qubits):
        for j in range(i + 1, num_qubits):
            zz_corr = 0.0
            for bitstring, count in counts.items():
                bit_i, bit_j = int(bitstring[i]), int(bitstring[j])
                zz_value = (-1) ** (bit_i + bit_j)
                zz_corr += zz_value * (count / shots)
            zz_symmetric += zz_corr
            pairs += 1
    return zz_symmetric / pairs if pairs > 0 else 0.0


def compute_correlations_for_hypergraph(
    correlation_data: Dict,
    num_qubits: int,
    mode: str,
    config: Dict,
) -> Dict:
    """
    Computes correlations and builds hypergraph edges.

    Args:
        correlation_data (Dict): Counts or density matrix data.
        num_qubits (int): Number of qubits.
        mode (str): 'qasm' or 'density'.
        config (Dict): Visualization configuration.

    Returns:
        Dict: Hypergraph edges with weights.
    """
    edges = {}
    edge_id = 0
    shots = sum(correlation_data.values()) if mode == "qasm" else 1
    threshold = config.get("threshold")
    if threshold is None:
        threshold = 0.1 if mode == "qasm" else 0.01
    max_order = config.get("max_order", 2)

    if mode == "qasm":
        for r in range(2, max_order + 1):
            for qubit_subset in combinations(range(num_qubits), r):
                corr = 0.0
                for bitstring, count in correlation_data.items():
                    bits = [int(bitstring[i]) for i in qubit_subset]
                    value = (-1) ** sum(bits)
                    corr += value * (count / shots)
                if abs(corr) > threshold:
                    edge_nodes = frozenset([f"q{i}" for i in qubit_subset])
                    edges[f"e{edge_id}"] = (edge_nodes, {"weight": corr})
                    edge_id += 1
    else:
        if "density" not in correlation_data:
            raise KeyError(
                "Expected 'density' key in correlation_data for density mode"
            )
        density_matrix = np.array(correlation_data["density"])
        for i in range(density_matrix.shape[0]):
            for j in range(i + 1, density_matrix.shape[1]):
                corr = abs(density_matrix[i, j])
                if corr > threshold:
                    bitstring_i = format(i, f"0{num_qubits}b")
                    bitstring_j = format(j, f"0{num_qubits}b")
                    differing_qubits = [
                        k for k in range(num_qubits) if bitstring_i[k] != bitstring_j[k]
                    ]
                    if len(differing_qubits) >= 2:
                        edge_nodes = frozenset([f"q{k}" for k in differing_qubits])
                        edges[f"e{edge_id}"] = (edge_nodes, {"weight": corr})
                        edge_id += 1
    return edges
