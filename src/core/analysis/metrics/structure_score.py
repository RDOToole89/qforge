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

from ..core.information_theory import (
    all_bitstrings,
    counts_to_probabilities,
    jensen_shannon_divergence,
    n_qubits_from_counts,
)
from ..core.null_models import factorized_null_model

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

# Canonical TPS lives in temporal_pathway_stability; re-export to keep one impl.
from .temporal_pathway_stability import compute_temporal_pathway_stability

logger = logging.getLogger(__name__)


def compute_structure_score(*, counts: dict[str, int], **kwargs: Any) -> dict[str, Any]:
    """Compute Structure Score (JSD from factorized null model).

    The Structure Score quantifies how much the observed distribution deviates
    from its factorized (independent-marginals) null model. A perfectly
    independent (separable) distribution yields ~0; any inter-qubit structure
    (correlations) raises the score.

    Mathematical Definition:
        SS = JSD(P_observed || Q_factorized)

    where P_observed is the full-support smoothed distribution and
    Q_factorized = ∏ᵢ q(xᵢ) is the product of per-qubit marginals. The JSD is
    computed in bits and bounded to [0, 1].

    Args:
        counts: Measurement counts {bitstring: count}
        **kwargs: Forwarded for API compatibility (unused).

    Returns:
        dict: Minimal MetricResult-like payload:
              {
                "value": <float>,
                "status": "computed",
                "extras": {"method": "jsd_factorized_null"}
              }
              (CI and final status should be attached by the bootstrap pipeline.)

    Notes:
        - Observed and null probability vectors are aligned over the same
          canonical lexicographic ordering of all 2^n bitstrings.
        - Distinct from the Asymmetry Index (TVD vs uniform); both measure
          different aspects of structure.
    """
    try:
        n = n_qubits_from_counts(counts)
        order = all_bitstrings(n)

        observed_probs = counts_to_probabilities(counts)
        null_probs = factorized_null_model(counts)

        p = np.asarray([observed_probs[bs] for bs in order], dtype=np.float64)
        q = np.asarray([null_probs[bs] for bs in order], dtype=np.float64)

        value = jensen_shannon_divergence(p, q)
        return {
            "value": float(value),
            "status": "computed",
            "extras": {"method": "jsd_factorized_null"},
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
