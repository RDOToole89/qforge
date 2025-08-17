"""
Schema-Required Metrics for Structured Decoherence Pathway Research

# Missing Metrics from V1.0 Schema Suite
This module implements the three critical metrics required by the frozen v1.0 schemas
that were missing from the original implementation: Structure Score (SS), 
Concentration Index (CI), and Total Correlation (TC).

# Physical Significance
These metrics complete the quantitative framework for detecting structured
decoherence patterns in quantum systems:
- **Structure Score**: Quantifies deviation from null model expectations
- **Concentration Index**: Measures inequality in error distribution
- **Total Correlation**: Captures multi-qubit correlations beyond pairwise

# Research Applications
Together with the existing 5 metrics (AI, PCR, EEC, TPS, CES), these complete
the 8-metric suite for comprehensive pathway characterization, enabling:
- Statistical validation against null models
- Economic-inspired inequality analysis
- Information-theoretic correlation measures

# Mathematical Foundations
- SS: Jensen-Shannon Divergence from null model predictions
- CI: Gini coefficient from economics applied to quantum measurements  
- TC: Multi-information from information theory

# Educational Framework
This module teaches advanced concepts bridging quantum mechanics with:
- Information theory (divergences, entropy, mutual information)
- Statistical physics (null models, ensemble comparisons)
- Economics (inequality measures, concentration analysis)
- Machine learning (distribution distances, correlation metrics)
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Any
from collections import Counter

logger = logging.getLogger("QuantumExperiment.Analysis.SchemaMetrics")


def compute_structure_score(counts: Dict[str, int], 
                           null_model_counts: Optional[Dict[str, int]] = None) -> float:
    """
    Compute Structure Score (SS) - Jensen-Shannon divergence from null model.
    
    # Information-Theoretic Foundation
    The Jensen-Shannon divergence (JSD) is a symmetric, bounded measure of
    distribution distance. For quantum measurements:
    JSD(P||Q) = 0.5 * KL(P||M) + 0.5 * KL(Q||M) where M = (P+Q)/2
    
    # Physical Interpretation
    SS measures how much the observed error distribution deviates from what
    we'd expect under purely random decoherence (null model). Higher SS
    indicates more structured pathways.
    
    # Null Model Construction
    If not provided, we construct a factorized null model using marginal
    distributions. This represents the expectation under independent
    qubit decoherence with no structured pathways.
    
    # Research Significance
    SS > 0.1 suggests structured decoherence pathways
    SS > 0.3 indicates strong pathway preferences
    SS > 0.5 shows highly non-random error patterns
    
    Args:
        counts: Observed measurement counts {bitstring: count}
        null_model_counts: Expected counts under null hypothesis
        
    Returns:
        float: Structure Score ∈ [0, 1] (0 = matches null, 1 = maximally different)
        
    Educational Notes:
        - JSD is the square root of JS divergence, making it a true metric
        - Unlike KL divergence, JSD is symmetric: JSD(P||Q) = JSD(Q||P)
        - JSD is bounded: 0 ≤ JSD ≤ 1 for normalized distributions
        - JSD = 0 only when distributions are identical
    """
    if not counts:
        logger.warning("Empty counts provided for structure score")
        return 0.0
    
    # Use research-grade null model and Jensen-Shannon divergence
    from ..core.null_models import factorized_null_model
    from ..core.information_theory import jensen_shannon_divergence, counts_to_probabilities
    
    # Convert observed counts to probabilities
    observed_probs_dict = counts_to_probabilities(counts)
    
    # Generate factorized null model if not provided
    if null_model_counts is None:
        null_model_probs = factorized_null_model(counts)
        logger.debug("Using factorized null model for structure score")
    else:
        null_model_probs = counts_to_probabilities(null_model_counts)
    
    # Ensure both distributions have same outcomes (needed for JSD)
    all_outcomes = sorted(set(observed_probs_dict.keys()) | set(null_model_probs.keys()))
    
    observed_array = np.array([observed_probs_dict.get(outcome, 0.0) for outcome in all_outcomes])
    null_array = np.array([null_model_probs.get(outcome, 0.0) for outcome in all_outcomes])
    
    # Compute Jensen-Shannon divergence using our research-grade implementation
    structure_score = jensen_shannon_divergence(observed_array, null_array)
    
    logger.debug(f"Computed Structure Score = {structure_score:.4f}")
    
    return structure_score


def compute_concentration_index(counts: Dict[str, int]) -> float:
    """
    Compute Concentration Index (CI) - Gini coefficient of error distribution.
    
    # Economic Origins
    The Gini coefficient, developed by Corrado Gini (1912), measures inequality
    in distributions. Originally for wealth inequality, it perfectly captures
    error concentration in quantum measurements.
    
    # Mathematical Definition
    Gini = (2 * Σᵢ i*xᵢ) / (n * Σᵢ xᵢ) - (n+1)/n
    where x is sorted in ascending order
    
    # Physical Interpretation for Quantum Systems
    - CI = 0: Perfect equality (all outcomes equally likely)
    - CI = 0.3-0.4: Moderate concentration (some preferred pathways)
    - CI = 0.6-0.7: High concentration (dominant error pathways)
    - CI → 1: Extreme concentration (single dominant pathway)
    
    # Research Applications
    CI reveals whether decoherence concentrates in specific pathways:
    - Low CI + High AI: Broad but non-uniform errors
    - High CI + High AI: Focused pathway structure
    - High CI + Low AI: Few outcomes but randomly distributed
    
    Args:
        counts: Measurement counts {bitstring: count}
        
    Returns:
        float: Gini coefficient ∈ [0, 1] (0 = equality, 1 = maximal inequality)
        
    Educational Notes:
        - Gini is scale-invariant: doesn't depend on total counts
        - Geometric interpretation: ratio of areas in Lorenz curve
        - Related to other inequality measures (Theil, Atkinson)
        - Captures "long tail" phenomena in error distributions
    """
    if not counts or len(counts) == 0:
        logger.warning("Empty counts for concentration index")
        return 0.0
    
    # Convert to numpy array and sort
    frequencies = np.array(list(counts.values()), dtype=float)
    
    # Handle single outcome case
    if len(frequencies) == 1:
        return 0.0  # No inequality with single outcome
    
    # Sort frequencies in ascending order (required for Gini)
    frequencies = np.sort(frequencies)
    n = len(frequencies)
    
    # Handle case where all frequencies are zero
    if frequencies.sum() == 0:
        return 0.0
    
    # Normalize frequencies (work with proportions)
    frequencies = frequencies / frequencies.sum()
    
    # Calculate Gini coefficient using the standard formula
    # G = (2 * Σᵢ i*xᵢ) / (n * Σᵢ xᵢ) - (n+1)/n
    index = np.arange(1, n + 1)  # 1-indexed for formula
    gini = (2.0 * np.sum(index * frequencies)) / (n * np.sum(frequencies)) - (n + 1) / n
    
    # Ensure result is in valid range [0, 1]
    gini = max(0.0, min(1.0, gini))
    
    logger.debug(f"Computed Concentration Index (Gini) = {gini:.4f} for {n} outcomes")
    
    # Log distribution characteristics for research
    if gini > 0.7:
        logger.info("High concentration detected - strong pathway preferences")
    elif gini > 0.4:
        logger.info("Moderate concentration - emerging pathway structure")
    else:
        logger.debug("Low concentration - distributed error patterns")
    
    return gini


def compute_total_correlation(counts: Dict[str, int]) -> float:
    """
    Compute Total Correlation (TC) - Multi-information in quantum measurements.
    
    # Information-Theoretic Foundation
    Total Correlation (Watanabe 1960) measures the total amount of correlation
    among all variables in a multivariate distribution:
    TC = Σᵢ H(Xᵢ) - H(X₁, X₂, ..., Xₙ)
    
    # Quantum Interpretation
    For n-qubit measurements, TC quantifies how much information is shared
    between qubits beyond what's expected from independent measurements:
    - TC = 0: Qubits are independent (product state)
    - TC > 0: Qubits share information (entanglement or classical correlation)
    - TC = n-1: Maximum correlation (e.g., GHZ state)
    
    # Research Significance
    TC reveals the information structure of decoherence pathways:
    - High TC: Errors are correlated across qubits
    - Low TC: Errors affect qubits independently
    - TC patterns: Identify which qubit subsets maintain correlations
    
    # Relationship to Entanglement
    While TC includes both classical and quantum correlations, in the context
    of decoherence from entangled states, it captures how error patterns
    preserve or destroy multi-qubit correlations.
    
    Args:
        counts: Measurement counts {bitstring: count}
        
    Returns:
        float: Total Correlation in bits (≥ 0)
        
    Educational Notes:
        - TC is also called "multi-information" or "integration"
        - TC = 0 iff all variables are mutually independent
        - TC ≤ min(H(Xᵢ)) * (n-1) where n is number of variables
        - Related to mutual information: TC = generalization to n variables
        - In neuroscience, TC measures "integrated information"
    """
    # Use the research-grade implementation from core information theory module
    from ..core.information_theory import total_correlation
    return total_correlation(counts)


def create_null_model(state_type: str, num_qubits: int) -> Dict[str, float]:
    """
    Create null model for baseline comparison in structure score calculation.
    
    # Null Model Philosophy
    The null model represents our expectation under the hypothesis of
    "no structured pathways" - i.e., purely random decoherence without
    preferential error channels.
    
    # Model Construction Strategy
    Depends on quantum state and noise type:
    1. **Uniform Model**: All outcomes equally likely (maximum entropy)
    2. **State-Aware Model**: Respects initial state structure
    3. **Noise-Aware Model**: Incorporates known noise characteristics
    4. **Empirical Model**: Based on control experiments
    
    # Research Applications
    - Hypothesis testing: Does observation differ from random expectation?
    - Pathway detection: Which outcomes deviate most from null model?
    - Significance assessment: Statistical validation of structure
    
    Args:
        state_type: Initial quantum state (GHZ, W, Bell, etc.)
        num_qubits: Number of qubits in system
        
    Returns:
        Dict[str, float]: Null model probability distribution
        
    Educational Notes:
        - Null models are fundamental to statistical physics
        - Choice of null model affects interpretation of results
        - Multiple null models can test different hypotheses
        - Null model should preserve known constraints
    """
    # For now, implement uniform null model as baseline
    # Future: Add state-specific and noise-aware null models
    
    n_outcomes = 2 ** num_qubits
    uniform_prob = 1.0 / n_outcomes
    
    # Create all possible bitstrings
    null_distribution = {}
    for i in range(n_outcomes):
        bitstring = format(i, f'0{num_qubits}b')
        null_distribution[bitstring] = uniform_prob
    
    logger.debug(f"Created uniform null model for {num_qubits} qubits "
                f"with {n_outcomes} outcomes")
    
    # Future enhancements based on state type
    if state_type == "GHZ" and num_qubits > 1:
        # GHZ null model could emphasize |00...0⟩ and |11...1⟩
        logger.debug("Note: GHZ-specific null model not yet implemented, using uniform")
    elif state_type == "W" and num_qubits > 1:
        # W null model could emphasize single-excitation states
        logger.debug("Note: W-specific null model not yet implemented, using uniform")
    
    return null_distribution