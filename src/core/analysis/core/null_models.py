"""
Null Models for Structured Decoherence Hypothesis Testing

# Statistical Null Model Framework
This module provides baseline null models for testing the structured decoherence
hypothesis. Null models represent the expectation under "no structured pathways" -
purely random decoherence without preferential error channels.

# Mathematical Foundation
The primary null model is the factorized (independent) model:
Q(x₁,...,xₙ) = ∏ᵢ q(xᵢ)

where q(xᵢ) are marginal probabilities estimated from data with Jeffreys smoothing.
This models the case where all qubits decohere independently.

# Research Applications
Null models enable hypothesis testing:
- Structure Score: JSD(Observed || Factorized Null)
- Parametric Bootstrap: Generate synthetic data under null
- P-value Calculation: Compare observed metrics to null distribution

# Advanced Features (Optional)
- Readout Confusion: Account for measurement errors
- Tikhonov Regularization: Numerical stability for matrix inversion
- State-Aware Nulls: Respect known initial state structure

References:
- Cover & Thomas (2006), "Elements of Information Theory"
- Tikhonov & Arsenin (1977), "Solutions of Ill-posed Problems"
- Nielsen & Chuang (2010), "Quantum Computation and Quantum Information"
"""

import numpy as np
import logging
from typing import Dict, Mapping, Optional, Tuple, List
from scipy.linalg import solve

from .information_theory import marginal_distribution, counts_to_probabilities
from ..constants import ALPHA, TIKHONOV_LAMBDA, validate_counts_dict

logger = logging.getLogger(__name__)


def factorized_null_model(counts: Mapping[str, int], 
                          alpha: float = ALPHA) -> Dict[str, float]:
    """
    Create factorized (independent) null model from marginal distributions.
    
    Mathematical Definition:
        For n qubits, construct null model as:
        Q(x₁,...,xₙ) = ∏ᵢ q(xᵢ)
        
        where q(xᵢ) are marginal probabilities estimated from data:
        q(xᵢ = 0) = (count(xᵢ=0) + α) / (N + 2α)
        q(xᵢ = 1) = (count(xᵢ=1) + α) / (N + 2α)
        
    Physical Interpretation:
        This null model assumes all qubits decohere independently, with no
        correlations or structured pathways. Any deviation from this model
        suggests structured decoherence.
        
    Research Usage:
        Primary null model for Structure Score calculation:
        SS = JSD(Observed || Factorized_Null)
        
    Args:
        counts: Empirical measurement counts {bitstring: count}
        alpha: Jeffreys prior parameter for smoothing (default: 0.5)
        
    Returns:
        Dict[str, float]: Factorized null probabilities for all bitstrings
        
    Examples:
        >>> counts = {"00": 250, "01": 250, "10": 250, "11": 250}
        >>> null = factorized_null_model(counts)
        >>> # Should return uniform distribution: each outcome = 0.25
        
    Raises:
        ValueError: If counts are invalid or inconsistent
    """
    counts_clean = validate_counts_dict(counts)
    
    if not counts_clean:
        raise ValueError("Empty counts dictionary")
    
    # Determine number of qubits
    n_qubits = len(next(iter(counts_clean.keys())))
    
    if n_qubits == 0:
        raise ValueError("Zero-length bitstrings")
    
    logger.debug(f"Building factorized null model for {n_qubits} qubits")
    
    # Compute marginal distributions for each qubit
    marginals = []
    for i in range(n_qubits):
        marginal = marginal_distribution(counts_clean, i, alpha)
        marginals.append(marginal)
        logger.debug(f"Marginal {i}: p(0)={marginal[0]:.4f}, p(1)={marginal[1]:.4f}")
    
    # Generate all possible bitstrings and compute factorized probabilities
    null_model = {}
    
    for outcome_index in range(2**n_qubits):
        # Convert outcome index to bitstring
        bitstring = format(outcome_index, f'0{n_qubits}b')
        
        # Compute factorized probability: ∏ᵢ q(xᵢ)
        factorized_prob = 1.0
        for i, bit_char in enumerate(bitstring):
            bit_value = int(bit_char)
            factorized_prob *= marginals[i][bit_value]
        
        null_model[bitstring] = factorized_prob
    
    # Verify normalization
    total_prob = sum(null_model.values())
    if not np.isclose(total_prob, 1.0, atol=1e-10):
        logger.warning(f"Null model normalization: {total_prob:.10f} (expected 1.0)")
        # Renormalize if needed
        null_model = {bs: prob/total_prob for bs, prob in null_model.items()}
    
    logger.info(f"Created factorized null model with {len(null_model)} outcomes")
    
    return null_model


def generate_null_samples(null_model: Dict[str, float],
                         num_samples: int,
                         rng: np.random.Generator) -> List[Dict[str, int]]:
    """
    Generate synthetic count samples from null model for parametric bootstrap.
    
    Mathematical Process:
        1. Sample N outcomes from multinomial distribution Mult(N, Q)
        2. Convert samples to counts dictionaries
        3. Return list of synthetic count datasets
        
    Research Usage:
        Generate synthetic datasets under null hypothesis for:
        - Parametric bootstrap confidence intervals
        - P-value calculation via Monte Carlo
        - Power analysis for detecting structured decoherence
        
    Args:
        null_model: Null probability distribution {bitstring: probability}
        num_samples: Number of shots per synthetic dataset
        rng: Random number generator for reproducibility
        
    Returns:
        List[Dict[str, int]]: List of synthetic count dictionaries
        
    Examples:
        >>> rng = np.random.default_rng(42)
        >>> null = {"00": 0.25, "01": 0.25, "10": 0.25, "11": 0.25}
        >>> samples = generate_null_samples(null, 1000, rng)
        >>> len(samples)  # Should return list of count dictionaries
    """
    if not null_model:
        raise ValueError("Empty null model")
    
    if num_samples <= 0:
        raise ValueError(f"num_samples must be positive, got {num_samples}")
    
    # Extract bitstrings and probabilities in consistent order
    bitstrings = sorted(null_model.keys())  # Ensure deterministic ordering
    probabilities = np.array([null_model[bs] for bs in bitstrings])
    
    # Validate probabilities
    if not np.isclose(probabilities.sum(), 1.0, atol=1e-10):
        raise ValueError(f"Null model probabilities sum to {probabilities.sum():.10f}, not 1.0")
    
    # Sample from multinomial distribution
    sampled_counts = rng.multinomial(num_samples, probabilities)
    
    # Convert to counts dictionary
    synthetic_counts = {}
    for i, bitstring in enumerate(bitstrings):
        if sampled_counts[i] > 0:  # Only include non-zero counts
            synthetic_counts[bitstring] = int(sampled_counts[i])
    
    # Handle edge case where some outcomes might have zero counts
    if not synthetic_counts:
        # This is very rare but possible - give one count to first outcome
        synthetic_counts[bitstrings[0]] = 1
        logger.warning("All synthetic counts were zero, added one count to maintain valid dataset")
    
    logger.debug(f"Generated synthetic counts with {len(synthetic_counts)} non-zero outcomes")
    
    return [synthetic_counts]  # Return as list to match interface


def parametric_bootstrap_null(observed_counts: Mapping[str, int],
                             n_bootstrap: int = 1000,
                             rng: Optional[np.random.Generator] = None) -> List[Dict[str, int]]:
    """
    Perform parametric bootstrap under factorized null model.
    
    Mathematical Process:
        1. Estimate marginal distributions from observed data
        2. Construct factorized null model Q(x) = ∏ᵢ q(xᵢ)
        3. Generate B synthetic datasets from Q
        4. Return list of synthetic count dictionaries
        
    Research Application:
        This provides the synthetic data needed for:
        - Null distribution of Structure Score
        - P-value calculation: P(SS_null ≥ SS_observed)
        - Confidence intervals under null hypothesis
        
    Args:
        observed_counts: Original measurement counts
        n_bootstrap: Number of bootstrap samples to generate
        rng: Random generator (if None, creates new one)
        
    Returns:
        List[Dict[str, int]]: List of synthetic count datasets under null
        
    Examples:
        >>> counts = {"000": 200, "111": 300, "others": 500}
        >>> rng = np.random.default_rng(42)
        >>> null_samples = parametric_bootstrap_null(counts, 100, rng)
        >>> len(null_samples)  # Should be 100
    """
    if rng is None:
        rng = np.random.default_rng()
    
    counts_clean = validate_counts_dict(observed_counts)
    total_shots = sum(counts_clean.values())
    
    logger.info(f"Performing parametric bootstrap under null with {n_bootstrap} samples")
    
    # Build factorized null model from observed data
    null_model = factorized_null_model(counts_clean)
    
    # Generate synthetic datasets
    bootstrap_samples = []
    for i in range(n_bootstrap):
        synthetic_sample = generate_null_samples(null_model, total_shots, rng)[0]
        bootstrap_samples.append(synthetic_sample)
        
        if (i + 1) % 100 == 0:
            logger.debug(f"Generated {i + 1}/{n_bootstrap} bootstrap samples")
    
    logger.info(f"Completed parametric bootstrap: {len(bootstrap_samples)} samples")
    
    return bootstrap_samples


def readout_confusion_model(counts: Mapping[str, int],
                           confusion_matrices: List[np.ndarray],
                           regularization: float = TIKHONOV_LAMBDA) -> Dict[str, float]:
    """
    Apply readout confusion correction to measurement counts.
    
    Mathematical Framework:
        Readout confusion model:
        P_measured = C * P_true
        
        where C is the readout confusion matrix and P_true is the ideal distribution.
        
        To find P_true: P_true = C⁻¹ * P_measured
        
        For numerical stability, use Tikhonov regularization:
        P_true = (C^T C + λI)⁻¹ C^T * P_measured
        
    Physical Interpretation:
        Real quantum devices have imperfect readout. The confusion matrix C_ij
        gives the probability of measuring outcome j when the true state is i.
        This correction attempts to recover the ideal distribution.
        
    Research Usage:
        Optional enhancement for null models when readout calibration data
        is available. Can improve accuracy of Structure Score calculations.
        
    Args:
        counts: Measured counts with readout errors
        confusion_matrices: Per-qubit confusion matrices (2×2 each)
        regularization: Tikhonov parameter for numerical stability
        
    Returns:
        Dict[str, float]: Corrected probability distribution
        
    Notes:
        This is an advanced feature. Most research can use the simpler
        factorized null model without readout correction.
        
    Raises:
        ValueError: If confusion matrices are invalid
        np.linalg.LinAlgError: If matrix inversion fails
    """
    counts_clean = validate_counts_dict(counts)
    
    if not counts_clean:
        raise ValueError("Empty counts dictionary")
    
    n_qubits = len(next(iter(counts_clean.keys())))
    
    if len(confusion_matrices) != n_qubits:
        raise ValueError(f"Need {n_qubits} confusion matrices, got {len(confusion_matrices)}")
    
    # Validate confusion matrices
    for i, C in enumerate(confusion_matrices):
        if C.shape != (2, 2):
            raise ValueError(f"Confusion matrix {i} has shape {C.shape}, expected (2,2)")
        if not np.allclose(C.sum(axis=1), 1.0):
            raise ValueError(f"Confusion matrix {i} rows don't sum to 1")
        if np.any(C < 0) or np.any(C > 1):
            raise ValueError(f"Confusion matrix {i} has probabilities outside [0,1]")
    
    logger.info(f"Applying readout confusion correction with λ={regularization}")
    
    # Build full confusion matrix for n-qubit system
    # This is computationally expensive for large n_qubits
    if n_qubits > 8:
        logger.warning(f"Readout correction for {n_qubits} qubits may be slow")
    
    # For now, implement a simplified version that assumes independent readout errors
    # Full tensor product would be: C_total = C_0 ⊗ C_1 ⊗ ... ⊗ C_{n-1}
    
    # Convert counts to probability vector (sorted by bitstring)
    bitstrings = sorted(counts_clean.keys())
    measured_probs = np.array([counts_clean[bs] for bs in bitstrings], dtype=float)
    measured_probs = measured_probs / measured_probs.sum()
    
    # For independent readout errors, we can correct each qubit marginally
    # This is an approximation but much more tractable
    corrected_marginals = []
    
    for i in range(n_qubits):
        # Get measured marginal for this qubit
        marginal_counts = [0, 0]
        for bs, count in counts_clean.items():
            bit = int(bs[i])
            marginal_counts[bit] += count
        
        measured_marginal = np.array(marginal_counts, dtype=float)
        measured_marginal = measured_marginal / measured_marginal.sum()
        
        # Apply Tikhonov regularized inversion
        C = confusion_matrices[i]
        try:
            # Solve (C^T C + λI) x = C^T * measured_marginal
            A = C.T @ C + regularization * np.eye(2)
            b = C.T @ measured_marginal
            corrected_marginal = solve(A, b)
            
            # Ensure valid probabilities
            corrected_marginal = np.clip(corrected_marginal, 0.0, 1.0)
            corrected_marginal = corrected_marginal / corrected_marginal.sum()
            
        except np.linalg.LinAlgError:
            logger.warning(f"Matrix inversion failed for qubit {i}, using uncorrected marginal")
            corrected_marginal = measured_marginal
        
        corrected_marginals.append(corrected_marginal)
        logger.debug(f"Qubit {i}: {measured_marginal} → {corrected_marginal}")
    
    # Reconstruct corrected joint distribution (assuming independence)
    corrected_counts = {}
    for bs in bitstrings:
        prob = 1.0
        for i, bit_char in enumerate(bs):
            bit = int(bit_char)
            prob *= corrected_marginals[i][bit]
        corrected_counts[bs] = prob
    
    # Renormalize
    total_prob = sum(corrected_counts.values())
    corrected_counts = {bs: prob/total_prob for bs, prob in corrected_counts.items()}
    
    logger.info("Readout confusion correction completed")
    
    return corrected_counts


def ghz_aware_null_model(counts: Mapping[str, int],
                        n_qubits: int,
                        alpha: float = ALPHA) -> Dict[str, float]:
    """
    Create GHZ-state-aware null model for specialized hypothesis testing.
    
    Mathematical Motivation:
        For GHZ states, we expect enhanced probability on |00...0⟩ and |11...1⟩
        even under decoherence. A uniform null model might be too conservative.
        
        This null model preserves the |00...0⟩ ↔ |11...1⟩ symmetry while
        allowing uniform distribution over other outcomes.
        
    Research Usage:
        Alternative null model for GHZ state experiments. Provides more
        conservative baseline that accounts for expected GHZ structure.
        
    Args:
        counts: Observed measurement counts
        n_qubits: Number of qubits in system
        alpha: Jeffreys prior parameter
        
    Returns:
        Dict[str, float]: GHZ-aware null distribution
        
    Notes:
        This is an experimental feature. The standard factorized null
        model is recommended for most research applications.
    """
    counts_clean = validate_counts_dict(counts)
    
    if not counts_clean:
        raise ValueError("Empty counts dictionary")
    
    # Special treatment for |00...0⟩ and |11...1⟩ outcomes
    all_zeros = '0' * n_qubits
    all_ones = '1' * n_qubits
    
    # Count special outcomes
    special_count = counts_clean.get(all_zeros, 0) + counts_clean.get(all_ones, 0)
    
    # Count all other outcomes
    other_outcomes = []
    other_count = 0
    for bs, count in counts_clean.items():
        if bs not in [all_zeros, all_ones]:
            other_outcomes.append(bs)
            other_count += count
    
    total_count = sum(counts_clean.values())
    
    # Build GHZ-aware null: preserve |00...0⟩ ↔ |11...1⟩ ratio,
    # distribute remaining mass uniformly over other outcomes
    null_model = {}
    
    if special_count > 0:
        # Distribute special count equally between |00...0⟩ and |11...1⟩
        special_prob = (special_count + alpha) / (total_count + alpha * 2**n_qubits)
        null_model[all_zeros] = special_prob / 2
        null_model[all_ones] = special_prob / 2
    else:
        # If no special outcomes observed, give minimal probability
        minimal_prob = alpha / (total_count + alpha * 2**n_qubits)
        null_model[all_zeros] = minimal_prob
        null_model[all_ones] = minimal_prob
    
    # Distribute remaining probability uniformly over other outcomes
    remaining_prob = 1.0 - null_model[all_zeros] - null_model[all_ones]
    
    if other_outcomes:
        uniform_other_prob = remaining_prob / len(other_outcomes)
        for bs in other_outcomes:
            null_model[bs] = uniform_other_prob
    
    # Add any missing outcomes with minimal probability
    for i in range(2**n_qubits):
        bs = format(i, f'0{n_qubits}b')
        if bs not in null_model:
            null_model[bs] = alpha / (total_count + alpha * 2**n_qubits)
    
    # Renormalize
    total_prob = sum(null_model.values())
    null_model = {bs: prob/total_prob for bs, prob in null_model.items()}
    
    logger.info(f"Created GHZ-aware null model (special outcomes: {special_count}/{total_count})")
    
    return null_model