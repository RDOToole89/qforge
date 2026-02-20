"""
Topology adjacency matrix builders.

Shared by noise models (correlated depolarizing) and analysis metrics (NTC).
Each builder returns an n x n symmetric binary adjacency matrix.
"""

import numpy as np
from numpy.typing import NDArray


def chain_adjacency(n: int) -> NDArray[np.float64]:
    """Linear chain: edges (0,1), (1,2), ..., (n-2, n-1)."""
    W = np.zeros((n, n), dtype=np.float64)
    for i in range(n - 1):
        W[i, i + 1] = W[i + 1, i] = 1.0
    return W


def star_adjacency(n: int) -> NDArray[np.float64]:
    """Star (hub-and-spoke): qubit 0 connected to all others."""
    W = np.zeros((n, n), dtype=np.float64)
    for i in range(1, n):
        W[0, i] = W[i, 0] = 1.0
    return W


def all_to_all_adjacency(n: int) -> NDArray[np.float64]:
    """Complete graph: every pair connected."""
    return (np.ones((n, n), dtype=np.float64) - np.eye(n, dtype=np.float64))


TOPOLOGY_BUILDERS: dict[str, type(chain_adjacency)] = {
    # Noise topology names
    "CHAIN": chain_adjacency,
    "STAR": star_adjacency,
    "ALL_TO_ALL": all_to_all_adjacency,
    # State-type aliases (match circuit connectivity)
    "GHZ": chain_adjacency,
    "CLUSTER": chain_adjacency,
    "W": all_to_all_adjacency,
}

__all__ = [
    "chain_adjacency",
    "star_adjacency",
    "all_to_all_adjacency",
    "TOPOLOGY_BUILDERS",
]
