"""
Information theory metrics for quantum state analysis.

This module provides information-theoretic measures for analyzing quantum
experiments, including entropy, mutual information, and divergence metrics
critical for structured decoherence research.
"""

import numpy as np
import logging
from typing import Dict, Any, List, Tuple, Optional
from scipy.stats import entropy as scipy_entropy
from collections import Counter

logger = logging.getLogger("QuantumExperiment.Analysis.InformationTheory")


def compute_shannon_entropy(counts: Dict[str, int], normalize: bool = True) -> float:
    """
    Compute Shannon entropy of a probability distribution from measurement counts.

    Shannon entropy quantifies the randomness/uncertainty in the measurement outcomes.
    For a perfectly random distribution, entropy is maximized. For structured outcomes,
    entropy is reduced.

    Args:
        counts: Dictionary of measurement outcomes (bitstrings) to count frequencies
        normalize: Whether to normalize entropy by log(num_states) for comparison

    Returns:
        Shannon entropy H(X) = -Σ p(x) log₂(p(x))
        If normalize=True, returns H(X)/log₂(N) where N is number of possible states
    """
    if not counts:
        logger.warning("Empty counts dictionary provided to Shannon entropy")
        return 0.0

    # Convert to probability distribution
    total_shots = sum(counts.values())
    if total_shots == 0:
        return 0.0

    probabilities = [count / total_shots for count in counts.values()]

    # Compute Shannon entropy using scipy (base 2)
    entropy = scipy_entropy(probabilities, base=2)

    if normalize:
        # Normalize by maximum possible entropy
        num_states = len(counts)
        max_entropy = np.log2(num_states) if num_states > 1 else 1
        entropy = entropy / max_entropy if max_entropy > 0 else 0

    # Shannon entropy computed successfully
    return float(entropy)


def compute_kl_divergence(observed_counts: Dict[str, int],
                         ideal_counts: Dict[str, int]) -> float:
    """
    Compute Kullback-Leibler divergence between observed and ideal distributions.

    KL divergence measures how much the observed distribution differs from the
    ideal/theoretical distribution. For structured decoherence research, this
    quantifies deviation from expected quantum behavior.

    Args:
        observed_counts: Actual measurement outcomes
        ideal_counts: Expected/theoretical measurement outcomes

    Returns:
        KL divergence D_KL(P||Q) = Σ p(x) log(p(x)/q(x))
    """
    if not observed_counts or not ideal_counts:
        logger.warning("Empty counts provided to KL divergence")
        return float('inf')

    # Ensure both distributions have the same support
    all_outcomes = set(observed_counts.keys()) | set(ideal_counts.keys())

    # Convert to probability distributions with smoothing
    total_observed = sum(observed_counts.values())
    total_ideal = sum(ideal_counts.values())

    if total_observed == 0 or total_ideal == 0:
        return float('inf')

    # Add small epsilon to avoid log(0)
    epsilon = 1e-10

    p_probs = []  # observed
    q_probs = []  # ideal

    for outcome in all_outcomes:
        p = (observed_counts.get(outcome, 0) + epsilon) / (total_observed + len(all_outcomes) * epsilon)
        q = (ideal_counts.get(outcome, 0) + epsilon) / (total_ideal + len(all_outcomes) * epsilon)
        p_probs.append(p)
        q_probs.append(q)

    # Compute KL divergence
    kl_div = sum(p * np.log(p / q) for p, q in zip(p_probs, q_probs))

    # KL divergence computed successfully
    return float(kl_div)


def compute_total_variation_distance(observed_counts: Dict[str, int],
                                   ideal_counts: Dict[str, int]) -> float:
    """
    Compute Total Variation distance between two probability distributions.

    TV distance measures the maximum difference between probabilities of any event.
    It's bounded between 0 (identical distributions) and 1 (completely different).

    Args:
        observed_counts: Actual measurement outcomes
        ideal_counts: Expected measurement outcomes

    Returns:
        Total variation distance TV(P,Q) = (1/2) * Σ |p(x) - q(x)|
    """
    if not observed_counts or not ideal_counts:
        return 1.0  # Maximum distance for empty/invalid inputs

    # Get all possible outcomes
    all_outcomes = set(observed_counts.keys()) | set(ideal_counts.keys())

    # Convert to probabilities
    total_observed = sum(observed_counts.values())
    total_ideal = sum(ideal_counts.values())

    if total_observed == 0 or total_ideal == 0:
        return 1.0

    # Compute total variation distance
    tv_distance = 0.0
    for outcome in all_outcomes:
        p = observed_counts.get(outcome, 0) / total_observed
        q = ideal_counts.get(outcome, 0) / total_ideal
        tv_distance += abs(p - q)

    tv_distance *= 0.5  # Factor of 1/2 in TV distance definition

    # Total variation distance computed successfully
    return float(tv_distance)


def compute_mutual_information(counts: Dict[str, int],
                              qubit_a: int,
                              qubit_b: int) -> float:
    """
    Compute mutual information between two qubits from measurement outcomes.

    Mutual information quantifies the amount of information shared between
    two qubits. For entangled states, MI should be high; for separable states,
    MI should be low.

    Args:
        counts: Measurement outcomes as bitstring counts
        qubit_a: Index of first qubit (0-indexed)
        qubit_b: Index of second qubit (0-indexed)

    Returns:
        Mutual information I(A;B) = H(A) + H(B) - H(A,B)
    """
    if not counts:
        return 0.0

    total_shots = sum(counts.values())
    if total_shots == 0:
        return 0.0

    # Extract individual qubit measurements
    qubit_a_counts = {'0': 0, '1': 0}
    qubit_b_counts = {'0': 0, '1': 0}
    joint_counts = {'00': 0, '01': 0, '10': 0, '11': 0}

    for bitstring, count in counts.items():
        if len(bitstring) > max(qubit_a, qubit_b):
            bit_a = bitstring[qubit_a]
            bit_b = bitstring[qubit_b]

            qubit_a_counts[bit_a] += count
            qubit_b_counts[bit_b] += count
            joint_counts[bit_a + bit_b] += count

    # Compute individual entropies
    h_a = compute_shannon_entropy(qubit_a_counts, normalize=False)
    h_b = compute_shannon_entropy(qubit_b_counts, normalize=False)
    h_ab = compute_shannon_entropy(joint_counts, normalize=False)

    # Mutual information
    mi = h_a + h_b - h_ab

            # Mutual information computed for qubit pair
    return float(mi)


def compute_qubit_wise_bias(counts: Dict[str, int], num_qubits: int) -> Dict[str, float]:
    """
    Compute bias toward |0⟩ or |1⟩ for each qubit individually.

    This helps identify if certain qubits preferentially collapse to specific
    states during decoherence, revealing asymmetric noise effects.

    Args:
        counts: Measurement outcomes as bitstring counts
        num_qubits: Number of qubits in the system

    Returns:
        Dictionary mapping qubit index to bias (-1 to +1)
        Bias = (P(|1⟩) - P(|0⟩)) where:
        - Bias > 0: favors |1⟩
        - Bias < 0: favors |0⟩
        - Bias = 0: unbiased
    """
    if not counts or num_qubits <= 0:
        return {}

    # Initialize counters for each qubit
    qubit_counts = {}
    for i in range(num_qubits):
        qubit_counts[f'q{i}'] = {'0': 0, '1': 0}

    total_shots = sum(counts.values())
    if total_shots == 0:
        return {f'q{i}': 0.0 for i in range(num_qubits)}

    # Count outcomes for each qubit
    for bitstring, count in counts.items():
        if len(bitstring) == num_qubits:
            for i, bit in enumerate(bitstring):
                if bit in ['0', '1']:
                    qubit_counts[f'q{i}'][bit] += count

    # Compute bias for each qubit
    biases = {}
    for i in range(num_qubits):
        qubit_key = f'q{i}'
        zeros = qubit_counts[qubit_key]['0']
        ones = qubit_counts[qubit_key]['1']
        total = zeros + ones

        if total > 0:
            p_zero = zeros / total
            p_one = ones / total
            bias = p_one - p_zero  # Range: [-1, +1]
            biases[qubit_key] = bias
        else:
            biases[qubit_key] = 0.0

    # Qubit-wise biases computed successfully
    return biases


def compute_research_metrics(counts: Dict[str, int],
                           ideal_counts: Optional[Dict[str, int]] = None,
                           num_qubits: Optional[int] = None) -> Dict[str, Any]:
    """
    Compute comprehensive research-grade metrics for structured decoherence analysis.

    This is the main function for your GHZ structured decoherence research,
    computing all the metrics needed for pattern detection and statistical analysis.

    Args:
        counts: Observed measurement outcomes
        ideal_counts: Expected/theoretical outcomes (for comparisons)
        num_qubits: Number of qubits (auto-detected if None)

    Returns:
        Comprehensive dictionary of research metrics
    """
    if not counts:
        logger.warning("Empty counts provided to research metrics")
        return {}

    # Auto-detect number of qubits if not provided
    if num_qubits is None and counts:
        first_bitstring = next(iter(counts.keys()))
        num_qubits = len(first_bitstring)

    metrics = {
        'basic_stats': {
            'total_shots': sum(counts.values()),
            'unique_outcomes': len(counts),
            'num_qubits': num_qubits
        },
        'information_theory': {
            'shannon_entropy': compute_shannon_entropy(counts, normalize=False),
            'normalized_entropy': compute_shannon_entropy(counts, normalize=True),
        },
        'qubit_analysis': {
            'qubit_wise_bias': compute_qubit_wise_bias(counts, num_qubits) if num_qubits else {}
        }
    }

    # Add comparative metrics if ideal distribution provided
    if ideal_counts:
        metrics['distribution_comparison'] = {
            'kl_divergence': compute_kl_divergence(counts, ideal_counts),
            'total_variation_distance': compute_total_variation_distance(counts, ideal_counts)
        }

    # Add mutual information for small systems
    if num_qubits and num_qubits <= 4:  # Avoid exponential blowup
        mi_matrix = {}
        for i in range(num_qubits):
            for j in range(i + 1, num_qubits):
                mi_matrix[f'I({i};{j})'] = compute_mutual_information(counts, i, j)
        metrics['entanglement_analysis'] = {
            'mutual_information_matrix': mi_matrix
        }

    logger.info(f"Computed research metrics for {num_qubits}-qubit system")
    return metrics
