# src/analysis/decoherence.py

"""
Decoherence analysis for quantum states.

This module provides functions to analyze decoherence in quantum states,
including Fubini-Study distance calculations and other decoherence metrics.
"""

import numpy as np
import logging
from scipy.linalg import sqrtm

logger = logging.getLogger("QuantumExperiment.Analysis.Decoherence")


def compute_fubini_study_distance(rho1: np.ndarray, rho2: np.ndarray) -> float:
    """
    Computes the Fubini-Study distance between two density matrices.

    The Fubini-Study distance is a metric on the space of quantum states
    that measures the "distance" between two density matrices. It's particularly
    useful for analyzing decoherence, as it quantifies how much a quantum state
    has changed over time.

    Args:
        rho1 (np.ndarray): First density matrix.
        rho2 (np.ndarray): Second density matrix.

    Returns:
        float: Fubini-Study distance in radians.

    Notes:
        The Fubini-Study distance is computed as:
        d(ρ₁, ρ₂) = arccos(Tr(√(√ρ₁ ρ₂ √ρ₁)))

        This metric is:
        - Symmetric: d(ρ₁, ρ₂) = d(ρ₂, ρ₁)
        - Bounded: 0 ≤ d(ρ₁, ρ₂) ≤ π/2
        - Zero only when ρ₁ = ρ₂
    """
    try:
        # Compute the square root of rho1 using scipy.linalg.sqrtm
        sqrt_rho1 = sqrtm(rho1)
        # Compute inner = sqrt(rho1) @ rho2 @ sqrt(rho1)
        inner = sqrt_rho1 @ rho2 @ sqrt_rho1
        # Compute sqrt(inner) using sqrtm
        sqrt_inner = sqrtm(inner)
        fidelity = np.trace(sqrt_inner).real
        # Ensure fidelity is within [0, 1] to avoid numerical errors
        fidelity = min(max(fidelity, 0.0), 1.0)
        distance = np.arccos(fidelity)
        return distance
    except Exception as e:
        logger.error(f"Error computing Fubini-Study distance: {str(e)}")
        return 0.0  # Fallback value


def compute_fubini_study_distances_over_time(
    density_matrices: list, time_steps: list = None
) -> list:
    """
    Computes Fubini-Study distances between consecutive density matrices.

    Args:
        density_matrices (list): List of density matrices over time.
        time_steps (list, optional): List of time steps corresponding to the matrices.

    Returns:
        list: List of Fubini-Study distances between consecutive matrices.
    """
    distances = []
    for i in range(len(density_matrices) - 1):
        rho1 = np.array(density_matrices[i]["density"])
        rho2 = np.array(density_matrices[i + 1]["density"])
        distance = compute_fubini_study_distance(rho1, rho2)
        distances.append(distance)
    return distances


def analyze_decoherence_rate(distances: list, time_steps: list) -> dict:
    """
    Analyzes the rate of decoherence based on Fubini-Study distances.

    Args:
        distances (list): List of Fubini-Study distances.
        time_steps (list): List of time steps.

    Returns:
        dict: Analysis results including average rate and trends.
    """
    if len(distances) < 2:
        return {"average_rate": 0.0, "trend": "insufficient_data"}

    # Compute average decoherence rate
    time_diffs = np.diff(time_steps[1:])  # Time differences between consecutive steps
    rates = np.array(distances) / time_diffs
    average_rate = np.mean(rates)

    # Analyze trend
    if len(rates) > 1:
        slope = np.polyfit(time_steps[1:-1], rates, 1)[0]
        if slope > 0.01:
            trend = "accelerating"
        elif slope < -0.01:
            trend = "decelerating"
        else:
            trend = "constant"
    else:
        trend = "insufficient_data"

    return {
        "average_rate": average_rate,
        "trend": trend,
        "max_distance": max(distances),
        "total_distance": sum(distances),
    }
