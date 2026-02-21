"""
Noise Topology Correlation (NTC) Metric

Measures whether EXCESS pairwise bit covariance (relative to a baseline with
independent noise) concentrates on topology-adjacent qubit pairs.

NTC = mean(excess_cov_adjacent) - mean(excess_cov_nonadjacent)

This is the "topology selectivity" of the correlated noise effect.
Positive NTC means noise correlations prefer topology-connected pairs.

The permutation test shuffles qubit labels on the adjacency matrix to
determine whether the observed selectivity is significant.
"""

from __future__ import annotations

from itertools import permutations as iter_permutations
from math import factorial
from typing import Any

import numpy as np
from numpy.typing import NDArray

from ..core.correlations import bit_covariance_matrix


def noise_topology_correlation(
    counts: dict[str, int],
    baseline_counts: dict[str, int],
    noise_adjacency: NDArray[np.float64],
    n_qubits: int,
    n_permutations: int = 1000,
    alpha: float = 0.05,
    rng: np.random.Generator | None = None,
) -> dict[str, Any]:
    """Compute Noise Topology Correlation (NTC) with permutation test.

    Args:
        counts: Measurement counts from the condition being tested
        baseline_counts: Measurement counts from the independent noise baseline
        noise_adjacency: Adjacency matrix of the noise topology being tested
        n_qubits: Number of qubits
        n_permutations: Permutation count for significance test
        alpha: Significance threshold
        rng: Random generator for reproducibility

    Returns:
        Dict with: ntc, p_value, significant, effect_size,
            edge_excess_mean, non_edge_excess_mean
    """
    if rng is None:
        rng = np.random.default_rng()

    W = np.asarray(noise_adjacency, dtype=np.float64)
    mask = np.triu(np.ones((n_qubits, n_qubits), dtype=bool), k=1)
    w_flat = W[mask]
    adj_idx = w_flat > 0.5

    # Need both adjacent and non-adjacent pairs for the metric
    if adj_idx.sum() == 0 or (~adj_idx).sum() == 0:
        return {
            "ntc": 0.0,
            "p_value": 1.0,
            "significant": False,
            "effect_size": 0.0,
            "edge_excess_mean": 0.0,
            "non_edge_excess_mean": 0.0,
        }

    # Compute covariance matrices
    cov_obs = bit_covariance_matrix(counts, n_qubits)
    cov_base = bit_covariance_matrix(baseline_counts, n_qubits)

    # Excess covariance
    excess = cov_obs - cov_base
    excess_flat = excess[mask]

    # Observed NTC: topology selectivity
    adj_mean = float(np.mean(excess_flat[adj_idx]))
    nonadj_mean = float(np.mean(excess_flat[~adj_idx]))
    observed = adj_mean - nonadj_mean

    # Permutation test: shuffle qubit labels on adjacency, recompute selectivity
    n_fact = factorial(n_qubits)
    exhaustive = n_fact <= n_permutations

    null_ntcs: list[float] = []

    if exhaustive:
        for perm in iter_permutations(range(n_qubits)):
            perm_arr = np.array(perm)
            W_perm = W[np.ix_(perm_arr, perm_arr)]
            w_perm_flat = W_perm[mask]
            adj_perm = w_perm_flat > 0.5
            if adj_perm.sum() == 0 or (~adj_perm).sum() == 0:
                null_ntcs.append(0.0)
            else:
                null_ntcs.append(
                    float(np.mean(excess_flat[adj_perm]) - np.mean(excess_flat[~adj_perm]))
                )
    else:
        for _ in range(n_permutations):
            perm_arr = rng.permutation(n_qubits)
            W_perm = W[np.ix_(perm_arr, perm_arr)]
            w_perm_flat = W_perm[mask]
            adj_perm = w_perm_flat > 0.5
            if adj_perm.sum() == 0 or (~adj_perm).sum() == 0:
                null_ntcs.append(0.0)
            else:
                null_ntcs.append(
                    float(np.mean(excess_flat[adj_perm]) - np.mean(excess_flat[~adj_perm]))
                )

    null_array = np.array(null_ntcs)
    p_value = float(np.mean(null_array >= observed))

    null_mean = float(np.mean(null_array))
    null_std = float(np.std(null_array))
    effect_size = (observed - null_mean) / null_std if null_std > 1e-12 else 0.0

    return {
        "ntc": float(observed),
        "p_value": p_value,
        "significant": p_value < alpha,
        "effect_size": effect_size,
        "edge_excess_mean": adj_mean,
        "non_edge_excess_mean": nonadj_mean,
    }


__all__ = ["noise_topology_correlation"]
