"""
Core Implementation of Structured Decoherence Pathway Metrics

This module implements the 5 quantitative metrics for detecting structured 
decoherence patterns in quantum measurement data.

Mathematical Definitions:
    AI = (1/N) Σᵢ |pᵢ - p_uniform| / p_uniform
    PCR = (Top 25% frequencies) / (Bottom 25% frequencies)  
    EEC = Correlation coefficient between entanglement topology and error patterns
    TPS = 1 - σ(pathway_rankings) / mean(pathway_rankings)
    CES = Critical threshold where structured patterns emerge (≥3 qubits)

Author: Structured Decoherence Research
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Optional, Any
from collections import Counter
from scipy.stats import pearsonr

logger = logging.getLogger("QuantumExperiment.Analysis.StructuredDecoherence")


def compute_asymmetry_index(counts: Dict[str, int]) -> float:
    """
    Compute Asymmetry Index (AI) - deviation from uniform error distribution.
    
    AI quantifies how much the observed distribution deviates from a uniform
    distribution across all possible measurement outcomes.
    
    Formula: AI = (1/N) Σᵢ |pᵢ - p_uniform| / p_uniform
    
    Args:
        counts: Dictionary mapping bitstrings to measurement counts
        
    Returns:
        float: Asymmetry index (0 = perfectly uniform, higher = more structured)
    """
    if not counts:
        return 0.0
        
    total_shots = sum(counts.values())
    num_outcomes = len(counts)
    
    # Expected uniform probability for each outcome
    p_uniform = 1.0 / num_outcomes
    
    # Calculate asymmetry
    asymmetry_sum = 0.0
    for bitstring, count in counts.items():
        p_observed = count / total_shots
        asymmetry_sum += abs(p_observed - p_uniform) / p_uniform
    
    ai = asymmetry_sum / num_outcomes
    
    logger.debug(f"Computed AI = {ai:.4f} for {num_outcomes} outcomes")
    return ai


def compute_pathway_concentration_ratio(counts: Dict[str, int]) -> float:
    """
    Compute Pathway Concentration Ratio (PCR) - concentration in top error pathways.
    
    PCR measures how much the decoherence is concentrated in the most frequent
    error pathways compared to the least frequent ones.
    
    Formula: PCR = (Top 25% frequencies) / (Bottom 25% frequencies)
    
    Args:
        counts: Dictionary mapping bitstrings to measurement counts
        
    Returns:
        float: Pathway concentration ratio (higher = more concentrated)
    """
    if not counts or len(counts) < 4:
        return 1.0  # Not enough data for meaningful quartiles
        
    # Sort outcomes by frequency
    sorted_counts = sorted(counts.values(), reverse=True)
    n = len(sorted_counts)
    
    # Calculate quartile boundaries
    top_25_idx = max(1, n // 4)
    bottom_25_idx = max(1, n // 4)
    
    # Sum top and bottom quartiles
    top_25_sum = sum(sorted_counts[:top_25_idx])
    bottom_25_sum = sum(sorted_counts[-bottom_25_idx:])
    
    # Avoid division by zero
    if bottom_25_sum == 0:
        return float('inf') if top_25_sum > 0 else 1.0
        
    pcr = top_25_sum / bottom_25_sum
    
    logger.debug(f"Computed PCR = {pcr:.4f} (top {top_25_idx} vs bottom {bottom_25_idx})")
    return pcr


def compute_entanglement_error_correlation(counts: Dict[str, int], 
                                         state_type: str = "GHZ") -> float:
    """
    Compute Entanglement-Error Correlation (EEC) - correlation between topology and errors.
    
    EEC measures how well the error patterns correlate with the expected
    entanglement structure of the quantum state.
    
    Args:
        counts: Dictionary mapping bitstrings to measurement counts
        state_type: Type of quantum state ("GHZ", "W", "BELL", "CLUSTER")
        
    Returns:
        float: Correlation coefficient (-1 to 1, higher = stronger correlation)
    """
    if not counts:
        return 0.0
        
    # Extract bitstrings and their frequencies
    bitstrings = list(counts.keys())
    frequencies = list(counts.values())
    
    if len(bitstrings) < 2:
        return 0.0
        
    # Compute entanglement scores based on state type
    entanglement_scores = []
    
    for bitstring in bitstrings:
        if state_type.upper() == "GHZ":
            # For GHZ states, highest entanglement for |000⟩ and |111⟩
            score = _compute_ghz_entanglement_score(bitstring)
        elif state_type.upper() == "W":
            # For W states, highest entanglement for single-excitation states
            score = _compute_w_entanglement_score(bitstring)
        elif state_type.upper() == "BELL":
            # For Bell states, highest entanglement for |00⟩ and |11⟩
            score = _compute_bell_entanglement_score(bitstring)
        else:
            # Default: uniform scoring
            score = 1.0
            
        entanglement_scores.append(score)
    
    # Compute correlation between entanglement scores and error frequencies
    if len(set(entanglement_scores)) > 1 and len(set(frequencies)) > 1:
        correlation, _ = pearsonr(entanglement_scores, frequencies)
        eec = correlation if not np.isnan(correlation) else 0.0
    else:
        eec = 0.0
    
    logger.debug(f"Computed EEC = {eec:.4f} for {state_type} state")
    return eec


def compute_temporal_pathway_stability(pathway_rankings: List[List[str]]) -> float:
    """
    Compute Temporal Pathway Stability (TPS) - consistency across noise levels.
    
    TPS measures how stable the ranking of error pathways remains across
    different noise levels or experimental runs.
    
    Formula: TPS = 1 - σ(pathway_rankings) / mean(pathway_rankings)
    
    Args:
        pathway_rankings: List of pathway rankings for different conditions
        
    Returns:
        float: Temporal stability (0-1, higher = more stable)
    """
    if not pathway_rankings or len(pathway_rankings) < 2:
        return 1.0  # Perfect stability with insufficient data
        
    # Convert rankings to numerical stability scores
    stability_scores = []
    
    # Use first ranking as reference
    reference_ranking = pathway_rankings[0]
    
    for ranking in pathway_rankings[1:]:
        # Compute rank correlation with reference
        stability = _compute_ranking_similarity(reference_ranking, ranking)
        stability_scores.append(stability)
    
    if not stability_scores:
        return 1.0
        
    # Calculate temporal stability
    mean_stability = np.mean(stability_scores)
    std_stability = np.std(stability_scores)
    
    # TPS formula: higher stability = lower variance
    if mean_stability > 0:
        tps = 1 - (std_stability / mean_stability)
        tps = max(0.0, min(1.0, tps))  # Clamp to [0,1]
    else:
        tps = 0.0
    
    logger.debug(f"Computed TPS = {tps:.4f} across {len(pathway_rankings)} rankings")
    return tps


def compute_complexity_emergence_score(multi_qubit_data: Dict[int, Dict[str, int]]) -> float:
    """
    Compute Complexity Emergence Score (CES) - threshold for structured emergence.
    
    CES quantifies at what complexity level (number of qubits) structured
    decoherence patterns begin to emerge clearly above noise.
    
    Args:
        multi_qubit_data: Dictionary mapping num_qubits to measurement counts
        
    Returns:
        float: Emergence score (higher = clearer emergence at higher complexity)
    """
    if not multi_qubit_data or len(multi_qubit_data) < 2:
        return 0.0
        
    qubit_counts = sorted(multi_qubit_data.keys())
    asymmetry_progression = []
    
    # Compute AI for each qubit count
    for num_qubits in qubit_counts:
        counts = multi_qubit_data[num_qubits]
        ai = compute_asymmetry_index(counts)
        asymmetry_progression.append(ai)
    
    # Find the emergence threshold (where AI starts increasing significantly)
    if len(asymmetry_progression) < 2:
        return 0.0
        
    # Compute rate of change in asymmetry
    emergence_indicators = []
    for i in range(1, len(asymmetry_progression)):
        rate_of_change = asymmetry_progression[i] - asymmetry_progression[i-1]
        emergence_indicators.append(rate_of_change)
    
    # CES is the magnitude of emergence above the 3-qubit threshold
    if len(qubit_counts) >= 2 and qubit_counts[0] <= 3:
        # Focus on emergence at 3+ qubits (research hypothesis)
        threshold_idx = next((i for i, q in enumerate(qubit_counts) if q >= 3), 0)
        if threshold_idx < len(emergence_indicators):
            ces = max(0.0, emergence_indicators[threshold_idx])
        else:
            ces = 0.0
    else:
        ces = np.mean(emergence_indicators) if emergence_indicators else 0.0
    
    logger.debug(f"Computed CES = {ces:.4f} across {len(qubit_counts)} qubit counts")
    return ces


# Helper functions for entanglement scoring

def _compute_ghz_entanglement_score(bitstring: str) -> float:
    """Compute entanglement score for GHZ state topology."""
    n = len(bitstring)
    
    # Highest score for |000...⟩ and |111...⟩ (GHZ computational basis)
    if bitstring == '0' * n or bitstring == '1' * n:
        return 1.0
    
    # Medium score for single bit-flip errors (preserve some entanglement)
    hamming_from_00 = sum(c == '1' for c in bitstring)
    hamming_from_11 = sum(c == '0' for c in bitstring)
    min_hamming = min(hamming_from_00, hamming_from_11)
    
    if min_hamming == 1:
        return 0.7  # Single bit-flip
    elif min_hamming == 2:
        return 0.4  # Two bit-flips
    else:
        return 0.1  # Complete decoherence


def _compute_w_entanglement_score(bitstring: str) -> float:
    """Compute entanglement score for W state topology."""
    ones_count = bitstring.count('1')
    
    # W state has exactly one excitation
    if ones_count == 1:
        return 1.0
    elif ones_count == 0 or ones_count == len(bitstring):
        return 0.3  # All ground or all excited  
    else:
        return 0.1  # Multiple excitations


def _compute_bell_entanglement_score(bitstring: str) -> float:
    """Compute entanglement score for Bell state topology."""
    if len(bitstring) != 2:
        return 0.0
        
    # Bell states: |00⟩, |01⟩, |10⟩, |11⟩
    if bitstring in ['00', '11']:
        return 1.0  # Perfect correlation
    elif bitstring in ['01', '10']:
        return 0.8  # Anti-correlation
    else:
        return 0.0


def _compute_ranking_similarity(ranking1: List[str], ranking2: List[str]) -> float:
    """Compute similarity between two pathway rankings."""
    # Simple rank correlation approximation
    common_elements = set(ranking1) & set(ranking2)
    if not common_elements:
        return 0.0
        
    # Compute Spearman-like correlation for common elements
    rank_diffs = []
    for element in common_elements:
        try:
            rank1 = ranking1.index(element)
            rank2 = ranking2.index(element)
            rank_diffs.append(abs(rank1 - rank2))
        except ValueError:
            continue
    
    if not rank_diffs:
        return 0.0
        
    # Convert to similarity score (lower differences = higher similarity)
    max_possible_diff = max(len(ranking1), len(ranking2))
    avg_diff = np.mean(rank_diffs)
    similarity = 1.0 - (avg_diff / max_possible_diff)
    
    return max(0.0, similarity)