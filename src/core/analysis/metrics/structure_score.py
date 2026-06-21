"""Core Implementation of Structured Decoherence Pathway Metrics.

This module implements the 5 quantitative metrics for detecting structured
decoherence patterns in quantum measurement data.

Mathematical Definitions (project-standard):

    AI  (Asymmetry Index)
        TVD from uniform on the full support K = 2^n with Jeffreys prior:
        AI = 0.5 * Σ_i |p̃_i - 1/K|,  where  p̃_i = (c_i + α) / (N + αK)

    PCR (Pathway Concentration Ratio)
        PCR = (Σ frequencies in top 25%) / (Σ frequencies in bottom 25%)
        (uses adaptive quartiles for small numbers of outcomes)

    EEC (Entanglement–Error Correlation)
        EEC = corr( vec(W), vec(E) )
        where W is the entanglement/topology weight matrix for the chosen state
        and E is the error-correlation matrix (pairwise MI-based)

    TPS (Temporal Pathway Stability)
        Average pairwise Spearman rank correlation across runs/conditions,
        mapped to [0, 1] as (ρ̄ + 1)/2 for interpretability.

    CES (Complexity Emergence Score)
        Score derived from fitting emergence vs. qubit count (e.g., logistic),
        combining sharpness and amplitude to quantify a critical threshold.

Author: Structured Decoherence Research
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
from scipy.stats import spearmanr

# Delegate to rigorously implemented metric modules to avoid duplication and drift.
from .asymmetry_index import compute_asymmetry_index as _ai_compute
from .complexity_emergence_score import (
    compute_complexity_emergence_score as _ces_compute,
)
from .entanglement_error_correlation import (
    compute_entanglement_error_correlation as _eec_compute,
)
from .pathway_concentration_ratio import (
    compute_pathway_concentration_ratio as _pcr_compute,
)

logger = logging.getLogger(__name__)


def compute_structure_score(*, counts: dict[str, int], **kwargs: Any) -> dict[str, Any]:
    """Compute Structure Score (Asymmetry Index).

    This is a thin wrapper around the canonical implementation of Asymmetry Index.
    Confidence intervals and validation status are handled by higher-level
    pipelines (e.g., bootstrap module) and not in this core wrapper.

    Args:
        counts: Measurement counts {bitstring: count}
        **kwargs: Forwarded to the underlying implementation (if supported)

    Returns:
        dict: Minimal MetricResult-like payload:
              {
                "value": <float>,
                "status": "computed",
                "extras": {"method": "total_variation_distance"}
              }
              (CI and final status should be attached by the bootstrap pipeline.)

    Notes:
        - Keeps this "core" file lightweight and in sync with schema specs.
        - JSD (Jensen-Shannon Divergence) is an alternative metric that is more
          sensitive to tail deviations than TVD. While TVD is the primary
          "Structure Score" for its linear interpretability, JSD can be useful
          for sensitivity analysis in "Fog vs River" detection.
    """
    try:
        value = compute_asymmetry_index(counts)
        return {
            "value": float(value),
            "status": "computed",
            "extras": {"method": "total_variation_distance"},
        }
    except Exception as e:
        logger.error("Structure Score computation failed: %s", e)
        return {
            "value": 0.0,
            "status": "unstable",
            "extras": {"error": str(e)},
        }


def compute_asymmetry_index(counts: dict[str, int]) -> float:
    """Compute Asymmetry Index (AI) — deviation from a uniform error distribution.

    This function delegates to the project’s canonical `asymmetry_index` module,
    which implements the TVD-from-uniform definition on the full 2^n support
    with Jeffreys prior smoothing.

    Returns:
        float: Asymmetry Index in [0, 0.5]
    """
    return float(_ai_compute(counts))


def compute_pathway_concentration_ratio(counts: dict[str, int]) -> float:
    """Compute Pathway Concentration Ratio (PCR) — concentration in top error pathways.

    Delegates to the vetted `pathway_concentration` implementation, which uses
    adaptive quartiles for small n and handles edge cases robustly.

    Returns:
        float: PCR (≥ 1.0, or ∞ in extreme single-pathway cases)
    """
    return float(_pcr_compute(counts))


def compute_entanglement_error_correlation(
    counts: dict[str, int],
    state_type: str = "GHZ",
) -> float:
    """Compute Entanglement–Error Correlation (EEC) — correlation between topology and errors.

    Delegates to the canonical `eec` implementation, which builds the state-specific
    topology matrix W, computes the error-correlation matrix E from pairwise MI, and
    returns the Pearson correlation between vec(W) and vec(E).

    Args:
        counts: {bitstring: count}
        state_type: "GHZ", "W", "Bell", "Cluster", or "Custom"

    Returns:
        float: EEC in [-1, 1]
    """
    return float(_eec_compute(counts, state_type=state_type))


def compute_temporal_pathway_stability(pathway_rankings: list[list]) -> float:
    """Compute Temporal Pathway Stability (TPS) — ranking consistency across conditions.

    TPS is computed as the average pairwise Spearman rank correlation ρ across all
    provided rankings, mapped to [0, 1] via (ρ̄ + 1)/2 for interpretability.

    Args:
        pathway_rankings: A list of pathway orderings (each ordering is a list of IDs)

    Returns:
        float: TPS in [0, 1] (higher = more stable)

    Notes:
        - Only elements common to a pair of rankings contribute to that pair’s ρ.
        - If there are fewer than two rankings, returns 1.0 by convention.
        - If no pair has ≥2 elements in common, returns 0.0.
    """
    if not pathway_rankings or len(pathway_rankings) < 2:
        return 1.0

    def _to_rank_map(r: list) -> dict[Any, int]:
        return {k: i for i, k in enumerate(r)}

    maps = [_to_rank_map(r) for r in pathway_rankings]

    rhos: list[float] = []
    for i in range(len(maps)):
        for j in range(i + 1, len(maps)):
            common = sorted(set(maps[i]) & set(maps[j]))
            if len(common) < 2:
                continue
            a = [maps[i][k] for k in common]
            b = [maps[j][k] for k in common]
            rho, _ = spearmanr(a, b)
            if np.isnan(rho):
                continue
            rhos.append(float(rho))

    if not rhos:
        return 0.0

    # Map average Spearman ρ from [-1, 1] to [0, 1]
    tps = (float(np.mean(rhos)) + 1.0) / 2.0
    return float(np.clip(tps, 0.0, 1.0))


def compute_complexity_emergence_score(
    multi_qubit_data: dict[int, dict[str, int]],
) -> float:
    """Compute Complexity Emergence Score (CES) — threshold for structured emergence.

    Delegates to the canonical `complexity_emergence` implementation, which fits
    emergence curves (e.g., logistic) to structure vs. qubit-count data and
    combines sharpness and amplitude.

    Args:
        multi_qubit_data: {n_qubits: counts_dict}

    Returns:
        float: CES (higher = clearer, sharper emergence)
    """
    return float(_ces_compute(multi_qubit_data))


__all__ = [
    "compute_structure_score",
    "compute_asymmetry_index",
    "compute_pathway_concentration_ratio",
    "compute_entanglement_error_correlation",
    "compute_temporal_pathway_stability",
    "compute_complexity_emergence_score",
]
