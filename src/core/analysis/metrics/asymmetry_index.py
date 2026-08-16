"""Asymmetry Index (AI) - Total variation distance from the uniform distribution.

# Mathematical Foundation
The Asymmetry Index quantifies deviation of a measurement outcome distribution
from the uniform distribution. It is a primary indicator of how non-uniform
(concentrated) the observed distribution is.

# Physical Interpretation
A uniform outcome distribution means all measurement outcomes are equally
likely. Non-uniform distributions concentrate probability on a subset of
outcomes; AI detects and quantifies this concentration.

# Applications
- Primary screening metric for non-uniformity in outcome distributions
- Foundation for complexity emergence scoring (CES)
- Statistical comparison against a uniform baseline

# Mathematical Definition
AI is based on Total Variation Distance (TVD) from the uniform distribution:
    AI = 0.5 * Σᵢ |p(xᵢ) - p_uniform|
where p(xᵢ) are observed probabilities and p_uniform = 1/K with K = 2^n.

# Important Range
Because TVD ≤ 1 and uniform reference is fixed, for discrete distributions
AI ∈ [0, 0.5]. This module returns AI in that range.

# Numerical Notes
- We use Jeffreys prior smoothing (α = 0.5) over the **full support** (K = 2^n):
  p̃(x) = (count(x) + α) / (N + α K), including unobserved outcomes.
- For AI we compute a closed-form TVD vs uniform that **does not enumerate**
  all K outcomes; it’s O(|observed|) instead of O(2^n).
- If you request the detailed educational analysis, we’ll compute additional
  summary quantities; for very large K we avoid full enumeration and use
  fast closed-form expressions where possible.

References:
- Cover & Thomas (2006), *Elements of Information Theory*
- Nielsen & Chuang (2010), *Quantum Computation and Quantum Information*
- MacKay (2003), *Information Theory, Inference and Learning Algorithms*
"""

import logging
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal, overload

import numpy as np

from src.core.math import total_variation_distance

from ..constants import (
    ALPHA,
    MAX_OUTCOMES_EXACT,
    STRUCTURE_MODERATE_THRESHOLD,
    STRUCTURE_STRONG_THRESHOLD,
    STRUCTURE_WEAK_THRESHOLD,
    validate_counts_dict,
)
from ..core.information_theory import (
    counts_to_probabilities,
    entropy,
    n_qubits_from_counts,
)
from ..core.null_models import factorized_null_model

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structure for rich/educational analysis results
# ---------------------------------------------------------------------------


@dataclass
class AsymmetryAnalysis:
    """Complete asymmetry analysis results with statistical interpretation.

    This structure provides the AI (TVD vs uniform), auxiliary stats,
    and a concise interpretation.
    """

    asymmetry_index: float
    total_variation_distance: float
    structure_evidence: str  # "weak", "moderate", "strong", "none"
    uniform_deviation: float
    entropy_reduction: float  # (H_max - H_obs)/H_max in bits
    dominant_outcomes: list[str]  # most-probable outcomes (educational)
    statistical_summary: str

    def to_dict(self) -> dict:
        """Convert to a JSON-serializable dictionary."""
        return {
            "asymmetry_index": self.asymmetry_index,
            "total_variation_distance": self.total_variation_distance,
            "structure_evidence": self.structure_evidence,
            "uniform_deviation": self.uniform_deviation,
            "entropy_reduction": self.entropy_reduction,
            "dominant_outcomes": self.dominant_outcomes,
            "statistical_summary": self.statistical_summary,
        }


# ---------------------------------------------------------------------------
# Fast closed-form helpers (no 2^n enumeration)
# ---------------------------------------------------------------------------


def _tvd_vs_uniform_from_counts_fast(
    counts: Mapping[str, int], alpha: float
) -> tuple[float, int, int]:
    """Compute TVD(p̃ || uniform) in O(|observed|) using the full-support Jeffreys prior.

    Let K = 2^n be the full outcome count (from bitstring length), N = total shots,
    and α the Jeffreys prior added to each of K outcomes.
      p̃_obs(x) = (c_x + α) / (N + α K)   for observed outcomes x in S
      p̃0       = α / (N + α K)          for each unobserved outcome
      u        = 1/K
    Then:
      TVD = 0.5 * [ Σ_{x∈S} |p̃_obs(x) - u| + (K - |S|) * |p̃0 - u| ].

    Returns:
        (tvd, K, S) where K is 2^n, S is the number of observed outcomes.
    """
    counts_clean = validate_counts_dict(counts)
    if not counts_clean:
        return 0.0, 0, 0

    n_qubits = len(next(iter(counts_clean.keys())))

    K = 1 << n_qubits

    N = sum(counts_clean.values())

    denom = N + alpha * K
    u = 1.0 / K

    # Sum abs deviation over observed outcomes
    s_obs = 0.0
    for c in counts_clean.values():
        s_obs += abs((c + alpha) / denom - u)

    # Unobserved outcomes share the same deviation
    M = len(counts_clean)
    delta0 = abs((alpha / denom) - u)

    tvd = 0.5 * (s_obs + (K - M) * delta0)
    return float(tvd), K, M


def _entropy_full_support_fast(counts: Mapping[str, int], alpha: float) -> float:
    """Compute H(p̃) in bits on the full 2^n support without enumerating all outcomes.

    p̃_obs(x) = (c_x + α) / (N + α K) for x in observed set S
    p̃0       = α / (N + α K)         for (K - S) unobserved outcomes
    H(p̃) = - Σ_{x∈S} p̃_obs(x) log2 p̃_obs(x)  -  (K-S) * p̃0 * log2 p̃0
    """
    counts_clean = validate_counts_dict(counts)
    n_qubits = n_qubits_from_counts(counts_clean)
    K = 1 << n_qubits

    N = int(sum(counts_clean.values()))
    if N <= 0:
        return 0.0

    denom = float(N + alpha * K)
    log2 = np.log(2.0)

    # Observed part
    h_obs_nats = 0.0
    for c in counts_clean.values():
        p = (float(c) + alpha) / denom
        h_obs_nats += -p * np.log(p)

    # Unobserved block (K - S copies of p0)
    S = len(counts_clean)
    p0 = alpha / denom
    h_unobs_nats = -(K - S) * p0 * np.log(p0)

    return float((h_obs_nats + h_unobs_nats) / log2)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


@overload
def compute_asymmetry_index(
    counts: Mapping[str, int],
    alpha: float = ...,
    return_analysis: Literal[False] = ...,
) -> float: ...


@overload
def compute_asymmetry_index(
    counts: Mapping[str, int],
    alpha: float = ...,
    *,
    return_analysis: Literal[True],
) -> AsymmetryAnalysis: ...


def compute_asymmetry_index(
    counts: Mapping[str, int],
    alpha: float = ALPHA,
    return_analysis: bool = False,
) -> float | AsymmetryAnalysis:
    """Compute Asymmetry Index — deviation from the uniform error distribution.

    Mathematical Definition:
        AI = 0.5 * Σᵢ |p(xᵢ) - 1/K|
    where p(xᵢ) are smoothed probabilities over the full support K = 2^n with
    Jeffreys prior (α), i.e. p̃(xᵢ) = (cᵢ + α) / (N + αK), including unobserved outcomes.

    Returns:
        float: Asymmetry Index ∈ [0, 1). The maximum for a deterministic
            distribution is 1 - 1/K, reduced slightly by the smoothing prior.
        OR AsymmetryAnalysis: Complete educational analysis (if return_analysis=True)

    Interpretation:
        - AI = 0: Uniform distribution
        - Larger AI: probability concentrated in fewer outcomes
        - AI → 1 - 1/K: (near-)deterministic distribution

    Interpretation Thresholds (from constants):
        - AI ≥ STRUCTURE_WEAK_THRESHOLD: weak concentration
        - AI ≥ STRUCTURE_MODERATE_THRESHOLD: moderate concentration
        - AI ≥ STRUCTURE_STRONG_THRESHOLD: strong concentration

    Numerical Features:
        - Uses a closed-form TVD vs uniform without enumerating all 2^n outcomes
        - Detailed analysis is computed exactly; for very large K, we avoid enumeration

    Examples:
        >>> # Uniform distribution (random decoherence)
        >>> counts = {"00": 250, "01": 250, "10": 250, "11": 250}
        >>> compute_asymmetry_index(counts)
        0.0

        >>> # Highly structured (GHZ-like)
        >>> counts = {"000": 400, "111": 400, "001": 100, "110": 100}
        >>> compute_asymmetry_index(counts)
        0.547808764940239
    """
    counts_clean = validate_counts_dict(counts, "asymmetry index input")

    if not counts_clean:
        logger.warning("Empty counts dictionary for asymmetry index")
        if not return_analysis:
            return 0.0
        return AsymmetryAnalysis(
            asymmetry_index=0.0,
            total_variation_distance=0.0,
            structure_evidence="none",
            uniform_deviation=0.0,
            entropy_reduction=0.0,
            dominant_outcomes=[],
            statistical_summary="No data available for analysis",
        )

    # Fast, exact AI without enumerating 2^n outcomes
    tvd, K, S = _tvd_vs_uniform_from_counts_fast(counts_clean, alpha)
    ai = tvd  # identical

    if not return_analysis:
        return ai

    # Build educational analysis. For large K, avoid enumerating all outcomes.
    N = int(sum(counts_clean.values()))
    H_max = np.log2(K) if K > 0 else 0.0

    # Decide whether to fully enumerate the 2^n support for detailed values
    if K <= MAX_OUTCOMES_EXACT:
        # Full-support path (educational, exact)
        prob_dict = counts_to_probabilities(counts_clean, alpha)  # includes unobserved
        probs = np.array(list(prob_dict.values()), dtype=np.float64)
        uniform = np.full_like(probs, 1.0 / K, dtype=np.float64)

        # Uniform deviation (L∞)
        uniform_deviation = float(np.max(np.abs(probs - uniform)))

        # Entropy reduction
        H_obs = entropy(probs)
        entropy_reduction = ((H_max - H_obs) / H_max) if H_max > 0 else 0.0

        # Dominant outcomes: top 25% by probability (at least 1)
        sorted_outcomes = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)
        n_dom = max(1, len(sorted_outcomes) // 4)
        dominant_outcomes = [o for (o, _) in sorted_outcomes[:n_dom]]

        details_note = f"Full support enumerated (K={K})."
    else:
        # Large-K path (no enumeration)
        # Compute exact uniform deviation via observed/unobserved split
        denom = float(N + alpha * K)
        u = 1.0 / K
        obs_devs = [abs(((float(c) + alpha) / denom) - u) for c in counts_clean.values()]
        p0 = alpha / denom
        unobs_dev = abs(p0 - u)
        uniform_deviation = float(max(max(obs_devs) if obs_devs else 0.0, unobs_dev))

        # Exact entropy via closed-form
        H_obs = _entropy_full_support_fast(counts_clean, alpha)
        entropy_reduction = ((H_max - H_obs) / H_max) if H_max > 0 else 0.0

        # Dominant outcomes among observed only (avoid listing unobserved)
        sorted_obs = sorted(counts_clean.items(), key=lambda x: x[1], reverse=True)
        n_dom = max(1, len(sorted_obs) // 4)
        dominant_outcomes = [o for (o, _) in sorted_obs[:n_dom]]

        details_note = (
            f"Large support (K={K}) — used closed-form analysis without full enumeration."
        )

    # Evidence label via thresholds from constants
    if ai >= STRUCTURE_STRONG_THRESHOLD:
        structure_evidence = "strong"
    elif ai >= STRUCTURE_MODERATE_THRESHOLD:
        structure_evidence = "moderate"
    elif ai >= STRUCTURE_WEAK_THRESHOLD:
        structure_evidence = "weak"
    else:
        structure_evidence = "none"

    summary = (
        f"AI={ai:.3f} ({structure_evidence} structure) with {S} observed outcomes, "
        f"N={N} shots, K={K} total outcomes. Entropy reduction: {entropy_reduction:.1%}. "
        + details_note
    )

    return AsymmetryAnalysis(
        asymmetry_index=ai,
        total_variation_distance=ai,
        structure_evidence=structure_evidence,
        uniform_deviation=uniform_deviation,
        entropy_reduction=entropy_reduction,
        dominant_outcomes=dominant_outcomes,
        statistical_summary=summary,
    )


def compute_asymmetry_index_with_null_comparison(
    counts: Mapping[str, int],
    alpha: float = ALPHA,
) -> tuple[float, float, str]:
    """Compute AI with explicit comparison to the factorized null model.

    Process:
      1) AI vs uniform (standard, fast closed-form)
      2) AI vs factorized null Q (requires Q over full support)
      3) Interpretation by comparing both values

    Returns:
        (AI_uniform, AI_factorized, interpretation)
        interpretation ∈ {"structured", "marginal_bias_only",
                          "unstructured", "intermediate_structure"}
    """
    counts_clean = validate_counts_dict(counts)

    # Standard AI (vs uniform) — fast/closed form
    ai_uniform, K, _ = _tvd_vs_uniform_from_counts_fast(counts_clean, alpha)

    if K > MAX_OUTCOMES_EXACT:
        return (
            ai_uniform,
            float("nan"),
            (
                "unstructured"
                if ai_uniform < STRUCTURE_WEAK_THRESHOLD
                else (
                    "structured"
                    if ai_uniform >= STRUCTURE_MODERATE_THRESHOLD
                    else "intermediate_structure"
                )
            ),
        )

    # AI vs factorized null model
    # Note: this enumerates K outcomes via factorized_null_model.
    null_model = factorized_null_model(counts_clean, alpha)
    observed_probs = counts_to_probabilities(counts_clean, alpha)

    # Align arrays by canonical order
    outcomes = sorted(observed_probs.keys())
    obs_array = np.array([observed_probs[o] for o in outcomes], dtype=np.float64)
    null_array = np.array([null_model.get(o, 0.0) for o in outcomes], dtype=np.float64)
    null_array = null_array / null_array.sum()  # defensive renormalization
    ai_factorized = total_variation_distance(obs_array, null_array)

    # Interpretation based on comparison
    if ai_uniform >= STRUCTURE_MODERATE_THRESHOLD and ai_factorized >= STRUCTURE_WEAK_THRESHOLD:
        interpretation = "structured"
    elif ai_uniform >= STRUCTURE_WEAK_THRESHOLD and ai_factorized < STRUCTURE_WEAK_THRESHOLD:
        interpretation = "marginal_bias_only"
    elif ai_uniform < STRUCTURE_WEAK_THRESHOLD:
        interpretation = "unstructured"
    else:
        interpretation = "intermediate_structure"

    logger.info(
        "AI comparison: uniform=%.3f, factorized=%.3f, interpretation=%s (K=%d)",
        ai_uniform,
        ai_factorized,
        interpretation,
        K,
    )
    return ai_uniform, ai_factorized, interpretation


def validate_asymmetry_index_properties(
    ai: float,
    counts: Mapping[str, int],
    tolerance: float = 1e-10,
) -> bool:
    """Validate key mathematical properties of the computed Asymmetry Index.

    Validated Properties:
      1) Range: AI ∈ [0, 1)
      2) Non-negativity
      3) Uniform case: AI ≈ 0 when the full support is observed with equal counts
      4) Single-outcome case: AI matches the closed form (N+α)/(N+αK) − 1/K
      5) Finite/real

    Returns:
        True if all checks pass (raises AssertionError otherwise).
    """
    counts_clean = validate_counts_dict(counts)

    # 1) Range and 2) Non-negativity
    assert -tolerance <= ai < 1.0, f"AI={ai} outside [0, 1)"
    assert ai >= -tolerance, f"AI={ai} is negative"

    # 3) Uniform (observed) case — crude but reasonable check
    if len(counts_clean) > 1 and len(set(counts_clean.values())) == 1:
        assert ai <= tolerance, f"AI={ai} should be ~0 for uniform observed counts"

    # 4) Single observed outcome: TVD equals the positive deviation of that outcome
    if len(counts_clean) == 1:
        n_qubits = len(next(iter(counts_clean.keys())))
        big_k = 1 << n_qubits
        n_shots = sum(counts_clean.values())
        expected = (n_shots + ALPHA) / (n_shots + ALPHA * big_k) - 1.0 / big_k
        assert abs(ai - expected) <= tolerance, (
            f"AI={ai} should be {expected} for a single observed outcome"
        )

    # 5) Finite and real
    assert np.isfinite(ai), f"AI={ai} not finite"
    assert np.isreal(ai), f"AI={ai} not real"

    logger.debug("Asymmetry Index validation passed: AI=%.6f", ai)
    return True


def asymmetry_index_educational_demo() -> dict:
    """Educational demonstration of Asymmetry Index behavior.

    Provides concrete examples illustrating how AI responds to different
    measurement distributions.

    Returns:
        dict of named examples with counts, AI, and interpretations.
    """
    demo_results: dict[str, dict] = {}

    # Example 1: Perfect uniform (random decoherence)
    uniform_counts = {"00": 250, "01": 250, "10": 250, "11": 250}
    ai_uniform = compute_asymmetry_index(uniform_counts)
    demo_results["uniform_distribution"] = {
        "counts": uniform_counts,
        "asymmetry_index": ai_uniform,
        "interpretation": "Random decoherence — no preferred pathways",
    }

    # Example 2: GHZ-like structure
    ghz_counts = {"000": 400, "111": 400, "001": 100, "110": 100}
    ai_ghz = compute_asymmetry_index(ghz_counts)
    demo_results["ghz_structure"] = {
        "counts": ghz_counts,
        "asymmetry_index": ai_ghz,
        "interpretation": "Concentrated distribution — GHZ-like correlations preserved",
    }

    # Example 3: Single dominant pathway (valid bitstrings only)
    dominant_counts = {"0000": 800, "0001": 50, "0010": 50, "0011": 100}
    ai_dominant = compute_asymmetry_index(dominant_counts)
    demo_results["dominant_pathway"] = {
        "counts": dominant_counts,
        "asymmetry_index": ai_dominant,
        "interpretation": "Highly structured — single dominant error pathway",
    }

    # Example 4: Bimodal distribution
    bimodal_counts = {"000": 300, "111": 300, "010": 200, "101": 200}
    ai_bimodal = compute_asymmetry_index(bimodal_counts)
    demo_results["bimodal_structure"] = {
        "counts": bimodal_counts,
        "asymmetry_index": ai_bimodal,
        "interpretation": "Moderate structure — bimodal pathway preferences",
    }

    demo_results["summary"] = {
        "ai_range_observed": [ai_uniform, ai_ghz, ai_dominant, ai_bimodal],
        "structure_progression": "uniform < bimodal < ghz < dominant",
        "insight": "AI increases as the outcome distribution becomes more concentrated",
    }

    logger.info("AI educational demo complete.")
    return demo_results


__all__ = [
    "AsymmetryAnalysis",
    "compute_asymmetry_index",
    "compute_asymmetry_index_with_null_comparison",
    "validate_asymmetry_index_properties",
    "asymmetry_index_educational_demo",
]
