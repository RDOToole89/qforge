"""
Correlation Analysis Utilities

Mathematical utilities for computing correlation matrices and adjacency
matrices used in entanglement-error correlation analysis.

This module provides:
- Mutual information matrices for multi-qubit systems
- Adjacency matrix construction from distance matrices
- Correlation analysis helpers for topology studies
"""

import logging
from collections.abc import Mapping

import numpy as np
from numpy.typing import NDArray

from ..constants import ALPHA, EEC_LAMBDA, validate_counts_dict
from .information_theory import mutual_information, n_qubits_from_counts

logger = logging.getLogger(__name__)


def mi_matrix(counts: Mapping[str, int], *, alpha: float = ALPHA) -> NDArray[np.float64]:
    """
    Compute mutual information matrix for all qubit pairs.

    Mathematical Definition:
        MI_matrix[i,j] = MI(X_i; X_j) for i ≠ j
        MI_matrix[i,i] = 0 (self-information excluded)

    This matrix captures pairwise information sharing between all qubits
    in the quantum system, forming the basis for topology correlation analysis.

    Args:
        counts: Joint measurement counts {bitstring: count}
        alpha: Jeffreys prior parameter for smoothing

    Returns:
        np.ndarray: n×n mutual information matrix (symmetric, zero diagonal)

    Raises:
        ValueError: If counts are invalid or insufficient

    Examples:
        >>> counts = {"00": 250, "01": 250, "10": 250, "11": 250}  # Independent
        >>> mi_mat = mi_matrix(counts)
        >>> print(f"MI[0,1] = {mi_mat[0,1]:.3f}")  # Should be ~0

        >>> counts = {"00": 500, "11": 500}  # Maximally correlated
        >>> mi_mat = mi_matrix(counts)
        >>> print(f"MI[0,1] = {mi_mat[0,1]:.3f}")  # Should be ~1

    Complexity:
        Time: O(n²) where n = number of qubits
        Space: O(n²) for the matrix

    Educational Notes:
        - MI matrix is symmetric: MI(X_i; X_j) = MI(X_j; X_i)
        - Diagonal is zero: qubits don't have MI with themselves
        - Upper triangle contains all unique pairwise MI values
        - Matrix eigenvalues relate to multi-qubit entanglement structure
    """
    counts_clean = validate_counts_dict(counts)
    n_qubits = n_qubits_from_counts(counts_clean)
    if n_qubits < 2:
        raise ValueError(f"Need ≥2 qubits for MI matrix, got {n_qubits}")

    mi_mat = np.zeros((n_qubits, n_qubits), dtype=np.float64)

    for i in range(n_qubits):
        for j in range(i + 1, n_qubits):
            mi_value = float(mutual_information(counts_clean, i, j, alpha=alpha))
            mi_mat[i, j] = mi_value
            mi_mat[j, i] = mi_value

    logger.debug(
        "Computed %dx%d MI matrix; %d pairs > 0.01 bits",
        n_qubits,
        n_qubits,
        int(np.sum(mi_mat > 0.01)),
    )

    return mi_mat


def adjacency_from_distances(distances: np.ndarray, lam: float = EEC_LAMBDA) -> NDArray[np.float64]:
    """
    Compute adjacency matrix from distance matrix using exponential decay.

    Mathematical Definition:
        A[i,j] = exp(-λ * d[i,j]) for i ≠ j
        A[i,i] = 0 (no self-adjacency)

    This converts physical or logical distances between qubits into
    a weighted adjacency matrix representing expected coupling strength.

    Physical Interpretation:
        - λ controls decay rate: larger λ → more local interactions
        - A[i,j] → 1 for neighboring qubits (d[i,j] → 0)
        - A[i,j] → 0 for distant qubits (d[i,j] → ∞)
        - Models exponential decay of quantum coupling with distance

    Args:
        distances: n×n distance matrix (symmetric, zero diagonal)
        lam: Decay parameter λ > 0 (default: EEC_LAMBDA)

    Returns:
        np.ndarray: n×n adjacency matrix with exponential decay weights

    Raises:
        ValueError: If distance matrix is invalid

    Examples:
        >>> # Linear chain topology
        >>> distances = np.array([[0, 1, 2], [1, 0, 1], [2, 1, 0]])
        >>> adj = adjacency_from_distances(distances, lam=1.0)
        >>> round(adj[0,1], 3), round(adj[0,2], 3)
        (0.368, 0.135)

        >>> distances = np.array([[0, 1, np.sqrt(2)], [1, 0, 1], [np.sqrt(2), 1, 0]])
        >>> adj = adjacency_from_distances(distances, lam=0.5)

    Complexity:
        Time: O(n²) for matrix exponentiation
        Space: O(n²) for adjacency matrix

    Educational Notes:
        - Exponential decay models realistic quantum coupling
        - λ = 1 gives moderate locality (common choice)
        - Can model various topologies: linear, 2D grid, all-to-all
        - Used in quantum error correction and connectivity analysis
    """
    distances = np.asarray(distances, dtype=np.float64)

    if distances.ndim != 2 or distances.shape[0] != distances.shape[1]:
        raise ValueError(f"Distance matrix must be square, got shape {distances.shape}")
    if not np.all(np.isfinite(distances)):
        raise ValueError("Distance matrix contains non-finite values (NaN/Inf)")

    n = distances.shape[0]
    if n < 2:
        raise ValueError(f"Need ≥2 qubits for adjacency matrix, got {n}")
    if lam <= 0:
        raise ValueError(f"Decay parameter λ must be positive, got {lam}")

    if not np.allclose(distances, distances.T):
        logger.warning("Distance matrix is not symmetric")
    if not np.allclose(np.diag(distances), 0):
        logger.warning("Distance matrix diagonal is not zero")
    if np.any(distances < 0):
        raise ValueError("Distance matrix contains negative values")

    adjacency = np.exp(-lam * distances).astype(np.float64)
    np.fill_diagonal(adjacency, 0.0)

    logger.debug(
        "Computed %dx%d adjacency (λ=%.3g), mean coupling=%.3f",
        n,
        n,
        lam,
        float(np.mean(adjacency[adjacency > 0])),
    )

    return adjacency


def get_topology_adjacency(topology_type: str, n_qubits: int) -> NDArray[np.float64]:
    """
    Get standard adjacency matrix for common quantum topologies.

    Args:
        topology_type: "linear", "ring", "grid", "all_to_all", or "star"
            - "grid": uses a near-rectangular 2D layout; if n_qubits is not
              a perfect square, the last row may be shorter ("ragged grid")
        n_qubits: Number of qubits

    Returns:
        np.ndarray: Adjacency matrix for the specified topology

    Examples:
        >>> adj_linear = get_topology_adjacency("linear", 4)
        >>> adj_ring = get_topology_adjacency("ring", 4)
        >>> adj_grid = get_topology_adjacency("grid", 4)  # 2×2 grid
    """
    if n_qubits < 2:
        raise ValueError(f"Need ≥2 qubits, got {n_qubits}")

    adj = np.zeros((n_qubits, n_qubits), dtype=np.float64)

    if topology_type == "linear":
        # Linear chain: nearest neighbors only
        for i in range(n_qubits - 1):
            adj[i, i + 1] = 1.0
            adj[i + 1, i] = 1.0

    elif topology_type == "ring":
        # Ring: linear chain + wraparound
        for i in range(n_qubits - 1):
            adj[i, i + 1] = 1.0
            adj[i + 1, i] = 1.0
        adj[0, n_qubits - 1] = 1.0
        adj[n_qubits - 1, 0] = 1.0

    elif topology_type == "grid":
        # Near-rectangular grid; handles non-perfect squares robustly
        rows = int(np.floor(np.sqrt(n_qubits)))
        cols = int(np.ceil(n_qubits / rows))
        if rows * cols != n_qubits:
            logger.warning(
                "Using rectangular grid %dx%d for %d qubits (ragged last row).",
                rows,
                cols,
                n_qubits,
            )

        for idx in range(n_qubits):
            r, c = divmod(idx, cols)

            # Right neighbor: stay within the same row and bounds
            if (c + 1) < cols and (idx + 1) < n_qubits and ((idx // cols) == ((idx + 1) // cols)):
                j = idx + 1
                adj[idx, j] = adj[j, idx] = 1.0

            # Down neighbor: next row exists and index in bounds
            if (r + 1) < rows and (idx + cols) < n_qubits:
                j = idx + cols
                adj[idx, j] = adj[j, idx] = 1.0

    elif topology_type == "all_to_all":
        # Complete graph
        adj = np.ones((n_qubits, n_qubits))
        np.fill_diagonal(adj, 0)

    elif topology_type == "star":
        # Star graph: central node connected to all others
        central = 0
        for i in range(1, n_qubits):
            adj[central, i] = adj[i, central] = 1.0

    else:
        raise ValueError(f"Unknown topology type: {topology_type}")

    logger.debug(
        f"Generated {topology_type} topology for {n_qubits} qubits, {np.sum(adj) / 2:.0f} edges"
    )

    return adj


def correlation_upper_triangle(matrix: np.ndarray) -> NDArray[np.float64]:
    """
    Extract upper triangle of correlation matrix as 1D array.

    This is useful for correlation analysis where we only need
    unique pairwise values (avoiding double-counting due to symmetry).

    Args:
        matrix: Symmetric correlation matrix

    Returns:
        np.ndarray: Upper triangle values as 1D array

    Examples:
        >>> mi_mat = mi_matrix(counts)
        >>> mi_values = correlation_upper_triangle(mi_mat)
        >>> print(f"Mean pairwise MI: {np.mean(mi_values):.3f}")
    """

    if not np.allclose(matrix, matrix.T, atol=1e-12):
        logger.warning(
            "Matrix not perfectly symmetric; upper-triangle may duplicate inconsistent entries."
        )

    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError(f"Matrix must be square, got shape {matrix.shape}")

    n = matrix.shape[0]
    if n < 2:
        return np.array([], dtype=np.float64)

    indices = np.triu_indices(n, k=1)
    upper_triangle = matrix[indices]
    logger.debug("Extracted %d upper triangle values", upper_triangle.size)
    return upper_triangle.astype(np.float64, copy=False)


__all__ = [
    "mi_matrix",
    "adjacency_from_distances",
    "get_topology_adjacency",
    "correlation_upper_triangle",
]
