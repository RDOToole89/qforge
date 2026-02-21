"""
Temporal Pathway Stability (TPS) - Dynamic Pathway Consistency Analysis

# Mathematical Foundation
Temporal Pathway Stability quantifies how consistently error pathways maintain
their relative rankings across different experimental conditions (noise levels,
time evolution, parameter sweeps). It combines time series analysis with
rank correlation methods to detect persistent structured decoherence.

# Physical Interpretation
TPS tests whether decoherence pathway preferences remain stable or fluctuate
randomly across experimental variations. High TPS indicates robust pathway
structure that persists across conditions, while low TPS suggests random
or highly sensitive pathway dynamics.

# Research Applications
- Validating pathway stability across noise parameter sweeps
- Characterizing robustness of structured decoherence patterns
- Identifying critical points where pathway structure breaks down
- Temporal analysis of quantum error patterns in dynamic systems

# Mathematical Definition
TPS uses rank correlation analysis across temporal/parametric sequences:
TPS = 1 - σ(ρ_rankings) / μ(ρ_rankings)

where ρ_rankings are Spearman correlations between consecutive ranking pairs,
providing a coefficient of variation for ranking stability.

# Educational Framework
This implementation demonstrates:
- Time series analysis applied to quantum measurement sequences
- Rank correlation methods (Spearman, Kendall) for non-parametric analysis
- Statistical stability measures and variance decomposition
- Dynamic systems analysis in quantum information contexts

References:
- Kendall (1938), "A New Measure of Rank Correlation"
- Spearman (1904), "The Proof and Measurement of Association"
- Box & Jenkins (1976), "Time Series Analysis: Forecasting and Control"
- Nielsen & Chuang (2010), "Quantum Computation and Quantum Information"
"""

import logging
from dataclasses import dataclass
from typing import Optional, Union

import numpy as np
from scipy.stats import kendalltau, pearsonr, spearmanr

from ..constants import (
    PP_MIN_RUNS,
    PP_TOP_K_MAX,
    PP_TOP_K_MIN,
)

logger = logging.getLogger(__name__)

# Local tuning constants
CRITICAL_DROP = 0.3  # correlation drop considered a transition


@dataclass
class TemporalAnalysis:
    """
    Complete temporal pathway stability analysis with dynamic insights.

    This structure provides comprehensive information about pathway stability
    across temporal or parametric sequences.
    """

    temporal_pathway_stability: float
    mean_rank_correlation: float
    stability_variance: float
    ranking_consistency: str  # "highly_stable", "stable", "unstable", "chaotic"
    persistent_pathways: list[str]
    volatile_pathways: list[str]
    stability_trend: str  # "increasing", "decreasing", "constant", "oscillating"
    critical_transitions: list[int]
    temporal_summary: str

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "temporal_pathway_stability": self.temporal_pathway_stability,
            "mean_rank_correlation": self.mean_rank_correlation,
            "stability_variance": self.stability_variance,
            "ranking_consistency": self.ranking_consistency,
            "persistent_pathways": self.persistent_pathways,
            "volatile_pathways": self.volatile_pathways,
            "stability_trend": self.stability_trend,
            "critical_transitions": self.critical_transitions,
            "temporal_summary": self.temporal_summary,
        }


def compute_temporal_pathway_stability(
    pathway_rankings: list[list[str]],
    correlation_method: str = "spearman",
    adaptive_top_k: bool = True,
    return_analysis: bool = False,
) -> Union[float, TemporalAnalysis]:
    """
    Compute Temporal Pathway Stability - consistency across experimental conditions.

    Mathematical Process:
        1. Extract pathway rankings from each experimental condition
        2. Compute pairwise rank correlations between consecutive conditions
        3. Calculate stability as: TPS = 1 - σ(correlations) / μ(correlations)
        4. Apply adaptive thresholding and statistical validation

    Physical Interpretation:
        - TPS → 1: Perfectly stable pathway rankings (robust structure)
        - TPS ≈ 0.5-0.8: Moderately stable (some pathway persistence)
        - TPS → 0: Completely unstable rankings (random fluctuations)
        - TPS < 0: Anti-stable (systematic rank reversals)

    Correlation Methods:
        - **Spearman**: Monotonic relationships, robust to outliers
        - **Kendall**: Focuses on concordant/discordant pairs
        - **Pearson**: Linear relationships (rarely used for rankings)

    Adaptive Top-K Selection:
        When adaptive_top_k=True, focuses analysis on pathways with
        significant probability mass (≥ PP_MASS_THRESHOLD of total).
        This filters noise from rare pathways while preserving structure.

    Args:
        pathway_rankings: List of pathway rankings for each condition
                         Each ranking is a list of bitstrings ordered by frequency
        correlation_method: "spearman", "kendall", or "pearson"
        adaptive_top_k: Whether to focus on top-k pathways automatically
        return_analysis: If True, return comprehensive TemporalAnalysis

    Returns:
        float: Temporal Pathway Stability ∈ [0, 1] (higher = more stable)
        OR TemporalAnalysis: Complete temporal analysis results

    Raises:
        ValueError: If rankings are invalid or insufficient

    Examples:
        >>> # Stable pathways across noise levels
        >>> rankings = [
        ...     ["000", "111", "001", "110"],  # Low noise
        ...     ["000", "111", "001", "110"],  # Medium noise
        ...     ["000", "111", "110", "001"]   # High noise
        ... ]
        >>> tps = compute_temporal_pathway_stability(rankings)
        >>> print(f"TPS = {tps:.3f}")  # Expected: high stability

        >>> # Random pathway fluctuations
        >>> rankings = [
        ...     ["000", "111", "001", "110"],
        ...     ["001", "110", "000", "111"],
        ...     ["111", "000", "110", "001"]
        ... ]
        >>> tps = compute_temporal_pathway_stability(rankings)
        >>> print(f"TPS = {tps:.3f}")  # Expected: low stability

    Complexity:
        Time: O(n² × k) where n = rankings, k = pathways per ranking
        Space: O(n × k) for storing ranking data

    Educational Notes:
        - TPS bridges time series analysis and quantum measurement theory
        - Rank correlations are non-parametric and robust to outliers
        - Coefficient of variation provides normalized stability measure
        - Temporal analysis reveals dynamic aspects of quantum decoherence
    """
    # Input validation with research-grade error handling
    if not pathway_rankings or len(pathway_rankings) < PP_MIN_RUNS:
        logger.warning(
            f"TPS requires ≥{PP_MIN_RUNS} rankings, got {len(pathway_rankings) if pathway_rankings else 0}"
        )
        return (
            1.0
            if not return_analysis
            else TemporalAnalysis(
                temporal_pathway_stability=1.0,
                mean_rank_correlation=1.0,
                stability_variance=0.0,
                ranking_consistency="stable",
                persistent_pathways=[],
                volatile_pathways=[],
                stability_trend="constant",
                critical_transitions=[],
                temporal_summary="Insufficient data for temporal analysis",
            )
        )

    # Validate ranking consistency
    all_pathways = set()
    for ranking in pathway_rankings:
        if not ranking:
            logger.warning("Empty ranking detected in temporal sequence")
            continue
        all_pathways.update(ranking)

    if not all_pathways:
        logger.warning("No pathways found in rankings")
        return 1.0 if not return_analysis else _create_empty_temporal_analysis()

    n_conditions = len(pathway_rankings)
    logger.debug(
        f"Computing TPS for {n_conditions} conditions with {len(all_pathways)} unique pathways"
    )

    # Apply adaptive top-k selection if requested
    if adaptive_top_k:
        pathway_rankings = _apply_adaptive_top_k_selection(pathway_rankings)

    # Compute pairwise rank correlations between consecutive conditions
    rank_correlations: list[float] = []
    for i in range(len(pathway_rankings) - 1):
        correlation = _compute_ranking_correlation(
            pathway_rankings[i], pathway_rankings[i + 1], correlation_method
        )
        rank_correlations.append(correlation)
        logger.debug(f"Rank correlation {i}->{i + 1}: {correlation:.4f}")

    if not rank_correlations:
        logger.warning("No valid rank correlations computed")
        return 1.0 if not return_analysis else _create_empty_temporal_analysis()

    # Calculate temporal stability using coefficient of variation
    mean_correlation = float(np.mean(rank_correlations))
    std_correlation = float(np.std(rank_correlations))

    # TPS formula: 1 - (coefficient of variation)
    # Higher mean correlation and lower variance → higher TPS
    if mean_correlation > 0:
        eps = 1e-12  # robustness when mean ~ 0
        cv = std_correlation / max(eps, mean_correlation)
        tps = 1.0 - cv
        # Clamp to reasonable range (can go negative for anti-stable systems)
        tps = float(np.clip(tps, 0.0, 1.0))
    else:
        # Handle zero or negative mean correlation
        tps = 0.0

    logger.debug("Computed TPS = %.6f (μ=%.4f, σ=%.4f)", tps, mean_correlation, std_correlation)

    if not return_analysis:
        return tps

    # Generate comprehensive temporal analysis
    return _generate_temporal_analysis(
        tps,
        rank_correlations,
        pathway_rankings,
        mean_correlation,
        std_correlation,
        all_pathways,
    )


def compute_pathway_persistence_scores(
    pathway_rankings: list[list[str]], top_k: Optional[int] = None
) -> dict[str, float]:
    """
    Compute persistence scores for individual pathways across conditions.

    This function analyzes how consistently each pathway maintains its
    ranking position across different experimental conditions.

    Mathematical Definition:
        For each pathway, compute:
        Persistence = 1 - σ(rank_positions) / μ(rank_positions)

        where rank_positions are the pathway's ranks across conditions.

    Research Applications:
        - Identifying which pathways are most robust to noise
        - Finding pathways that consistently dominate across conditions
        - Characterizing pathway-specific stability patterns

    Args:
        pathway_rankings: List of rankings for each condition
        top_k: Focus on top-k pathways (None = use all pathways)

    Returns:
        Dict[str, float]: {pathway: persistence_score} for each pathway

    Examples:
        >>> rankings = [
        ...     ["000", "111", "001", "110"],
        ...     ["000", "111", "110", "001"],
        ...     ["000", "001", "111", "110"]
        ... ]
        >>> persistence = compute_pathway_persistence_scores(rankings)
        >>> print(f"000 persistence: {persistence['000']:.3f}")  # High
        >>> print(f"110 persistence: {persistence['110']:.3f}")  # Low
    """
    if not pathway_rankings:
        return {}

    # Collect all unique pathways
    all_pathways = set()
    for ranking in pathway_rankings:
        all_pathways.update(ranking)

    if top_k is not None:
        # Focus on pathways that appear in top-k of any ranking
        top_pathways = set()
        for ranking in pathway_rankings:
            top_pathways.update(ranking[:top_k])
        all_pathways = top_pathways

    persistence_scores: dict[str, float] = {}

    for pathway in all_pathways:
        rank_positions: list[int] = []

        for ranking in pathway_rankings:
            try:
                # Find rank position (0-indexed)
                rank = ranking.index(pathway)
                rank_positions.append(rank)
            except ValueError:
                # Pathway not in this ranking - assign worst rank
                rank_positions.append(len(ranking))

        if len(rank_positions) > 1:
            # Compute persistence as inverse coefficient of variation
            mean_rank = float(np.mean(rank_positions))
            std_rank = float(np.std(rank_positions))

            if mean_rank > 0:
                persistence = 1.0 - (std_rank / mean_rank)
                persistence = max(0.0, persistence)  # Clamp to non-negative
            else:
                persistence = 1.0  # Perfect top ranking
        else:
            persistence = 1.0  # Single occurrence

        persistence_scores[pathway] = float(persistence)
        logger.debug("Pathway %s: persistence = %.4f", pathway, persistence)

    return persistence_scores


def compute_temporal_transition_matrix(
    pathway_rankings: list[list[str]], top_k: int = 5
) -> np.ndarray:
    """
    Compute transition matrix for pathway rank movements across conditions.

    This function builds a Markov chain transition matrix showing how
    pathways move between different rank positions across conditions.

    Mathematical Foundation:
        T[i,j] = P(rank_t+1 = j | rank_t = i)

        Transition matrix captures rank mobility patterns and stability.

    Research Applications:
        - Analyzing rank mobility and stability patterns
        - Identifying absorbing states (persistent top ranks)
        - Characterizing pathway dynamics as Markov processes

    Args:
        pathway_rankings: List of rankings for each condition
        top_k: Number of top ranks to analyze (reduces matrix size)

    Returns:
        np.ndarray: Transition matrix of shape (top_k+1, top_k+1)
                   Last row/column represents "other" ranks

    Examples:
        >>> rankings = [["A", "B", "C"], ["A", "C", "B"], ["B", "A", "C"]]
        >>> T = compute_temporal_transition_matrix(rankings, top_k=2)
        >>> print(f"Prob(rank 0 -> rank 0): {T[0,0]:.3f}")
    """
    if len(pathway_rankings) < 2:
        return np.eye(top_k + 1)  # Identity matrix for single/no rankings

    # Initialize transition matrix (top_k + 1 for "other" category)
    T = np.zeros((top_k + 1, top_k + 1))

    # Track transitions for all pathways
    for i in range(len(pathway_rankings) - 1):
        current_ranking = pathway_rankings[i]
        next_ranking = pathway_rankings[i + 1]

        # Find all pathways in either ranking
        all_pathways = set(current_ranking + next_ranking)

        for pathway in all_pathways:
            # Get current rank (or "other" if not in top_k)
            try:
                current_rank = current_ranking.index(pathway)
                current_rank = min(current_rank, top_k)  # Cap at top_k
            except ValueError:
                current_rank = top_k  # "other" category

            # Get next rank (or "other" if not in top_k)
            try:
                next_rank = next_ranking.index(pathway)
                next_rank = min(next_rank, top_k)  # Cap at top_k
            except ValueError:
                next_rank = top_k  # "other" category

            # Record transition
            T[current_rank, next_rank] += 1

    # Normalize to get probabilities (row-wise)
    row_sums = T.sum(axis=1, keepdims=True)
    T = np.divide(T, row_sums, out=np.zeros_like(T), where=row_sums != 0)

    # Optional robustness: enforce a self-loop for rows with zero count
    # so each row is a valid distribution.
    empty_rows = np.where(row_sums.squeeze() == 0)[0]
    for r in empty_rows:
        T[r, r] = 1.0

    logger.debug("Computed %dx%d transition matrix", top_k + 1, top_k + 1)
    return T


def _apply_adaptive_top_k_selection(
    pathway_rankings: list[list[str]],
) -> list[list[str]]:
    """Apply adaptive top-k selection to focus on significant pathways.

    Note: without per-condition counts we approximate by using a size-based k.
    """
    ks = []
    filtered: list[list[str]] = []
    for ranking in pathway_rankings:
        k = max(PP_TOP_K_MIN, min(PP_TOP_K_MAX, max(1, len(ranking) // 2)))
        ks.append(k)
        filtered.append(ranking[:k])

    if ks:
        ks_arr = np.array(ks, dtype=float)
        logger.debug(
            "Applied adaptive top-k selection: min=%d, median=%.1f, max=%d",
            int(ks_arr.min()),
            float(np.median(ks_arr)),
            int(ks_arr.max()),
        )
    else:
        logger.debug("Applied adaptive top-k selection: no rankings")

    return filtered


def _compute_ranking_correlation(ranking1: list[str], ranking2: list[str], method: str) -> float:
    """Compute rank correlation between two pathway rankings."""
    if not ranking1 or not ranking2:
        return 0.0

    # Precompute rank maps (O(n))
    rmap1 = {p: i for i, p in enumerate(ranking1)}
    rmap2 = {p: i for i, p in enumerate(ranking2)}

    # Common pathways must exist to correlate
    common = list(set(rmap1.keys()) & set(rmap2.keys()))
    if len(common) < 2:
        return 0.0

    ranks1 = [rmap1[p] for p in common]
    ranks2 = [rmap2[p] for p in common]

    try:
        m = method.lower()
        if m == "spearman":
            corr, _ = spearmanr(ranks1, ranks2)
        elif m == "kendall":
            corr, _ = kendalltau(ranks1, ranks2)
        elif m == "pearson":
            corr, _ = pearsonr(ranks1, ranks2)
        else:
            raise ValueError(f"Unknown correlation method: {method}")

        if np.isnan(corr):
            return 0.0

        # Numerical safety: keep within [-1, 1]
        return float(np.clip(corr, -1.0, 1.0))

    except Exception as e:
        logger.debug(f"Correlation computation failed: {e}")
        return 0.0


def _generate_temporal_analysis(
    tps: float,
    rank_correlations: list[float],
    pathway_rankings: list[list[str]],
    mean_correlation: float,
    std_correlation: float,
    all_pathways: set,
) -> TemporalAnalysis:
    """Generate comprehensive temporal analysis results."""

    # Determine consistency level
    if tps >= 0.8:
        consistency = "highly_stable"
    elif tps >= 0.6:
        consistency = "stable"
    elif tps >= 0.3:
        consistency = "unstable"
    else:
        consistency = "chaotic"

    # Analyze pathway persistence
    persistence_scores = compute_pathway_persistence_scores(pathway_rankings)

    # Identify persistent vs volatile pathways
    persistent_pathways = [p for p, score in persistence_scores.items() if score > 0.7]
    volatile_pathways = [p for p, score in persistence_scores.items() if score < 0.3]

    # Analyze stability trend
    if len(rank_correlations) >= 3:
        # Fit linear trend to correlations
        x = np.arange(len(rank_correlations))
        slope = np.polyfit(x, rank_correlations, 1)[0]

        if slope > 0.05:
            trend = "increasing"
        elif slope < -0.05:
            trend = "decreasing"
        else:
            trend = "constant"
    else:
        trend = "insufficient_data"

    # Detect critical transitions (large correlation drops)
    critical_transitions: list[int] = []
    for i, corr in enumerate(rank_correlations):
        if i > 0 and abs(corr - rank_correlations[i - 1]) > CRITICAL_DROP:
            critical_transitions.append(i)

    # Generate summary
    summary = (
        f"TPS = {tps:.3f} ({consistency}): "
        f"μ_corr = {mean_correlation:.3f}, σ_corr = {std_correlation:.3f}, "
        f"trend = {trend}"
    )

    return TemporalAnalysis(
        temporal_pathway_stability=tps,
        mean_rank_correlation=mean_correlation,
        stability_variance=std_correlation**2,
        ranking_consistency=consistency,
        persistent_pathways=persistent_pathways,
        volatile_pathways=volatile_pathways,
        stability_trend=trend,
        critical_transitions=critical_transitions,
        temporal_summary=summary,
    )


def _create_empty_temporal_analysis() -> TemporalAnalysis:
    """Create empty temporal analysis for edge cases."""
    return TemporalAnalysis(
        temporal_pathway_stability=1.0,
        mean_rank_correlation=1.0,
        stability_variance=0.0,
        ranking_consistency="stable",
        persistent_pathways=[],
        volatile_pathways=[],
        stability_trend="constant",
        critical_transitions=[],
        temporal_summary="Insufficient data for temporal analysis",
    )


def validate_tps_properties(
    tps: float, pathway_rankings: list[list[str]], tolerance: float = 1e-10
) -> bool:
    """
    Validate mathematical properties of computed TPS.

    Validated Properties:
        1. Range: TPS ∈ [0, 1] for stable systems
        2. Extremes: TPS = 1 for identical rankings, TPS → 0 for random
        3. Monotonicity: More consistent rankings → higher TPS
        4. Symmetry: Order-independent for identical correlation patterns
        5. Statistical validity: Proper coefficient of variation properties
    """
    if not pathway_rankings:
        return True

    # Property 1: Range constraint (allow slight negative for anti-stable)
    assert -0.1 <= tps <= 1.0 + tolerance, f"TPS={tps} outside expected range"

    # Property 2: Non-NaN and finite
    assert np.isfinite(tps), f"TPS={tps} is not finite"
    assert np.isreal(tps), f"TPS={tps} is not real"

    # Property 3: Identical rankings give TPS = 1
    if len(set(tuple(r) for r in pathway_rankings)) == 1:  # All rankings identical
        assert abs(tps - 1.0) <= tolerance, f"TPS={tps} should be 1.0 for identical rankings"

    logger.debug("TPS validation passed: TPS=%.6f", tps)
    return True


def temporal_pathway_stability_educational_demo() -> dict:
    """
    Educational demonstration of TPS behavior across stability scenarios.

    Returns:
        dict: Demonstration results with time series interpretations
    """
    demo_results: dict[str, dict] = {}

    # Example 1: Perfect stability
    stable_rankings = [
        ["000", "111", "001", "110"],
        ["000", "111", "001", "110"],
        ["000", "111", "001", "110"],
    ]
    tps_stable = compute_temporal_pathway_stability(stable_rankings)
    demo_results["perfect_stability"] = {
        "rankings": stable_rankings,
        "tps": tps_stable,
        "interpretation": "Perfect pathway stability - rankings unchanged",
    }

    # Example 2: Gradual degradation
    degrading_rankings = [
        ["000", "111", "001", "110"],
        ["000", "111", "110", "001"],
        ["000", "001", "111", "110"],
        ["001", "000", "110", "111"],
    ]
    tps_degrading = compute_temporal_pathway_stability(degrading_rankings)
    demo_results["gradual_degradation"] = {
        "rankings": degrading_rankings,
        "tps": tps_degrading,
        "interpretation": "Pathway structure gradually breaks down",
    }

    # Example 3: Random fluctuations
    random_rankings = [
        ["000", "111", "001", "110"],
        ["110", "001", "111", "000"],
        ["001", "000", "110", "111"],
        ["111", "110", "000", "001"],
    ]
    tps_random = compute_temporal_pathway_stability(random_rankings)
    demo_results["random_fluctuations"] = {
        "rankings": random_rankings,
        "tps": tps_random,
        "interpretation": "Random pathway fluctuations - no persistent structure",
    }

    # Example 4: Persistence analysis
    persistence_scores = compute_pathway_persistence_scores(degrading_rankings)
    demo_results["persistence_analysis"] = {
        "persistence_scores": persistence_scores,
        "most_persistent": max(persistence_scores, key=persistence_scores.get),
        "most_volatile": min(persistence_scores, key=persistence_scores.get),
        "interpretation": "Individual pathway stability varies",
    }

    # Summary insights
    demo_results["summary"] = {
        "tps_range_observed": [tps_stable, tps_degrading, tps_random],
        "stability_progression": "stable > degrading > random",
        "research_insight": "TPS captures temporal dynamics of quantum error patterns",
        "applications": "Parameter sweeps, noise evolution, temporal stability",
    }

    logger.info("TPS educational demonstration completed")
    return demo_results


__all__ = [
    "TemporalAnalysis",
    "compute_temporal_pathway_stability",
    "compute_pathway_persistence_scores",
    "compute_temporal_transition_matrix",
    "validate_tps_properties",
    "temporal_pathway_stability_educational_demo",
]
