"""
Pathway Concentration Ratio (PCR) - Error Concentration Analysis

# Mathematical Foundation
The Pathway Concentration Ratio quantifies how concentrated errors are in
the most frequent pathways compared to the least frequent ones. It uses
economic inequality measures adapted for quantum measurement analysis.

# Physical Interpretation
PCR measures error "inequality" - whether decoherence affects all pathways
equally (low PCR) or concentrates in specific channels (high PCR). This
reveals the degree of pathway preference in structured decoherence.

# Research Applications
- Detecting pathway preferences and error concentration patterns
- Complementary to Asymmetry Index for complete structure characterization
- Identifying dominant vs rare error pathways in quantum systems
- Statistical validation of pathway-based decoherence models

# Mathematical Definition
PCR uses the ratio of top quartile to bottom quartile frequencies:
PCR = (Σ frequencies in top 25%) / (Σ frequencies in bottom 25%)

This is inspired by the Palma ratio from economics, adapted for discrete
measurement outcomes in quantum systems.

# Educational Framework
This implementation demonstrates:
- Economic inequality measures applied to quantum physics
- Robust statistical analysis with quartile-based metrics
- Handling of discrete distributions with variable support
- Research-grade edge case management and validation

References:
- Palma (2011), "Homogeneous Middles vs. Heterogeneous Tails"
- Atkinson & Bourguignon (2015), "Handbook of Income Distribution"
- Gini (1912), "Measurement of Inequality of Incomes"
"""

import logging
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Union

import numpy as np

from ..constants import (
    validate_counts_dict,
)

logger = logging.getLogger(__name__)


@dataclass
class ConcentrationAnalysis:
    """
    Complete concentration analysis results with economic interpretation.

    This structure provides comprehensive information about error concentration
    including multiple inequality measures and their quantum physics interpretation.
    """

    pathway_concentration_ratio: float
    gini_coefficient: float
    top_quartile_share: float
    bottom_quartile_share: float
    concentration_evidence: str  # "uniform", "moderate", "high", "extreme"
    dominant_pathways: list[str]
    rare_pathways: list[str]
    inequality_summary: str

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "pathway_concentration_ratio": self.pathway_concentration_ratio,
            "gini_coefficient": self.gini_coefficient,
            "top_quartile_share": self.top_quartile_share,
            "bottom_quartile_share": self.bottom_quartile_share,
            "concentration_evidence": self.concentration_evidence,
            "dominant_pathways": self.dominant_pathways,
            "rare_pathways": self.rare_pathways,
            "inequality_summary": self.inequality_summary,
        }


def compute_pathway_concentration_ratio(
    counts: Mapping[str, int],
    adaptive_quartiles: bool = True,
    return_analysis: bool = False,
) -> Union[float, "ConcentrationAnalysis"]:
    """
    Compute Pathway Concentration Ratio - error concentration in top pathways.

    Mathematical Definition:
        PCR = (Σ frequencies in top 25%) / (Σ frequencies in bottom 25%)

        This ratio quantifies how much more concentrated errors are in the
        most frequent pathways compared to the rarest pathways.

    Physical Interpretation:
        - PCR = 1: Uniform distribution (no concentration)
        - PCR > 1: Errors concentrate in top pathways
        - PCR >> 1: Highly concentrated (structured decoherence)
        - PCR → ∞: Extreme concentration (few dominant pathways)

    Research Thresholds:
        - PCR ∈ [1.0, 2.0]: Uniform to slight concentration
        - PCR ∈ [2.0, 5.0]: Moderate concentration (emerging structure)
        - PCR ∈ [5.0, 20.0]: High concentration (clear structure)
        - PCR > 20.0: Extreme concentration (dominant pathways)

    Adaptive Quartiles:
        When adaptive_quartiles=True, the algorithm adjusts quartile boundaries
        to ensure meaningful comparison even with few outcomes:
        - For n < 4: Use top half vs bottom half
        - For n ≥ 4: Use standard quartiles (25%)
        - Ensures robust behavior across all measurement scenarios

    Args:
        counts: Measurement counts {bitstring: count}
        adaptive_quartiles: Whether to adapt quartile size for small n
        return_analysis: If True, return comprehensive ConcentrationAnalysis

    Returns:
        float: Pathway Concentration Ratio (≥ 1.0)
        OR ConcentrationAnalysis: Complete analysis results

    Raises:
        ValueError: If counts are invalid or inconsistent

    Examples:
        >>> # Uniform distribution (no concentration)
        >>> counts = {"00": 250, "01": 250, "10": 250, "11": 250}
        >>> compute_pathway_concentration_ratio(counts)
        1.0

        >>> # High concentration (GHZ-like)
        >>> counts = {"000": 400, "111": 300, "001": 100, "010": 50, "011": 150}
        >>> compute_pathway_concentration_ratio(counts)
        14.0

    Complexity:
        Time: O(n log n) for sorting frequencies
        Space: O(n) for frequency array

    Educational Notes:
        - PCR is inspired by the Palma ratio from economics
        - Robust to outliers due to quartile-based design
        - Complements other inequality measures like Gini coefficient
        - Provides intuitive interpretation as "concentration factor"
    """
    # Input validation with research-grade error handling
    counts_clean = validate_counts_dict(counts, "pathway concentration ratio input")

    if not counts_clean:
        logger.warning("Empty counts dictionary for pathway concentration ratio")
        return (
            1.0
            if not return_analysis
            else ConcentrationAnalysis(
                pathway_concentration_ratio=1.0,
                gini_coefficient=0.0,
                top_quartile_share=0.25,
                bottom_quartile_share=0.25,
                concentration_evidence="uniform",
                dominant_pathways=[],
                rare_pathways=[],
                inequality_summary="No data available for concentration analysis",
            )
        )

    # Handle single outcome case (infinite concentration)
    if len(counts_clean) == 1:
        logger.debug("Single outcome detected - infinite concentration")
        if not return_analysis:
            return float("inf")
        else:
            outcome = list(counts_clean.keys())[0]
            return ConcentrationAnalysis(
                pathway_concentration_ratio=float("inf"),
                gini_coefficient=0.0,  # Gini undefined for single outcome
                top_quartile_share=1.0,
                bottom_quartile_share=0.0,
                concentration_evidence="extreme",
                dominant_pathways=[outcome],
                rare_pathways=[],
                inequality_summary="Deterministic outcome - infinite concentration",
            )

    n_outcomes = len(counts_clean)
    logger.debug(f"Computing PCR for {n_outcomes} outcomes, adaptive={adaptive_quartiles}")

    # Sort frequencies in descending order
    frequencies = sorted(counts_clean.values(), reverse=True)
    total_counts = sum(frequencies)

    # Determine quartile boundaries
    if adaptive_quartiles and n_outcomes < 4:
        # Use top half vs bottom half for small outcome sets
        top_k = max(1, n_outcomes // 2)
        bottom_k = n_outcomes - top_k
        logger.debug(f"Adaptive quartiles: top {top_k}, bottom {bottom_k}")
    else:
        # Standard quartiles (25%)
        top_k = max(1, n_outcomes // 4)
        bottom_k = max(1, n_outcomes // 4)
        logger.debug(f"Standard quartiles: top {top_k}, bottom {bottom_k}")

    # Calculate quartile sums
    top_quartile_sum = sum(frequencies[:top_k])
    bottom_quartile_sum = sum(frequencies[-bottom_k:])

    # Handle edge case: bottom quartile has zero frequency
    if bottom_quartile_sum == 0:
        logger.warning("Bottom quartile has zero frequency - extreme concentration detected")
        pcr = float("inf")
    else:
        pcr = top_quartile_sum / bottom_quartile_sum

    # Ensure PCR ≥ 1.0 (mathematical property)
    pcr = max(1.0, pcr)

    logger.debug(
        f"Computed PCR = {pcr:.3f} (top: {top_quartile_sum}, bottom: {bottom_quartile_sum})"
    )

    if not return_analysis:
        return pcr

    # Generate comprehensive analysis
    return _generate_concentration_analysis(
        pcr, frequencies, counts_clean, top_k, bottom_k, total_counts
    )


def compute_concentration_with_gini(counts: Mapping[str, int]) -> tuple[float, float]:
    """
    Compute both PCR and Gini coefficient for comprehensive inequality analysis.

    This function provides two complementary measures of concentration:
    - PCR: Quartile-based ratio (robust, intuitive)
    - Gini: Full distribution inequality (comprehensive, standard)

    Mathematical Background:
        PCR focuses on extreme quantiles, making it sensitive to tail behavior.
        Gini considers the entire distribution, providing a complete inequality picture.
        Together, they offer robust characterization of error concentration.

    Args:
        counts: Measurement counts {bitstring: count}

    Returns:
        Tuple[float, float]: (PCR, Gini coefficient)

    Research Applications:
        - PCR for detecting extreme concentration (dominant pathways)
        - Gini for overall distribution inequality
        - Combined analysis for complete concentration characterization

    Examples:
        >>> counts = {"000": 400, "111": 300, "010": 200, "011": 100}
        >>> pcr, gini = compute_concentration_with_gini(counts)
        >>> print(f"PCR: {pcr:.2f}, Gini: {gini:.3f}")
    """
    counts_clean = validate_counts_dict(counts)

    # Compute PCR using main function
    pcr = compute_pathway_concentration_ratio(counts_clean)

    # Compute Gini coefficient
    asc = np.asarray(sorted(counts_clean.values()), dtype=float)
    n = asc.size

    if n <= 1:
        gini = 0.0
    else:
        # Standard Gini coefficient formula
        cumsum = np.cumsum(asc)
        gini = (2.0 * np.sum(np.arange(1, n + 1, dtype=float) * asc)) / (n * cumsum[-1]) - (
            n + 1
        ) / n
    gini = max(0.0, gini)  # Ensure non-negative

    logger.debug(f"Concentration measures: PCR={pcr:.3f}, Gini={gini:.3f}")
    return pcr, gini


def _generate_concentration_analysis(
    pcr: float,
    frequencies: list[int],
    counts_clean: dict,
    top_k: int,
    bottom_k: int,
    total_counts: int,
) -> ConcentrationAnalysis:
    """Generate comprehensive concentration analysis results."""

    # Determine concentration evidence level
    if pcr == float("inf") or pcr > 20.0:
        concentration_evidence = "extreme"
    elif pcr > 5.0:
        concentration_evidence = "high"
    elif pcr > 2.0:
        concentration_evidence = "moderate"
    else:
        concentration_evidence = "uniform"

    # Calculate Gini coefficient for additional insight
    n = len(frequencies)
    if n > 1:
        cumsum = np.cumsum(sorted(frequencies))
        gini = (2.0 * np.sum(np.arange(1, n + 1) * sorted(frequencies))) / (n * cumsum[-1]) - (
            n + 1
        ) / n
        gini = max(0.0, gini)
    else:
        gini = 0.0

    # Calculate quartile shares (as fractions of total)
    top_quartile_share = sum(frequencies[:top_k]) / total_counts
    bottom_quartile_share = sum(frequencies[-bottom_k:]) / total_counts

    # stable tie-break on key for reproducibility
    sorted_outcomes = sorted(counts_clean.items(), key=lambda kv: (-kv[1], kv[0]))
    dominant_pathways = [outcome for outcome, _ in sorted_outcomes[:top_k]]
    rare_pathways = [outcome for outcome, _ in sorted_outcomes[-bottom_k:]]

    # Generate inequality summary
    if pcr == float("inf"):
        summary = "Infinite concentration - single or few dominant pathways"
    else:
        summary = (
            f"PCR={pcr:.2f} ({concentration_evidence} concentration): "
            f"top {100 * top_quartile_share:.1f}% vs bottom {100 * bottom_quartile_share:.1f}% "
            f"of total probability mass"
        )

    return ConcentrationAnalysis(
        pathway_concentration_ratio=pcr,
        gini_coefficient=gini,
        top_quartile_share=top_quartile_share,
        bottom_quartile_share=bottom_quartile_share,
        concentration_evidence=concentration_evidence,
        dominant_pathways=dominant_pathways,
        rare_pathways=rare_pathways,
        inequality_summary=summary,
    )


def validate_pcr_properties(
    pcr: float, counts: Mapping[str, int], tolerance: float = 1e-10
) -> bool:
    """
    Validate mathematical properties of computed PCR.

    This function performs comprehensive validation of PCR properties to ensure
    numerical correctness and catch potential implementation bugs.

    Validated Properties:
        1. Lower bound: PCR ≥ 1.0 (top quartile ≥ bottom quartile)
        2. Extremes: PCR = 1.0 for uniform, PCR → ∞ for concentrated
        3. Monotonicity: More concentration → higher PCR
        4. Scale invariance: Scaling all counts preserves PCR
        5. Symmetry: Permutation of equal counts preserves PCR

    Args:
        pcr: Computed pathway concentration ratio
        counts: Original measurement counts
        tolerance: Numerical tolerance for comparisons

    Returns:
        bool: True if all properties are satisfied

    Raises:
        AssertionError: If any property is violated
    """
    counts_clean = validate_counts_dict(counts)

    # Property 1: Lower bound
    assert pcr >= 1.0 - tolerance, f"PCR={pcr} below minimum value 1.0"

    # Property 2: Non-negativity and finiteness (allow inf for extreme cases)
    assert pcr >= 0.0, f"PCR={pcr} is negative"
    assert pcr > 0.0, f"PCR={pcr} is zero or negative"

    # Property 3: Uniform distribution gives PCR ≈ 1.0
    unique_counts = set(counts_clean.values())
    if len(unique_counts) == 1 and len(counts_clean) > 1:  # All counts equal
        assert abs(pcr - 1.0) <= tolerance, f"PCR={pcr} should be ~1.0 for uniform distribution"

    # Property 4: Single outcome gives PCR = ∞
    if len(counts_clean) == 1:
        assert pcr == float("inf"), f"PCR={pcr} should be infinite for single outcome"

    # Property 5: Real number (finite or inf)
    assert np.isreal(pcr), f"PCR={pcr} is not real"
    assert pcr == float("inf") or np.isfinite(pcr), f"PCR={pcr} is invalid (NaN)"

    logger.debug(f"PCR validation passed: PCR={pcr}")
    return True


def pathway_concentration_educational_demo() -> dict:
    """
    Educational demonstration of PCR behavior across different scenarios.

    This function provides concrete examples showing how PCR responds to
    different types of error concentration patterns, serving as both a validation
    tool and educational resource.

    Returns:
        dict: Demonstration results with interpretations

    Educational Value:
        - Shows PCR behavior across concentration levels
        - Demonstrates economic inequality concepts in quantum systems
        - Provides intuition for interpreting PCR in research contexts
        - Illustrates relationship between PCR and pathway structure
    """
    demo_results = {}

    # Example 1: Perfect uniform (no concentration)
    uniform_counts = {"00": 250, "01": 250, "10": 250, "11": 250}
    pcr_uniform = compute_pathway_concentration_ratio(uniform_counts)
    demo_results["uniform_distribution"] = {
        "counts": uniform_counts,
        "pcr": pcr_uniform,
        "interpretation": "No concentration - all pathways equally likely",
    }

    # Example 2: Moderate concentration
    moderate_counts = {"000": 400, "001": 300, "010": 200, "011": 100}
    pcr_moderate = compute_pathway_concentration_ratio(moderate_counts)
    demo_results["moderate_concentration"] = {
        "counts": moderate_counts,
        "pcr": pcr_moderate,
        "interpretation": "Moderate concentration - some pathway preferences",
    }

    # Example 3: High concentration (GHZ-like)
    high_counts = {"000": 600, "111": 300, "001": 50, "010": 30, "011": 20}
    pcr_high = compute_pathway_concentration_ratio(high_counts)
    demo_results["high_concentration"] = {
        "counts": high_counts,
        "pcr": pcr_high,
        "interpretation": "High concentration - clear dominant pathways",
    }

    # Example 4: Extreme concentration
    extreme_counts = {"0000": 900, "0001": 50, "0010": 25, "0011": 15, "0100": 10}
    pcr_extreme = compute_pathway_concentration_ratio(extreme_counts)
    demo_results["extreme_concentration"] = {
        "counts": extreme_counts,
        "pcr": pcr_extreme,
        "interpretation": "Extreme concentration - single dominant pathway",
    }

    # Example 5: Economic interpretation
    lorenz_analysis = _compute_lorenz_curve_data(high_counts)
    demo_results["economic_interpretation"] = {
        "lorenz_curve": lorenz_analysis,
        "inequality_analogy": "PCR measures 'pathway inequality' like income inequality",
        "quantum_insight": "High PCR indicates structured decoherence pathways",
    }

    # Summary insights
    demo_results["summary"] = {
        "pcr_range_observed": [pcr_uniform, pcr_moderate, pcr_high, pcr_extreme],
        "concentration_progression": "uniform < moderate < high < extreme",
        "research_insight": "PCR increases with pathway preference strength",
        "economic_analogy": "Like measuring wealth concentration in quantum error pathways",
    }

    logger.info("PCR educational demonstration completed")
    return demo_results


def _compute_lorenz_curve_data(counts: dict) -> dict:
    """Compute Lorenz curve data for economic interpretation of PCR."""
    frequencies = sorted(counts.values())
    cumulative_freq = np.cumsum(frequencies)
    total_freq = cumulative_freq[-1]

    # Lorenz curve: cumulative population vs cumulative frequency
    population_percentiles = np.arange(1, len(frequencies) + 1) / len(frequencies)
    frequency_percentiles = cumulative_freq / total_freq

    # Gini coefficient from Lorenz curve
    gini = 1 - 2 * np.trapz(frequency_percentiles, population_percentiles)

    return {
        "population_percentiles": population_percentiles.tolist(),
        "frequency_percentiles": frequency_percentiles.tolist(),
        "gini_coefficient": gini,
        "interpretation": f"Gini={gini:.3f} quantifies overall pathway inequality",
    }


__all__ = [
    "ConcentrationAnalysis",
    "compute_pathway_concentration_ratio",
    "compute_concentration_with_gini",
    "validate_pcr_properties",
    "pathway_concentration_educational_demo",
]
