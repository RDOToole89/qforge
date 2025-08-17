"""
Information Theory Utilities for Quantum Decoherence Analysis

# Information-Theoretic Foundations
This module provides numerically stable, research-grade implementations of
fundamental information theory measures used in quantum decoherence pathway analysis.

# Mathematical Framework
All entropy measures use base-2 logarithms (bits) and incorporate Jeffreys prior
smoothing (α = 0.5) for categorical distributions to handle finite sample effects.

Key Measures:
- Entropy: H(X) = -∑ p(x) log₂ p(x)  
- Mutual Information: MI(X;Y) = H(X) + H(Y) - H(X,Y)
- Total Correlation: TC(X₁,...,Xₙ) = ∑ H(Xᵢ) - H(X₁,...,Xₙ)

# Quantum Measurement Context
For n-qubit quantum measurements, these measures quantify:
- Information content of measurement outcomes
- Correlations between qubits (classical + quantum)
- Multi-party correlations in entangled states

# Numerical Stability
- Jeffreys prior smoothing prevents log(0) issues
- Probability clamping to [1e-12, 1] before logarithms
- Careful normalization to maintain probability constraints
- Explicit handling of edge cases (uniform, deterministic distributions)

References:
- Cover & Thomas (2006), "Elements of Information Theory"
- Jeffreys (1946), "An Invariant Form for the Prior Probability"
- Watanabe (1960), "Information Theoretical Analysis of Multivariate Correlation"
"""

import numpy as np
import logging
from typing import Dict, Mapping, Tuple, Union
from collections import Counter

from ..constants import ALPHA, EPS, LOG_BASE, validate_counts_dict, validate_probability_array

logger = logging.getLogger(__name__)


def entropy(p: np.ndarray, base: float = LOG_BASE) -> float:
    """
    Compute Shannon entropy with numerical stability.
    
    Mathematical Definition:
        H(X) = -∑ p(x) log_base p(x)
        
    For base=2: entropy is measured in bits
    For base=e: entropy is measured in nats
    
    Numerical Features:
    - Automatic probability normalization
    - Jeffreys prior smoothing handled by caller
    - Safe handling of zero probabilities
    - Clamps probabilities to [EPS, 1] before logs
    
    Args:
        p: Probability array (will be normalized)
        base: Logarithm base (default: 2 for bits)
        
    Returns:
        float: Shannon entropy in bits (base=2) or nats (base=e)
        
    Complexity:
        Time: O(n) where n = len(p)
        Space: O(1)
        
    Examples:
        >>> p_uniform = np.array([0.25, 0.25, 0.25, 0.25])
        >>> entropy(p_uniform)  # Should be 2.0 bits
        2.0
        
        >>> p_deterministic = np.array([1.0, 0.0, 0.0, 0.0])  
        >>> entropy(p_deterministic)  # Should be ~0 bits
        0.0
    """
    # Validate and normalize
    p = validate_probability_array(p, "entropy input")
    
    # Compute entropy (zeros are handled by clamping in validate_probability_array)
    log_p = np.log(p) / np.log(base)
    h = -np.sum(p * log_p)
    
    # Ensure non-negative (numerical safety)
    h = max(0.0, h)
    
    logger.debug(f"Computed entropy = {h:.6f} bits (base={base})")
    return h


def counts_to_probabilities(counts: Mapping[str, int], 
                          alpha: float = ALPHA) -> Dict[str, float]:
    """
    Convert counts to smoothed probability distribution.
    
    Mathematical Definition:
        Jeffreys prior smoothing for categorical data:
        p̃(x) = (count(x) + α) / (N + α * K)
        
        where N = total counts, K = number of categories, α = prior strength
        
    Educational Notes:
        α = 0.5 (Jeffreys prior) provides uninformative prior for categorical
        distributions, giving good finite-sample behavior without strong bias.
        
    Args:
        counts: Dictionary {bitstring: count}
        alpha: Jeffreys prior parameter (default: 0.5)
        
    Returns:
        Dict[str, float]: Smoothed probability distribution
        
    Raises:
        ValueError: If counts are invalid (negative, empty, inconsistent)
    """
    # Validate input
    counts_clean = validate_counts_dict(counts)
    
    # Calculate smoothed probabilities
    total_counts = sum(counts_clean.values())
    num_outcomes = len(counts_clean)
    
    # Jeffreys smoothing: p̃(x) = (count(x) + α) / (N + α * K)
    smoothed_total = total_counts + alpha * num_outcomes
    
    probabilities = {}
    for bitstring, count in counts_clean.items():
        probabilities[bitstring] = (count + alpha) / smoothed_total
    
    # Verify normalization
    prob_sum = sum(probabilities.values())
    if not np.isclose(prob_sum, 1.0, atol=1e-10):
        logger.warning(f"Probability sum = {prob_sum:.10f} (expected 1.0)")
    
    logger.debug(f"Converted {len(counts_clean)} outcomes with α={alpha}")
    
    return probabilities


def marginal_distribution(counts: Mapping[str, int], 
                        qubit_index: int,
                        alpha: float = ALPHA) -> np.ndarray:
    """
    Compute marginal distribution for a single qubit.
    
    Mathematical Definition:
        For qubit i, marginalize joint distribution:
        p(X_i = 0) = ∑_{x: x_i=0} p(x₁,...,xₙ)
        p(X_i = 1) = ∑_{x: x_i=1} p(x₁,...,xₙ)
        
    With Jeffreys smoothing applied to marginal counts.
    
    Args:
        counts: Joint measurement counts {bitstring: count}
        qubit_index: Index of qubit to marginalize (0-indexed)
        alpha: Jeffreys prior parameter
        
    Returns:
        np.ndarray: [p(X_i=0), p(X_i=1)] with shape (2,)
        
    Raises:
        ValueError: If qubit_index is out of range
        
    Examples:
        >>> counts = {"00": 250, "01": 250, "10": 250, "11": 250}
        >>> marginal_distribution(counts, 0)  # First qubit
        array([0.5, 0.5])  # Uniform marginal
    """
    counts_clean = validate_counts_dict(counts)
    
    # Determine number of qubits from first bitstring
    if not counts_clean:
        raise ValueError("Empty counts dictionary")
    
    n_qubits = len(next(iter(counts_clean.keys())))
    
    if not 0 <= qubit_index < n_qubits:
        raise ValueError(f"qubit_index {qubit_index} out of range [0, {n_qubits-1}]")
    
    # Count marginal occurrences
    marginal_counts = [0, 0]  # [count for bit=0, count for bit=1]
    
    for bitstring, count in counts_clean.items():
        bit_value = int(bitstring[qubit_index])
        marginal_counts[bit_value] += count
    
    # Apply Jeffreys smoothing
    total_marginal = sum(marginal_counts)
    smoothed_total = total_marginal + alpha * 2  # 2 outcomes for binary
    
    marginal_probs = np.array([
        (marginal_counts[0] + alpha) / smoothed_total,
        (marginal_counts[1] + alpha) / smoothed_total
    ])
    
    logger.debug(f"Marginal for qubit {qubit_index}: {marginal_probs}")
    
    return marginal_probs


def pairwise_joint_distribution(counts: Mapping[str, int],
                               qubit_i: int, 
                               qubit_j: int,
                               alpha: float = ALPHA) -> np.ndarray:
    """
    Compute joint distribution for a pair of qubits.
    
    Mathematical Definition:
        For qubits i,j: compute 2×2 joint distribution
        p(X_i, X_j) with outcomes (0,0), (0,1), (1,0), (1,1)
        
    Args:
        counts: Joint measurement counts {bitstring: count}
        qubit_i: First qubit index
        qubit_j: Second qubit index  
        alpha: Jeffreys prior parameter
        
    Returns:
        np.ndarray: 2×2 joint probability matrix
                   [i,j] element = p(X_i=i, X_j=j)
                   
    Raises:
        ValueError: If qubit indices are out of range or equal
    """
    counts_clean = validate_counts_dict(counts)
    
    if not counts_clean:
        raise ValueError("Empty counts dictionary")
    
    n_qubits = len(next(iter(counts_clean.keys())))
    
    if not 0 <= qubit_i < n_qubits or not 0 <= qubit_j < n_qubits:
        raise ValueError(f"Qubit indices ({qubit_i}, {qubit_j}) out of range [0, {n_qubits-1}]")
    
    if qubit_i == qubit_j:
        raise ValueError(f"Qubit indices must be different, got both {qubit_i}")
    
    # Count joint occurrences 
    joint_counts = np.zeros((2, 2), dtype=int)
    
    for bitstring, count in counts_clean.items():
        bit_i = int(bitstring[qubit_i])
        bit_j = int(bitstring[qubit_j])
        joint_counts[bit_i, bit_j] += count
    
    # Apply Jeffreys smoothing
    total_joint = joint_counts.sum()
    smoothed_total = total_joint + alpha * 4  # 4 outcomes for 2-bit joint
    
    joint_probs = (joint_counts + alpha) / smoothed_total
    
    logger.debug(f"Joint distribution for qubits ({qubit_i}, {qubit_j}):\n{joint_probs}")
    
    return joint_probs


def mutual_information(counts: Mapping[str, int],
                      qubit_i: int,
                      qubit_j: int, 
                      alpha: float = ALPHA) -> float:
    """
    Compute mutual information between two qubits.
    
    Mathematical Definition:
        MI(X_i; X_j) = H(X_i) + H(X_j) - H(X_i, X_j)
                     = ∑∑ p(x_i, x_j) log₂[p(x_i, x_j) / (p(x_i)p(x_j))]
                     
    Physical Interpretation:
        MI quantifies the amount of information shared between qubits.
        MI = 0: qubits are independent
        MI > 0: qubits share information (correlation/entanglement)
        MI = 1: maximal correlation for binary variables
        
    Args:
        counts: Joint measurement counts {bitstring: count}
        qubit_i: First qubit index
        qubit_j: Second qubit index
        alpha: Jeffreys prior parameter
        
    Returns:
        float: Mutual information in bits
        
    Examples:
        >>> # Independent qubits
        >>> counts = {"00": 250, "01": 250, "10": 250, "11": 250}
        >>> mutual_information(counts, 0, 1)  # Should be ~0
        0.0
        
        >>> # Maximally correlated  
        >>> counts = {"00": 500, "11": 500}
        >>> mutual_information(counts, 0, 1)  # Should be ~1
        1.0
    """
    # Get marginal distributions
    p_i = marginal_distribution(counts, qubit_i, alpha)
    p_j = marginal_distribution(counts, qubit_j, alpha)
    
    # Get joint distribution
    p_ij = pairwise_joint_distribution(counts, qubit_i, qubit_j, alpha)
    
    # Compute marginal entropies
    h_i = entropy(p_i)
    h_j = entropy(p_j)
    
    # Compute joint entropy
    h_ij = entropy(p_ij.flatten())
    
    # Mutual information: MI = H(X_i) + H(X_j) - H(X_i, X_j)
    mi = h_i + h_j - h_ij
    
    # Ensure non-negative (numerical safety)
    mi = max(0.0, mi)
    
    logger.debug(f"MI({qubit_i},{qubit_j}) = {mi:.6f} bits "
                f"(H_i={h_i:.3f}, H_j={h_j:.3f}, H_ij={h_ij:.3f})")
    
    return mi


def total_correlation(counts: Mapping[str, int], 
                     alpha: float = ALPHA) -> float:
    """
    Compute total correlation (multi-information) across all qubits.
    
    Mathematical Definition:
        TC(X₁,...,Xₙ) = ∑ᵢ H(Xᵢ) - H(X₁,...,Xₙ)
                      = KL(P(X₁,...,Xₙ) || ∏ᵢ P(Xᵢ))
                      
    Physical Interpretation:
        TC quantifies total amount of correlation among all variables:
        - TC = 0: all qubits are independent
        - TC > 0: qubits share information 
        - TC = n-1: maximal correlation (n-qubit GHZ state)
        
    Properties:
        - Always non-negative: TC ≥ 0
        - Upper bound: TC ≤ (n-1) * min_i H(Xᵢ)
        - Includes both classical and quantum correlations
        
    Args:
        counts: Joint measurement counts {bitstring: count}
        alpha: Jeffreys prior parameter
        
    Returns:
        float: Total correlation in bits
        
    Examples:
        >>> # Product state (independent qubits)
        >>> counts = {"000": 125, "001": 125, "010": 125, "011": 125,
        ...           "100": 125, "101": 125, "110": 125, "111": 125}
        >>> total_correlation(counts)  # Should be ~0
        0.0
        
        >>> # GHZ state (maximal correlation)
        >>> counts = {"000": 500, "111": 500}
        >>> total_correlation(counts)  # Should be ~2.0
        2.0
    """
    counts_clean = validate_counts_dict(counts)
    
    if not counts_clean:
        raise ValueError("Empty counts dictionary")
    
    # Determine number of qubits
    n_qubits = len(next(iter(counts_clean.keys())))
    
    if n_qubits == 0:
        return 0.0
    
    # Compute marginal entropies: ∑ᵢ H(Xᵢ)
    marginal_entropy_sum = 0.0
    for i in range(n_qubits):
        p_i = marginal_distribution(counts_clean, i, alpha)
        h_i = entropy(p_i)
        marginal_entropy_sum += h_i
    
    # Compute joint entropy: H(X₁,...,Xₙ)
    joint_probs = counts_to_probabilities(counts_clean, alpha)
    joint_prob_array = np.array(list(joint_probs.values()))
    joint_entropy = entropy(joint_prob_array)
    
    # Total correlation: TC = ∑ᵢ H(Xᵢ) - H(X₁,...,Xₙ)
    tc = marginal_entropy_sum - joint_entropy
    
    # Ensure non-negative (numerical safety)
    tc = max(0.0, tc)
    
    logger.debug(f"Total correlation = {tc:.6f} bits "
                f"(∑H_i={marginal_entropy_sum:.3f}, H_joint={joint_entropy:.3f})")
    
    # Research interpretation
    max_possible_tc = (n_qubits - 1) * 1.0  # Upper bound for binary variables
    tc_fraction = tc / max_possible_tc if max_possible_tc > 0 else 0.0
    
    if tc_fraction > 0.7:
        logger.info(f"High total correlation ({tc_fraction:.1%} of maximum)")
    elif tc_fraction > 0.3:
        logger.info(f"Moderate total correlation ({tc_fraction:.1%} of maximum)")
    else:
        logger.debug(f"Low total correlation ({tc_fraction:.1%} of maximum)")
    
    return tc


def jensen_shannon_divergence(p: np.ndarray, q: np.ndarray) -> float:
    """
    Compute Jensen-Shannon divergence between two probability distributions.
    
    Mathematical Definition:
        Let M = (P + Q) / 2
        JSD(P||Q) = 0.5 * KL(P||M) + 0.5 * KL(Q||M)
        
    Properties:
        - Symmetric: JSD(P||Q) = JSD(Q||P)
        - Bounded: 0 ≤ JSD ≤ 1 (for base-2 logs)
        - Metric: √JSD satisfies triangle inequality
        
    Args:
        p: First probability distribution
        q: Second probability distribution
        
    Returns:
        float: Jensen-Shannon divergence in bits
        
    Raises:
        ValueError: If distributions have different lengths
    """
    p = validate_probability_array(p, "first distribution")
    q = validate_probability_array(q, "second distribution") 
    
    if len(p) != len(q):
        raise ValueError(f"Distribution lengths differ: {len(p)} vs {len(q)}")
    
    # Compute mixture distribution
    m = 0.5 * (p + q)
    
    # KL divergence components (using natural log for numerical stability)
    def kl_divergence(x, y):
        # Ensure no division by zero (already handled by validate_probability_array)
        return np.sum(x * np.log(x / y))
    
    # Jensen-Shannon divergence
    jsd = 0.5 * kl_divergence(p, m) + 0.5 * kl_divergence(q, m)
    
    # Convert to base-2 
    jsd = jsd / np.log(2.0)
    
    # Ensure bounds [0, 1]
    jsd = np.clip(jsd, 0.0, 1.0)
    
    logger.debug(f"Jensen-Shannon divergence = {jsd:.6f}")
    
    return jsd