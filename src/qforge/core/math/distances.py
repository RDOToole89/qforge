"""Distance / concentration measures shared across analysis metrics."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray


def total_variation_distance(
    p: Sequence[float] | NDArray[np.float64],
    q: Sequence[float] | NDArray[np.float64],
) -> float:
    """Total variation distance between two probability vectors.

    TVD(p, q) = 1/2 * sum_i |p_i - q_i|.

    The two vectors must be over the same, aligned outcome ordering and the same
    length. For probability distributions TVD lies in [0, 1].

    Args:
        p: First probability vector.
        q: Second probability vector (same length / ordering as ``p``).

    Returns:
        The total variation distance.

    Raises:
        ValueError: If the vectors have different lengths.
    """
    pa = np.asarray(p, dtype=np.float64)
    qa = np.asarray(q, dtype=np.float64)
    if pa.shape != qa.shape:
        raise ValueError(f"Vectors must have the same shape, got {pa.shape} and {qa.shape}")
    return 0.5 * float(np.sum(np.abs(pa - qa)))


def gini_coefficient(values: Sequence[float] | NDArray[np.float64]) -> float:
    """Gini coefficient of a set of non-negative values (concentration measure).

    Uses the standard sorted formulation::

        G = (2 * sum_{i=1..n} i * x_(i)) / (n * sum(x)) - (n + 1) / n

    where x_(i) are the values sorted ascending and i is 1-indexed. Returns 0.0
    for a perfectly uniform set and approaches 1.0 as mass concentrates in one
    outcome. Returns 0.0 if the total is zero or there is a single value.

    Args:
        values: Non-negative values (e.g. measurement counts or probabilities).

    Returns:
        The Gini coefficient in [0, 1).
    """
    arr = np.sort(np.asarray(values, dtype=np.float64))
    n = arr.size
    total = float(arr.sum())
    if n <= 1 or total <= 0.0:
        return 0.0
    index = np.arange(1, n + 1, dtype=np.float64)
    return float((2.0 * np.sum(index * arr)) / (n * total) - (n + 1) / n)
