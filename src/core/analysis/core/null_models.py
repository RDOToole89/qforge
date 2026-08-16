"""Null models for baseline comparisons.

# Statistical Null Model Framework
This module provides baseline null models representing the expectation under
statistically independent qubit outcomes — no correlations between qubits.

# Mathematical Foundation
The primary null model is the factorized (independent) model:
Q(x₁,...,xₙ) = ∏ᵢ q(xᵢ)

where q(xᵢ) are marginal probabilities estimated from data with Jeffreys smoothing.
This models the case where all qubit outcomes are independent.

# Applications
Null models enable baseline comparisons:
- Structure Score: JSD(Observed || Factorized Null)
- Parametric Bootstrap: Generate synthetic data under the null model
- P-value Calculation: Compare observed metrics to the null distribution

# Advanced Features (Optional)
- Readout Confusion: Account for measurement errors
- Tikhonov Regularization: Numerical stability for matrix inversion
- State-Aware Nulls: Respect known initial state structure

References:
- Cover & Thomas (2006), "Elements of Information Theory"
- Tikhonov & Arsenin (1977), "Solutions of Ill-posed Problems"
- Nielsen & Chuang (2010), "Quantum Computation and Quantum Information"
"""

from __future__ import annotations

import logging
from collections.abc import Mapping

import numpy as np
import numpy.linalg as npl
from numpy.typing import NDArray

from ..constants import (
    ALPHA,
    DEFAULT_BOOTSTRAP_B,
    MAX_OUTCOMES_EXACT,
    TIKHONOV_LAMBDA,
    validate_counts_dict,
)

# Import canonical helpers from information_theory
from .information_theory import (
    all_bitstrings,
    marginal_distribution,
    n_qubits_from_counts,
)

logger = logging.getLogger(__name__)

# Type aliases for readability
Counts = Mapping[str, int]
Probs = dict[str, float]


def factorized_null_model(counts: Counts, alpha: float = ALPHA) -> Probs:
    """Create factorized (independent) null model from marginal distributions.

    Mathematical Definition:
        For n qubits, construct null model as:
        Q(x₁,...,xₙ) = ∏ᵢ q(xᵢ)

        where q(xᵢ) are marginal probabilities estimated from data:
        q(xᵢ = 0) = (count(xᵢ=0) + α) / (N + 2α)
        q(xᵢ = 1) = (count(xᵢ=1) + α) / (N + 2α)

    Physical Interpretation:
        This null model assumes all qubit outcomes are statistically
        independent. Any deviation from this model indicates correlations
        between qubits.

    Usage:
        Primary null model for Structure Score calculation:
        SS = JSD(Observed || Factorized_Null)

    Complexity:
        Enumerates the full 2^n support; for n ≳ 12 this can be memory-/time-heavy.

    Args:
        counts: Empirical measurement counts {bitstring: count}
        alpha: Jeffreys prior parameter for smoothing (default: 0.5)

    Returns:
        Dict[str, float]: Factorized null probabilities for all bitstrings
        in lexicographic order over full 2^n support.

    Examples:
        >>> counts = {"00": 250, "01": 250, "10": 250, "11": 250}
        >>> null = factorized_null_model(counts)
        >>> # Should return uniform distribution: each outcome = 0.25

    Raises:
        ValueError: If counts are invalid or inconsistent
    """
    counts_clean = validate_counts_dict(counts)
    n = n_qubits_from_counts(counts_clean)

    # soft guard for exponential blowup
    outcomes = 1 << n
    if outcomes > MAX_OUTCOMES_EXACT:
        logger.warning(
            "Factorized null expanding to %d outcomes (> MAX_OUTCOMES_EXACT=%d).",
            outcomes,
            MAX_OUTCOMES_EXACT,
        )

    # Per-qubit marginals with Jeffreys smoothing
    marginals: list[NDArray[np.float64]] = [
        marginal_distribution(counts_clean, i, alpha) for i in range(n)
    ]

    # Canonical lexicographic order over full support
    order = all_bitstrings(n)

    null_model: dict[str, float] = {}
    for bs in order:
        p = 1.0
        for i, b in enumerate(bs):
            p *= float(marginals[i][int(b)])
        null_model[bs] = p

    # Renormalize defensively
    Z = float(sum(null_model.values()))
    if not np.isfinite(Z) or Z <= 0.0:
        raise RuntimeError("Factorized null normalization failed (Z <= 0).")
    for k in null_model:
        null_model[k] /= Z

    logger.debug(f"Factorized null built on {2**n} outcomes (n={n}).")
    return null_model


def sample_multinomial_counts(
    probs: Mapping[str, float],
    N: int,
    rng: np.random.Generator,
    order: list[str] | None = None,
    drop_zeros: bool = True,
) -> dict[str, int]:
    """Sample one counts dict from Mult(N, probs) with a deterministic key order.

    - Uses lexicographically sorted keys by default for canonical ordering.
    - Renormalizes defensively if tiny numerical drift exists.
    """
    if N <= 0:
        raise ValueError(f"N must be positive, got {N}")

    keys = order if order is not None else sorted(probs.keys())
    pvec = np.asarray([float(probs.get(k, 0.0)) for k in keys], dtype=np.float64)

    s = float(pvec.sum())
    if not np.isfinite(s) or s <= 0.0:
        raise ValueError(f"Probability vector is invalid: sum={s}")
    if not np.isclose(s, 1.0, atol=1e-12):
        pvec = pvec / s  # renormalize defensively

    draws = rng.multinomial(N, pvec)
    if drop_zeros:
        return {keys[i]: int(c) for i, c in enumerate(draws) if c > 0}
    return {keys[i]: int(draws[i]) for i in range(len(keys))}


def generate_null_samples(
    null_model: dict[str, float],
    num_samples: int,
    rng: np.random.Generator,
) -> list[dict[str, int]]:
    """Return a single sampled dataset from the null model (wrapped in a list)."""
    if not null_model:
        raise ValueError("Empty null model")
    if num_samples <= 0:  # soft guard for negative samples
        raise ValueError(f"num_samples must be positive, got {num_samples}")
    order = sorted(null_model.keys())  # canonical lexicographic
    syn = sample_multinomial_counts(null_model, num_samples, rng, order=order)
    return [syn]


def parametric_bootstrap_null(
    observed_counts: Mapping[str, int],
    n_bootstrap: int = DEFAULT_BOOTSTRAP_B,
    rng: np.random.Generator | None = None,
) -> list[dict[str, int]]:
    """Perform parametric bootstrap under factorized null model.

    Mathematical Process:
        1. Estimate marginal distributions from observed data
        2. Construct factorized null model Q(x) = ∏ᵢ q(xᵢ)
        3. Generate B synthetic datasets from Q
        4. Return list of synthetic count dictionaries

    Application:
        This provides the synthetic data needed for:
        - Null distribution of Structure Score
        - P-value calculation: P(SS_null ≥ SS_observed)
        - Confidence intervals under the null model

    Note:
        Re-fitting the null model per bootstrap replicate (Q^(b)) for
        Structure Score should be done in the **metric implementation**,
        not here. This generator draws synthetic datasets from a fixed Q
        estimated on the observed data.

    Args:
        observed_counts: Original measurement counts
        n_bootstrap: Number of bootstrap samples to generate
        rng: Random generator (if None, creates new one)

    Returns:
        List[Dict[str, int]]: List of synthetic count datasets under null

    Examples:
        >>> counts = {"000": 200, "111": 300, "001": 100}
        >>> rng = np.random.default_rng(42)
        >>> null_samples = parametric_bootstrap_null(counts, 100, rng)
        >>> len(null_samples)  # Should be 100
    """
    if rng is None:
        rng = np.random.default_rng()

    counts_clean = validate_counts_dict(observed_counts)
    N = int(sum(counts_clean.values()))
    if N <= 0:
        raise ValueError("Observed counts have zero total shots.")

    # Build Q from observed, in canonical order
    Q = factorized_null_model(counts_clean)  # already canonical order

    # Generate B synthetic datasets
    out: list[dict[str, int]] = []
    for _ in range(n_bootstrap):
        syn = sample_multinomial_counts(Q, N, rng)
        out.append(syn)
    logger.info(f"Parametric bootstrap produced {len(out)} datasets (N={N}).")
    return out


def readout_confusion_model(
    counts: Mapping[str, int],
    confusion_matrices: list[NDArray[np.float64]],
    regularization: float = TIKHONOV_LAMBDA,
) -> dict[str, float]:
    """Apply readout confusion correction to measurement counts.

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

    Usage:
        Optional enhancement for null models when readout calibration data
        is available. Can improve accuracy of Structure Score calculations.

    Args:
        counts: Measured counts with readout errors
        confusion_matrices: Per-qubit confusion matrices (2×2 each)
        regularization: Tikhonov parameter for numerical stability

    Returns:
        Dict[str, float]: Corrected probability distribution

    Notes:
        This is an advanced feature. Most analyses can use the simpler
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
        if not np.allclose(C.sum(axis=1), 1.0, atol=1e-12):
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

        # Apply Tikhonov regularized inversion.
        # C is row-stochastic with C_ij = P(measure j | true i), so the forward
        # model is p_measured = C^T p_true. Recovering p_true means solving
        # C^T x = p_measured; the regularized normal equations are therefore
        # (C C^T + λI) x = C p_measured.
        C = confusion_matrices[i]
        A = C @ C.T + regularization * np.eye(2, dtype=float)
        b = C @ measured_marginal
        try:
            corrected_marginal = npl.solve(A, b)
        except npl.LinAlgError:
            logger.warning(f"Matrix inversion failed for qubit {i}, using uncorrected marginal")
            corrected_marginal = measured_marginal

        # Ensure valid probabilities
        corrected_marginal = np.clip(corrected_marginal, 0.0, 1.0)
        corrected_marginal = corrected_marginal / corrected_marginal.sum()

        corrected_marginals.append(corrected_marginal)
        logger.debug(f"Qubit {i}: {measured_marginal} → {corrected_marginal}")

    # Reconstruct corrected joint distribution (assuming independence)
    corrected_probs = {}
    for bs in bitstrings:
        prob = 1.0
        for i, bit_char in enumerate(bs):
            bit = int(bit_char)
            prob *= corrected_marginals[i][bit]
        corrected_probs[bs] = prob

    # Renormalize with robust guard
    total_prob = float(sum(corrected_probs.values()))
    if not np.isfinite(total_prob) or total_prob <= 0.0:
        raise RuntimeError("Readout correction produced invalid probabilities.")
    corrected_probs = {bs: prob / total_prob for bs, prob in corrected_probs.items()}

    logger.info("Readout confusion correction completed")

    return corrected_probs


def ghz_aware_null_model(
    counts: Mapping[str, int], n_qubits: int | None = None, alpha: float = ALPHA
) -> dict[str, float]:
    """Create GHZ-state-aware null model.

    Mathematical Motivation:
        For GHZ states, the ideal distribution concentrates probability on
        |00...0⟩ and |11...1⟩, and this remains partially true under
        decoherence. A uniform null model might be too conservative.

        This null model enforces equal probability for |00...0⟩ and |11...1⟩
        while distributing remaining mass uniformly over other outcomes.

    Usage:
        Alternative null model for GHZ state experiments. Provides a more
        conservative baseline that accounts for the ideal GHZ distribution.

    Args:
        counts: Observed measurement counts
        n_qubits: Number of qubits (optional, inferred from counts if not provided)
        alpha: Jeffreys prior parameter

    Returns:
        Dict[str, float]: GHZ-aware null distribution in lexicographic order

    Notes:
        This is an experimental feature. The standard factorized null
        model is recommended for most analyses.
    """
    counts_clean = validate_counts_dict(counts)

    logger.warning("Using experimental GHZ-aware null model.")

    # Infer n from counts
    n_infer = n_qubits_from_counts(counts_clean)
    if n_qubits is not None and n_qubits != n_infer:
        raise ValueError(f"n_qubits mismatch: {n_qubits} vs inferred {n_infer}")
    n = n_infer

    # soft guard for expansion
    outcomes = 1 << n
    if outcomes > MAX_OUTCOMES_EXACT:
        logger.warning(
            "GHZ-aware null expanding to %d outcomes (> MAX_OUTCOMES_EXACT=%d).",
            outcomes,
            MAX_OUTCOMES_EXACT,
        )

    order = all_bitstrings(n)

    # Two special outcomes
    all_zeros = "0" * n
    all_ones = "1" * n

    special_count = counts_clean.get(all_zeros, 0) + counts_clean.get(all_ones, 0)
    total_count = sum(counts_clean.values())

    null_model: dict[str, float] = {}

    if special_count > 0:
        special_prob = (special_count + alpha) / (total_count + alpha * (2**n))
        null_model[all_zeros] = special_prob / 2.0
        null_model[all_ones] = special_prob / 2.0
    else:
        minimal = alpha / (total_count + alpha * (2**n))
        null_model[all_zeros] = minimal
        null_model[all_ones] = minimal

    # Uniformly distribute remaining mass over ALL other outcomes on full support
    other_outcomes = [bs for bs in order if bs not in (all_zeros, all_ones)]
    remaining = 1.0 - (null_model[all_zeros] + null_model[all_ones])
    uniform_other = remaining / max(len(other_outcomes), 1)

    for bs in other_outcomes:
        null_model[bs] = uniform_other

    # Final renormalization/guard
    Z = float(sum(null_model.values()))
    if not np.isfinite(Z) or Z <= 0.0:
        raise RuntimeError("GHZ-aware null produced invalid normalization.")
    null_model = {bs: prob / Z for bs, prob in null_model.items()}

    logger.info(f"Created GHZ-aware null model (special outcomes: {special_count}/{total_count})")

    return null_model


# Public API exports
__all__ = [
    "factorized_null_model",
    "generate_null_samples",  # compatibility wrapper
    "parametric_bootstrap_null",
    "sample_multinomial_counts",
    "readout_confusion_model",
    "ghz_aware_null_model",
]

# Back-compat alias
factorized_null = factorized_null_model
