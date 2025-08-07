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
                    zz_corr += zz_value * (int(count) / shots)
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
                zz_corr += zz_value * (int(count) / shots)
            zz_symmetric += zz_corr
            pairs += 1
    return zz_symmetric / pairs if pairs > 0 else 0.0


def compute_adaptive_threshold(
    correlation_data: Dict,
    num_qubits: int,
    mode: str,
    target_edge_count: int = None,
    percentile: float = 75.0,
) -> float:
    """
    Computes an adaptive threshold for hypergraph edge inclusion.

    Uses statistical analysis to automatically determine optimal thresholds
    based on the correlation distribution, ensuring meaningful visualizations.

    Args:
        correlation_data (Dict): Counts or density matrix data.
        num_qubits (int): Number of qubits.
        mode (str): 'qasm' or 'density'.
        target_edge_count (int): Target number of edges (None for percentile-based).
        percentile (float): Percentile for threshold selection (default: 75%).

    Returns:
        float: Adaptive threshold value.
    """
    if mode == "qasm":
        # Handle both dict and Counts objects
        if hasattr(correlation_data, 'shots'):
            shots = correlation_data.shots()
        else:
            shots = sum(int(count) for count in correlation_data.values())
    else:
        shots = 1
    correlation_values = []

    if mode == "qasm":
        # Compute all possible correlations to find distribution
        for r in range(2, min(num_qubits + 1, 4)):  # Up to 3-qubit correlations
            for qubit_subset in combinations(range(num_qubits), r):
                corr = 0.0
                for bitstring, count in correlation_data.items():
                    bits = [int(bitstring[i]) for i in qubit_subset]
                    value = (-1) ** sum(bits)
                    corr += value * (int(count) / shots)
                correlation_values.append(abs(corr))
    else:
        # For density matrix mode, analyze off-diagonal elements
        if "density" in correlation_data:
            density_matrix = np.array(correlation_data["density"])
            for i in range(density_matrix.shape[0]):
                for j in range(i + 1, density_matrix.shape[1]):
                    corr = abs(density_matrix[i, j])
                    correlation_values.append(corr)

    if not correlation_values:
        # Fallback to default values
        return 0.1 if mode == "qasm" else 0.01

    correlation_values = np.array(correlation_values)

    # Remove zero correlations for better statistics
    nonzero_correlations = correlation_values[correlation_values > 1e-10]

    if len(nonzero_correlations) == 0:
        return 0.1 if mode == "qasm" else 0.01

    # Strategy 1: Target edge count (if specified)
    if target_edge_count is not None:
        sorted_corrs = np.sort(nonzero_correlations)[::-1]  # Descending
        if len(sorted_corrs) > target_edge_count:
            threshold = sorted_corrs[target_edge_count - 1]
        else:
            threshold = sorted_corrs[-1] * 0.5  # Half of smallest

        logger.info(f"Adaptive threshold (target {target_edge_count} edges): {threshold:.6f}")
        return float(threshold)

    # Strategy 2: Percentile-based threshold
    threshold = np.percentile(nonzero_correlations, percentile)

    # Add some intelligence: avoid too many or too few edges
    mean_corr = np.mean(nonzero_correlations)
    std_corr = np.std(nonzero_correlations)

    # If threshold is too low (would create too many edges), raise it
    if threshold < mean_corr - std_corr:
        threshold = mean_corr - 0.5 * std_corr
        logger.info(f"Adjusted threshold upward to avoid too many edges: {threshold:.6f}")

    # If threshold is too high (would create too few edges), lower it
    elif threshold > mean_corr + std_corr:
        threshold = mean_corr + 0.5 * std_corr
        logger.info(f"Adjusted threshold downward to ensure sufficient edges: {threshold:.6f}")

    logger.info(f"Adaptive threshold (mode={mode}, percentile={percentile}%): {threshold:.6f}")
    logger.info(f"  Correlation stats: mean={mean_corr:.6f}, std={std_corr:.6f}")
    logger.info(f"  Total correlations analyzed: {len(correlation_values)}")

    return float(threshold)


def compute_correlations_for_hypergraph(
    correlation_data: Dict,
    num_qubits: int,
    mode: str,
    config: Dict,
) -> Dict:
    """
    Computes correlations and builds hypergraph edges with adaptive thresholds.

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
    if mode == "qasm":
        # Handle both dict and Counts objects
        if hasattr(correlation_data, 'shots'):
            shots = correlation_data.shots()
        else:
            shots = sum(int(count) for count in correlation_data.values())
    else:
        shots = 1

    # Enhanced threshold selection with adaptive capabilities
    threshold = config.get("threshold")
    use_adaptive = config.get("adaptive_threshold", True)
    target_edges = config.get("target_edge_count", None)
    percentile = config.get("threshold_percentile", 75.0)

    if threshold is None or use_adaptive:
        if use_adaptive:
            threshold = compute_adaptive_threshold(
                correlation_data, num_qubits, mode, target_edges, percentile
            )
            logger.info(f"Using adaptive threshold: {threshold:.6f}")
        else:
            threshold = 0.1 if mode == "qasm" else 0.01
            logger.info(f"Using default threshold: {threshold:.6f}")
    else:
        logger.info(f"Using manual threshold: {threshold:.6f}")

    max_order = config.get("max_order", 2)

    if mode == "qasm":
        for r in range(2, max_order + 1):
            for qubit_subset in combinations(range(num_qubits), r):
                corr = 0.0
                for bitstring, count in correlation_data.items():
                    bits = [int(bitstring[i]) for i in qubit_subset]
                    value = (-1) ** sum(bits)
                    corr += value * (int(count) / shots)
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
