"""
Correlation Analysis Utilities

Mathematical utilities for computing correlation matrices and adjacency
matrices used in entanglement-error correlation analysis.

This module provides:
- Mutual information matrices for multi-qubit systems
- Adjacency matrix construction from distance matrices
- Correlation analysis helpers for topology studies
"""

import numpy as np
import logging
from typing import Mapping

from .information_theory import mutual_information
from ..constants import EEC_LAMBDA, ALPHA

logger = logging.getLogger(__name__)

def mi_matrix(counts: Mapping[str, int], *, alpha: float = ALPHA) -> np.ndarray:
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
    if not counts:
        raise ValueError("Empty counts dictionary")
    
    # Determine number of qubits from bitstring length
    n_qubits = len(next(iter(counts.keys())))
    
    if n_qubits < 2:
        raise ValueError(f"Need ≥2 qubits for MI matrix, got {n_qubits}")
    
    # Initialize symmetric matrix
    mi_mat = np.zeros((n_qubits, n_qubits))
    
    # Compute all pairwise MI values
    for i in range(n_qubits):
        for j in range(i + 1, n_qubits):  # Upper triangle only
            mi_value = mutual_information(counts, i, j, alpha=alpha)
            mi_mat[i, j] = mi_value
            mi_mat[j, i] = mi_value  # Symmetry
    
    logger.debug(f"Computed {n_qubits}×{n_qubits} MI matrix with {np.sum(mi_mat > 0.01)} significant pairs")
    
    return mi_mat

def adjacency_from_distances(distances: np.ndarray, 
                           lam: float = EEC_LAMBDA) -> np.ndarray:
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
        >>> print(f"Nearest neighbor: {adj[0,1]:.3f}")  # e^(-1) ≈ 0.368
        >>> print(f"Next nearest: {adj[0,2]:.3f}")      # e^(-2) ≈ 0.135
        
        >>> # 2D grid topology (for surface codes)
        >>> distances = np.array([[0, 1, √2], [1, 0, 1], [√2, 1, 0]])
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
    
    n = distances.shape[0]
    
    if n < 2:
        raise ValueError(f"Need ≥2 qubits for adjacency matrix, got {n}")
    
    if lam <= 0:
        raise ValueError(f"Decay parameter λ must be positive, got {lam}")
    
    # Check matrix properties
    if not np.allclose(distances, distances.T):
        logger.warning("Distance matrix is not symmetric")
    
    if not np.allclose(np.diag(distances), 0):
        logger.warning("Distance matrix diagonal is not zero")
    
    if np.any(distances < 0):
        raise ValueError("Distance matrix contains negative values")
    
    # Compute adjacency with exponential decay
    adjacency = np.exp(-lam * distances)
    
    # Zero out diagonal (no self-adjacency)
    np.fill_diagonal(adjacency, 0)
    
    logger.debug(f"Computed {n}×{n} adjacency matrix with λ={lam}, "
                f"mean coupling = {np.mean(adjacency[adjacency > 0]):.3f}")
    
    return adjacency

def get_topology_adjacency(topology_type: str, n_qubits: int) -> np.ndarray:
    """
    Get standard adjacency matrix for common quantum topologies.
    
    Args:
        topology_type: "linear", "ring", "grid", "all_to_all", or "star"
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
    
    adj = np.zeros((n_qubits, n_qubits))
    
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
        # 2D grid (square if possible)
        rows = int(np.sqrt(n_qubits))
        cols = n_qubits // rows
        if rows * cols != n_qubits:
            logger.warning(f"Cannot make perfect square grid with {n_qubits} qubits")
        
        for i in range(n_qubits):
            row, col = divmod(i, cols)
            # Right neighbor
            if col < cols - 1:
                j = i + 1
                adj[i, j] = adj[j, i] = 1.0
            # Down neighbor  
            if row < rows - 1:
                j = i + cols
                if j < n_qubits:
                    adj[i, j] = adj[j, i] = 1.0
                    
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
    
    logger.debug(f"Generated {topology_type} topology for {n_qubits} qubits, "
                f"{np.sum(adj)/2:.0f} edges")
    
    return adj

def correlation_upper_triangle(matrix: np.ndarray) -> np.ndarray:
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
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError(f"Matrix must be square, got shape {matrix.shape}")
    
    n = matrix.shape[0]
    if n < 2:
        return np.array([])
    
    # Extract upper triangle (above diagonal)
    indices = np.triu_indices(n, k=1)
    upper_triangle = matrix[indices]
    
    logger.debug(f"Extracted {len(upper_triangle)} upper triangle values")
    
    return upper_triangle