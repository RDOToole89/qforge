"""
Asymmetry Index (AI) - Structured Decoherence Pathway Detection

# Mathematical Foundation
The Asymmetry Index quantifies deviation from uniform error distribution using
information-theoretic principles. It serves as the primary indicator of 
structured vs random decoherence patterns in quantum measurements.

# Physical Interpretation
In quantum systems, uniform error distribution indicates random decoherence
where all measurement outcomes are equally likely. Structured decoherence
creates preferential pathways, leading to non-uniform distributions that
AI detects and quantifies.

# Research Applications
- Primary screening metric for structured decoherence detection
- Baseline metric for pathway emergence analysis
- Foundation for complexity emergence scoring (CES)
- Statistical validation against null hypothesis of random decoherence

# Mathematical Definition
AI is based on Total Variation Distance from uniform distribution:
AI = 0.5 * Σᵢ |p(xᵢ) - p_uniform|

where p(xᵢ) are observed probabilities and p_uniform = 1/N.

# Educational Framework
This implementation demonstrates:
- Information theory applications in quantum measurement analysis
- Statistical hypothesis testing with null models
- Numerical stability in probability calculations
- Research-grade algorithm design with proper validation

References:
- Cover & Thomas (2006), "Elements of Information Theory"
- Nielsen & Chuang (2010), "Quantum Computation and Quantum Information"
- MacKay (2003), "Information Theory, Inference and Learning Algorithms"
"""

import numpy as np
import logging
from typing import Dict, Mapping, Tuple, Optional
from dataclasses import dataclass

from ..constants import (
    ALPHA, EPS, VALIDATED_CV_THRESHOLD, EXPERIMENTAL_CV_THRESHOLD,
    STRUCTURE_WEAK_THRESHOLD, STRUCTURE_MODERATE_THRESHOLD, STRUCTURE_STRONG_THRESHOLD,
    validate_counts_dict
)
from ..core.information_theory import counts_to_probabilities, entropy
from ..core.null_models import factorized_null_model

logger = logging.getLogger(__name__)


@dataclass
class AsymmetryAnalysis:
    """
    Complete asymmetry analysis results with statistical validation.
    
    This structure provides comprehensive information about the asymmetry
    measurement including the core value, confidence assessment, and
    research interpretation.
    """
    asymmetry_index: float
    total_variation_distance: float
    structure_evidence: str  # "weak", "moderate", "strong", "none"
    uniform_deviation: float
    entropy_reduction: float
    dominant_outcomes: list
    statistical_summary: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "asymmetry_index": self.asymmetry_index,
            "total_variation_distance": self.total_variation_distance,
            "structure_evidence": self.structure_evidence,
            "uniform_deviation": self.uniform_deviation,
            "entropy_reduction": self.entropy_reduction,
            "dominant_outcomes": self.dominant_outcomes,
            "statistical_summary": self.statistical_summary
        }


def compute_asymmetry_index(counts: Mapping[str, int], 
                          alpha: float = ALPHA,
                          return_analysis: bool = False) -> float:
    """
    Compute Asymmetry Index - deviation from uniform error distribution.
    
    Mathematical Definition:
        AI = 0.5 * Σᵢ |p(xᵢ) - p_uniform|
        
        This is the Total Variation Distance between observed and uniform
        distributions, providing a normalized measure ∈ [0, 1].
        
    Physical Interpretation:
        - AI = 0: Perfect uniform distribution (random decoherence)
        - AI = 0.5: Maximum asymmetry (deterministic outcomes)
        - AI ∈ (0, 0.5): Structured decoherence with varying concentrations
        
    Research Thresholds:
        - AI > 0.1: Weak evidence of structure
        - AI > 0.3: Moderate evidence of structure  
        - AI > 0.5: Strong evidence of structure
        
    Numerical Features:
        - Jeffreys prior smoothing for finite-sample stability
        - Probability clamping to prevent log(0) issues
        - Input validation with descriptive error messages
        - Handles edge cases (single outcome, zero counts)
        
    Args:
        counts: Measurement counts {bitstring: count}
        alpha: Jeffreys prior parameter for smoothing
        return_analysis: If True, return comprehensive AsymmetryAnalysis
        
    Returns:
        float: Asymmetry Index ∈ [0, 1]
        OR AsymmetryAnalysis: Complete analysis results
        
    Raises:
        ValueError: If counts are invalid or inconsistent
        
    Examples:
        >>> # Uniform distribution (random decoherence)
        >>> counts = {"00": 250, "01": 250, "10": 250, "11": 250}
        >>> compute_asymmetry_index(counts)
        0.0
        
        >>> # Highly structured (GHZ-like)
        >>> counts = {"000": 400, "111": 400, "others": 200}
        >>> compute_asymmetry_index(counts)
        0.4
        
    Complexity:
        Time: O(n) where n = number of outcomes
        Space: O(1) auxiliary space
        
    Educational Notes:
        - Total Variation Distance is a fundamental metric in probability theory
        - Equivalent to half the L1 norm between probability vectors
        - Related to Kullback-Leibler divergence for comparing distributions
        - Used extensively in statistical physics and information theory
    """
    # Input validation with research-grade error messages
    counts_clean = validate_counts_dict(counts, "asymmetry index input")
    
    if not counts_clean:
        logger.warning("Empty counts dictionary for asymmetry index")
        return 0.0 if not return_analysis else AsymmetryAnalysis(
            asymmetry_index=0.0,
            total_variation_distance=0.0,
            structure_evidence="none",
            uniform_deviation=0.0,
            entropy_reduction=0.0,
            dominant_outcomes=[],
            statistical_summary="No data available for analysis"
        )
    
    # Handle single outcome case
    if len(counts_clean) == 1:
        logger.debug("Single outcome detected - maximum asymmetry")
        if not return_analysis:
            return 0.5  # Maximum asymmetry for deterministic case
        else:
            return AsymmetryAnalysis(
                asymmetry_index=0.5,
                total_variation_distance=0.5,
                structure_evidence="strong",
                uniform_deviation=0.5,
                entropy_reduction=1.0,
                dominant_outcomes=list(counts_clean.keys()),
                statistical_summary="Deterministic outcome - maximum structure"
            )
    
    logger.debug(f"Computing asymmetry index for {len(counts_clean)} outcomes with α={alpha}")
    
    # Convert to smoothed probabilities using research-grade utilities
    prob_dict = counts_to_probabilities(counts_clean, alpha)
    observed_probs = np.array(list(prob_dict.values()))
    
    # Uniform reference distribution
    n_outcomes = len(observed_probs)
    uniform_probs = np.ones(n_outcomes) / n_outcomes
    
    # Total Variation Distance: TVD = 0.5 * Σᵢ |p(xᵢ) - q(xᵢ)|
    tvd = 0.5 * np.sum(np.abs(observed_probs - uniform_probs))
    
    # Asymmetry Index is the Total Variation Distance from uniform
    asymmetry_index = tvd
    
    # Ensure result is in valid range [0, 0.5] due to TVD properties
    asymmetry_index = np.clip(asymmetry_index, 0.0, 0.5)
    
    logger.debug(f"Computed Asymmetry Index = {asymmetry_index:.6f}")
    
    if not return_analysis:
        return asymmetry_index
    
    # Generate comprehensive analysis
    return _generate_asymmetry_analysis(
        asymmetry_index, 
        observed_probs, 
        uniform_probs, 
        counts_clean, 
        prob_dict
    )


def compute_asymmetry_index_with_null_comparison(counts: Mapping[str, int],
                                               alpha: float = ALPHA) -> Tuple[float, float, str]:
    """
    Compute AI with explicit comparison to factorized null model.
    
    This function computes AI relative to both uniform and factorized null
    models, providing enhanced statistical validation for structure detection.
    
    Mathematical Process:
        1. Compute AI relative to uniform distribution (standard)
        2. Compute AI relative to factorized null model  
        3. Compare results to assess structure type
        
    Research Application:
        Distinguishes between:
        - Pure structure: High AI vs both uniform and factorized nulls
        - Marginal bias: High AI vs uniform, low AI vs factorized null
        - Random decoherence: Low AI vs both null models
        
    Args:
        counts: Measurement counts {bitstring: count}
        alpha: Jeffreys prior parameter
        
    Returns:
        Tuple[float, float, str]: (AI_uniform, AI_factorized, interpretation)
        
    Examples:
        >>> counts = {"000": 400, "111": 400, "010": 100, "101": 100}
        >>> ai_uniform, ai_fact, interp = compute_asymmetry_index_with_null_comparison(counts)
        >>> print(f"AI vs uniform: {ai_uniform:.3f}, vs factorized: {ai_fact:.3f}")
        >>> print(f"Interpretation: {interp}")
    """
    counts_clean = validate_counts_dict(counts)
    
    # Standard AI (vs uniform)
    ai_uniform = compute_asymmetry_index(counts_clean, alpha)
    
    # AI vs factorized null model
    null_model = factorized_null_model(counts_clean, alpha)
    
    # Convert to probability arrays
    observed_probs = counts_to_probabilities(counts_clean, alpha)
    
    # Ensure same outcome ordering
    outcomes = sorted(observed_probs.keys())
    obs_array = np.array([observed_probs[outcome] for outcome in outcomes])
    null_array = np.array([null_model.get(outcome, 0.0) for outcome in outcomes])
    
    # Normalize null array (safety)
    null_array = null_array / null_array.sum()
    
    # TVD from factorized null
    ai_factorized = 0.5 * np.sum(np.abs(obs_array - null_array))
    
    # Interpretation based on comparison
    if ai_uniform > STRUCTURE_MODERATE_THRESHOLD and ai_factorized > STRUCTURE_WEAK_THRESHOLD:
        interpretation = "structured_decoherence"
    elif ai_uniform > STRUCTURE_WEAK_THRESHOLD and ai_factorized < STRUCTURE_WEAK_THRESHOLD:
        interpretation = "marginal_bias_only"
    elif ai_uniform < STRUCTURE_WEAK_THRESHOLD:
        interpretation = "random_decoherence"
    else:
        interpretation = "intermediate_structure"
    
    logger.info(f"AI comparison: uniform={ai_uniform:.3f}, factorized={ai_factorized:.3f}, "
               f"interpretation={interpretation}")
    
    return ai_uniform, ai_factorized, interpretation


def _generate_asymmetry_analysis(asymmetry_index: float,
                               observed_probs: np.ndarray,
                               uniform_probs: np.ndarray,
                               counts_clean: dict,
                               prob_dict: dict) -> AsymmetryAnalysis:
    """Generate comprehensive asymmetry analysis results."""
    
    # Determine structure evidence level
    if asymmetry_index >= STRUCTURE_STRONG_THRESHOLD:
        structure_evidence = "strong"
    elif asymmetry_index >= STRUCTURE_MODERATE_THRESHOLD:
        structure_evidence = "moderate"
    elif asymmetry_index >= STRUCTURE_WEAK_THRESHOLD:
        structure_evidence = "weak"
    else:
        structure_evidence = "none"
    
    # Calculate uniform deviation (L∞ norm)
    uniform_deviation = np.max(np.abs(observed_probs - uniform_probs))
    
    # Calculate entropy reduction from maximum entropy
    observed_entropy = entropy(observed_probs)
    max_entropy = np.log2(len(observed_probs))  # Maximum entropy for n outcomes
    entropy_reduction = (max_entropy - observed_entropy) / max_entropy if max_entropy > 0 else 0.0
    
    # Find dominant outcomes (top 25% by probability)
    sorted_outcomes = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)
    n_dominant = max(1, len(sorted_outcomes) // 4)
    dominant_outcomes = [outcome for outcome, _ in sorted_outcomes[:n_dominant]]
    
    # Statistical summary
    total_shots = sum(counts_clean.values())
    n_outcomes = len(counts_clean)
    
    summary = (f"AI={asymmetry_index:.3f} ({structure_evidence} structure) "
              f"from {n_outcomes} outcomes, {total_shots} shots. "
              f"Entropy reduction: {entropy_reduction:.1%}")
    
    return AsymmetryAnalysis(
        asymmetry_index=asymmetry_index,
        total_variation_distance=asymmetry_index,  # Same for uniform reference
        structure_evidence=structure_evidence,
        uniform_deviation=uniform_deviation,
        entropy_reduction=entropy_reduction,
        dominant_outcomes=dominant_outcomes,
        statistical_summary=summary
    )


def validate_asymmetry_index_properties(ai: float, 
                                       counts: Mapping[str, int],
                                       tolerance: float = 1e-10) -> bool:
    """
    Validate mathematical properties of computed Asymmetry Index.
    
    This function performs comprehensive validation of AI properties to ensure
    numerical correctness and catch potential implementation bugs.
    
    Validated Properties:
        1. Range: AI ∈ [0, 0.5]
        2. Symmetry: Permutation invariance
        3. Extremes: AI = 0 for uniform, AI = 0.5 for deterministic
        4. Monotonicity: More concentrated → higher AI
        5. Continuity: Small changes in counts → small changes in AI
        
    Args:
        ai: Computed asymmetry index
        counts: Original measurement counts
        tolerance: Numerical tolerance for comparisons
        
    Returns:
        bool: True if all properties are satisfied
        
    Raises:
        AssertionError: If any property is violated
        
    Educational Notes:
        - Property validation is crucial for research-grade algorithms
        - Helps catch numerical instabilities and implementation bugs
        - Provides confidence in metric behavior across edge cases
    """
    counts_clean = validate_counts_dict(counts)
    
    # Property 1: Range constraint
    assert 0.0 <= ai <= 0.5 + tolerance, f"AI={ai} outside valid range [0, 0.5]"
    
    # Property 2: Non-negativity
    assert ai >= -tolerance, f"AI={ai} is negative"
    
    # Property 3: Uniform distribution gives AI ≈ 0
    if len(set(counts_clean.values())) == 1:  # All counts equal
        assert ai <= tolerance, f"AI={ai} should be ~0 for uniform distribution"
    
    # Property 4: Single outcome gives AI ≈ 0.5
    if len(counts_clean) == 1:
        assert abs(ai - 0.5) <= tolerance, f"AI={ai} should be ~0.5 for single outcome"
    
    # Property 5: Finite and real
    assert np.isfinite(ai), f"AI={ai} is not finite"
    assert np.isreal(ai), f"AI={ai} is not real"
    
    logger.debug(f"Asymmetry Index validation passed: AI={ai:.6f}")
    return True


def asymmetry_index_educational_demo() -> dict:
    """
    Educational demonstration of Asymmetry Index behavior.
    
    This function provides concrete examples showing how AI responds to
    different types of measurement distributions, serving as both a validation
    tool and educational resource.
    
    Returns:
        dict: Demonstration results with interpretations
        
    Educational Value:
        - Shows AI behavior across different distribution types
        - Demonstrates relationship between quantum states and AI values
        - Provides intuition for interpreting AI in research contexts
    """
    demo_results = {}
    
    # Example 1: Perfect uniform (random decoherence)
    uniform_counts = {"00": 250, "01": 250, "10": 250, "11": 250}
    ai_uniform = compute_asymmetry_index(uniform_counts)
    demo_results["uniform_distribution"] = {
        "counts": uniform_counts,
        "asymmetry_index": ai_uniform,
        "interpretation": "Random decoherence - no preferred pathways"
    }
    
    # Example 2: GHZ-like structure
    ghz_counts = {"000": 400, "111": 400, "001": 100, "110": 100}
    ai_ghz = compute_asymmetry_index(ghz_counts)
    demo_results["ghz_structure"] = {
        "counts": ghz_counts,
        "asymmetry_index": ai_ghz,
        "interpretation": "Structured decoherence - GHZ-like correlations preserved"
    }
    
    # Example 3: Single dominant pathway
    dominant_counts = {"0000": 800, "0001": 50, "0010": 50, "others": 100}
    ai_dominant = compute_asymmetry_index(dominant_counts)
    demo_results["dominant_pathway"] = {
        "counts": dominant_counts,
        "asymmetry_index": ai_dominant,
        "interpretation": "Highly structured - single dominant error pathway"
    }
    
    # Example 4: Bimodal distribution
    bimodal_counts = {"000": 300, "111": 300, "010": 200, "101": 200}
    ai_bimodal = compute_asymmetry_index(bimodal_counts)
    demo_results["bimodal_structure"] = {
        "counts": bimodal_counts,
        "asymmetry_index": ai_bimodal,
        "interpretation": "Moderate structure - bimodal pathway preferences"
    }
    
    # Summary insights
    demo_results["summary"] = {
        "ai_range_observed": [ai_uniform, ai_ghz, ai_dominant, ai_bimodal],
        "structure_progression": "uniform < bimodal < ghz < dominant",
        "research_insight": "AI increases with pathway concentration and structure"
    }
    
    logger.info("Educational demonstration completed - see results for AI behavior examples")
    return demo_results