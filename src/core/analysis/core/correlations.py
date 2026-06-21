"""Correlation Analysis Utilities.

Mathematical utilities for computing correlation matrices and adjacency
matrices used in entanglement-error correlation analysis.

This module provides:
- Mutual information matrices for multi-qubit systems
- Adjacency matrix construction from distance matrices
- Correlation analysis helpers for topology studies
"""

import logging
from collections.abc import Mapping, Sequence

import numpy as np
from numpy.typing import NDArray

from src.core.math import bit_for_qubit

from ..constants import ALPHA, EEC_LAMBDA, validate_counts_dict
from .information_theory import mutual_information, n_qubits_from_counts
from .topology import all_to_all_adjacency, chain_adjacency, star_adjacency

logger = logging.getLogger(__name__)


def mi_matrix(counts: Mapping[str, int], *, alpha: float = ALPHA) -> NDArray[np.float64]:
    """Compute mutual information matrix for all qubit pairs.

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
    """Compute adjacency matrix from distance matrix using exponential decay.

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
    """Get standard adjacency matrix for common quantum topologies.

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

    if topology_type == "linear":
        # Linear chain (== chain_adjacency): nearest neighbors only
        adj = chain_adjacency(n_qubits)

    elif topology_type == "ring":
        # Ring: linear chain + wraparound
        adj = chain_adjacency(n_qubits)
        adj[0, n_qubits - 1] = 1.0
        adj[n_qubits - 1, 0] = 1.0

    elif topology_type == "grid":
        adj = np.zeros((n_qubits, n_qubits), dtype=np.float64)

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
        # Complete graph (== all_to_all_adjacency)
        adj = all_to_all_adjacency(n_qubits)

    elif topology_type == "star":
        # Star graph (== star_adjacency): central node connected to all others
        adj = star_adjacency(n_qubits)

    else:
        raise ValueError(f"Unknown topology type: {topology_type}")

    logger.debug(
        f"Generated {topology_type} topology for {n_qubits} qubits, {np.sum(adj) / 2:.0f} edges"
    )

    return adj


def correlation_upper_triangle(matrix: np.ndarray) -> NDArray[np.float64]:
    """Extract upper triangle of correlation matrix as 1D array.

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


def bit_covariance_matrix(
    counts: Mapping[str, int],
    n_qubits: int,
) -> NDArray[np.float64]:
    """Compute pairwise bit covariance from measurement counts.

    Cov(b_i, b_j) = E[b_i * b_j] - E[b_i] * E[b_j]

    where b_i in {0, 1} is the measured bit value for qubit i.

    Args:
        counts: Measurement counts {bitstring: count}
        n_qubits: Number of qubits

    Returns:
        n x n covariance matrix with zero diagonal
    """
    total = sum(counts.values())
    if total == 0:
        return np.zeros((n_qubits, n_qubits), dtype=np.float64)

    b_mean = np.zeros(n_qubits, dtype=np.float64)
    bb_mean = np.zeros((n_qubits, n_qubits), dtype=np.float64)

    for bitstring, count in counts.items():
        b = np.array(
            [float(bit_for_qubit(bitstring, i)) for i in range(n_qubits)], dtype=np.float64
        )
        weight = count / total
        b_mean += weight * b
        bb_mean += weight * np.outer(b, b)

    cov = bb_mean - np.outer(b_mean, b_mean)
    np.fill_diagonal(cov, 0.0)
    return cov


def excess_covariance_matrix(
    counts: Mapping[str, int],
    baseline_counts: Mapping[str, int],
    n_qubits: int,
) -> NDArray[np.float64]:
    """Compute excess covariance: ΔCov = Cov(test) - Cov(baseline).

    Isolates the noise-induced covariance by subtracting the baseline
    (independent noise) covariance from the test (correlated noise) covariance.

    Args:
        counts: Test condition measurement counts
        baseline_counts: Baseline (independent noise) measurement counts
        n_qubits: Number of qubits

    Returns:
        n x n excess covariance matrix (symmetric, zero diagonal)
    """
    cov_test = bit_covariance_matrix(counts, n_qubits)
    cov_base = bit_covariance_matrix(baseline_counts, n_qubits)
    return cov_test - cov_base


def fingerprint_vector(
    counts: Mapping[str, int],
    baseline_counts: Mapping[str, int],
    n_qubits: int,
) -> NDArray[np.float64]:
    """Extract noise fingerprint as 1D vector from excess covariance.

    Computes the excess covariance matrix and extracts its upper triangle
    as a flat vector. For n qubits this gives n*(n-1)/2 elements
    (e.g. 15 for n=6).

    Args:
        counts: Test condition measurement counts
        baseline_counts: Baseline (independent noise) measurement counts
        n_qubits: Number of qubits

    Returns:
        1D fingerprint vector of length n*(n-1)/2
    """
    delta_cov = excess_covariance_matrix(counts, baseline_counts, n_qubits)
    return correlation_upper_triangle(delta_cov)


def cosine_similarity_matrix(
    vectors: Sequence[NDArray[np.float64]],
) -> NDArray[np.float64]:
    """Compute pairwise cosine similarity matrix.

    Args:
        vectors: Sequence of 1D vectors (all same length)

    Returns:
        k x k similarity matrix where k = len(vectors).
        sim[i,j] = dot(v_i, v_j) / (|v_i| * |v_j|).
        Zero vectors produce 0.0 similarity with everything.
    """
    mat = np.stack(vectors, axis=0)  # k x d
    norms = np.linalg.norm(mat, axis=1)  # k
    # Avoid division by zero: replace zero norms with 1 (result will be 0 anyway)
    safe_norms = np.where(norms > 0, norms, 1.0)
    normed = mat / safe_norms[:, np.newaxis]
    # Zero out rows that had zero norm
    zero_mask = norms == 0
    normed[zero_mask] = 0.0
    sim = normed @ normed.T
    # Clamp to [-1, 1] for numerical safety
    np.clip(sim, -1.0, 1.0, out=sim)
    return sim


__all__ = [
    "mi_matrix",
    "adjacency_from_distances",
    "get_topology_adjacency",
    "correlation_upper_triangle",
    "bit_covariance_matrix",
    "excess_covariance_matrix",
    "fingerprint_vector",
    "cosine_similarity_matrix",
]
