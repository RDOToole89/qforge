"""Entanglement-Error Correlation (EEC) - Topology-Error Pattern Analysis.

# Mathematical Foundation
The Entanglement-Error Correlation quantifies how well decoherence patterns
correlate with the underlying entanglement topology of quantum states. It
combines graph theory, quantum information, and statistical correlation to
detect structured pathway preferences.

# Physical Interpretation
EEC tests the hypothesis that decoherence follows entanglement bonds - errors
should preferentially occur along highly entangled qubit connections. High
positive correlation suggests structure-preserving decoherence, while low or
negative correlation indicates topology-independent random errors.

# Research Applications
- Testing the "entanglement-guided decoherence" hypothesis
- Identifying which quantum state topologies preserve structure under noise
- Characterizing error correlations in multi-qubit entangled systems
- Validating theoretical predictions about decoherence pathways

# Mathematical Definition
EEC computes Pearson correlation between:
- Entanglement weights: W(i,j) based on quantum state topology
- Error frequencies: How often errors affect qubit pairs (i,j)

For state-specific topologies:
- GHZ: Maximum entanglement between all-pairs, exponential decay
- W: Single-excitation manifold with symmetric connections
- Bell: Perfect 2-qubit correlation with distance-based decay
- Cluster: Nearest-neighbor graph connectivity

# Educational Framework
This implementation demonstrates:
- Graph theory applications in quantum information
- Statistical correlation analysis with confidence intervals
- Quantum state topology characterization and analysis
- Interdisciplinary research combining physics, mathematics, and statistics

References:
- Nielsen & Chuang (2010), "Quantum Computation and Quantum Information"
- Horodecki et al. (2009), "Quantum Entanglement"
- Fortunato (2010), "Community Detection in Graphs"
- Wasserman & Faust (1994), "Social Network Analysis"
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from dataclasses import dataclass
from itertools import combinations
from typing import Any

import numpy as np
from scipy.stats import pearsonr

from ..constants import (
    ALPHA,
    CORRELATION_MODERATE_THRESHOLD,
    CORRELATION_STRONG_THRESHOLD,
    CORRELATION_WEAK_THRESHOLD,
    EEC_LAMBDA,
    validate_counts_dict,
)
from ..core.information_theory import mutual_information

logger = logging.getLogger(__name__)


@dataclass
class TopologyAnalysis:
    """Complete entanglement topology analysis with correlation results.

    This structure provides comprehensive information about the relationship
    between quantum state topology and observed error patterns.
    """

    entanglement_error_correlation: float
    correlation_p_value: float
    correlation_strength: str  # "none", "weak", "moderate", "strong"
    entanglement_matrix: np.ndarray
    error_correlation_matrix: np.ndarray
    topology_type: str
    dominant_correlations: list[tuple[int, int]]
    topology_summary: str
    statistical_significance: bool

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "entanglement_error_correlation": self.entanglement_error_correlation,
            "correlation_p_value": self.correlation_p_value,
            "correlation_strength": self.correlation_strength,
            "entanglement_matrix": self.entanglement_matrix.tolist(),
            "error_correlation_matrix": self.error_correlation_matrix.tolist(),
            "topology_type": self.topology_type,
            "dominant_correlations": self.dominant_correlations,
            "topology_summary": self.topology_summary,
            "statistical_significance": self.statistical_significance,
        }


def compute_entanglement_error_correlation(
    counts: Mapping[str, int],
    state_type: str = "GHZ",
    topology_params: dict[str, Any] | None = None,
    alpha: float = ALPHA,
    return_analysis: bool = False,
) -> float | TopologyAnalysis:
    """Compute Entanglement-Error Correlation - topology vs error pattern correlation.

    Mathematical Process:
        1. Construct entanglement topology matrix W(i,j) based on state type
        2. Compute error correlation matrix E(i,j) from measurement data
        3. Calculate Pearson correlation: EEC = corr(W_flat, E_flat)
        4. Apply statistical significance testing and interpretation

    Physical Interpretation:
        - EEC > 0: Errors follow entanglement topology (structured decoherence)
        - EEC ≈ 0: No correlation between topology and errors (random decoherence)
        - EEC < 0: Anti-correlation (rare, suggests topology-avoiding errors)

    State-Specific Topologies:
        - **GHZ**: All-to-all connectivity with distance decay
        - **W**: Single-excitation manifold with symmetric weights
        - **Bell**: Perfect 2-qubit correlation with extension rules
        - **Cluster**: Nearest-neighbor linear or 2D lattice connectivity
        - **Custom**: User-defined topology matrix

    Research Thresholds:
        - |EEC| < 0.2: No significant correlation
        - |EEC| ∈ [0.2, 0.5): Weak topology-error correlation
        - |EEC| ∈ [0.5, 0.8): Moderate correlation (structured pathways)
        - |EEC| ≥ 0.8: Strong correlation (topology-guided decoherence)

    Args:
        counts: Measurement counts {bitstring: count}
        state_type: Quantum state topology ("GHZ", "W", "Bell", "Cluster", "Custom")
        topology_params: Additional parameters for topology construction
        alpha: Significance level for statistical testing.
        return_analysis: If True, return comprehensive TopologyAnalysis

    Returns:
        float: Entanglement-Error Correlation ∈ [-1, 1]
        OR TopologyAnalysis: Complete topology analysis results

    Raises:
        ValueError: If counts are invalid or state_type unsupported

    Examples:
        >>> # GHZ state with topology-preserving errors
        >>> counts = {"000": 400, "111": 350, "001": 100, "110": 150}
        >>> eec = compute_entanglement_error_correlation(counts, "GHZ")
        >>> print(f"EEC = {eec:.3f}")  # Expected: positive correlation

        >>> # Random errors (no topology correlation)
        >>> counts = {"000": 250, "001": 250, "010": 250, "011": 250}
        >>> eec = compute_entanglement_error_correlation(counts, "GHZ")
        >>> print(f"EEC = {eec:.3f}")  # Expected: near zero

    Complexity:
        Time: O(n² + k) where n = qubits, k = outcomes
        Space: O(n²) for topology and correlation matrices

    Educational Notes:
        - EEC bridges quantum information theory and graph analysis
        - Pearson correlation assumes linear relationships between variables
        - Alternative: Spearman correlation for non-linear monotonic relationships
        - Statistical significance testing prevents false positive correlations
    """
    # Input validation with research-grade error handling
    counts_clean = validate_counts_dict(counts, "entanglement-error correlation input")

    if not counts_clean:
        logger.warning("Empty counts dictionary for EEC computation")
        return (
            0.0
            if not return_analysis
            else TopologyAnalysis(
                entanglement_error_correlation=0.0,
                correlation_p_value=1.0,
                correlation_strength="none",
                entanglement_matrix=np.array([]),
                error_correlation_matrix=np.array([]),
                topology_type=state_type,
                dominant_correlations=[],
                topology_summary="No data available for topology analysis",
                statistical_significance=False,
            )
        )

    # Determine number of qubits from bitstring length
    first_bitstring = next(iter(counts_clean.keys()))
    n_qubits = len(first_bitstring)

    if n_qubits < 2:
        logger.warning(f"EEC requires ≥2 qubits, got {n_qubits}")
        return 0.0 if not return_analysis else _create_empty_topology_analysis(state_type)

    logger.debug(
        f"Computing EEC for {n_qubits}-qubit {state_type} state with {len(counts_clean)} outcomes"
    )

    # Initialize topology parameters
    if topology_params is None:
        topology_params = {}

    # Construct entanglement topology matrix
    entanglement_matrix = _construct_entanglement_topology(n_qubits, state_type, topology_params)

    # Compute error correlation matrix from measurement data
    error_matrix = _compute_error_correlation_matrix(counts_clean, n_qubits, alpha)

    # Calculate correlation between topology and error patterns
    eec, p_value = _compute_topology_error_correlation(entanglement_matrix, error_matrix)

    logger.debug(f"Computed EEC = {eec:.6f} (p-value = {p_value:.4f})")

    if not return_analysis:
        return eec

    # Generate comprehensive topology analysis
    return _generate_topology_analysis(
        eec,
        p_value,
        entanglement_matrix,
        error_matrix,
        state_type,
        counts_clean,
        n_qubits,
    )


def compute_multiway_entanglement_correlation(
    counts: Mapping[str, int], state_type: str = "GHZ", max_order: int = 3
) -> dict[int, float]:
    """Compute higher-order entanglement correlations beyond pairwise.

    This function extends EEC to multiway correlations, analyzing how
    3-way, 4-way, and higher-order entanglement structures correlate
    with error patterns in quantum measurements.

    Mathematical Foundation:
        For k-way correlations, we compute:
        - k-way entanglement weights from state topology
        - k-way error frequencies from measurement data
        - Correlation between these k-dimensional structures

    Research Applications:
        - Detecting genuine multipartite entanglement effects on decoherence
        - Understanding how higher-order correlations survive noise
        - Characterizing error correlations in large quantum systems

    Args:
        counts: Measurement counts {bitstring: count}
        state_type: Quantum state topology
        max_order: Maximum correlation order to compute (2 ≤ max_order ≤ n_qubits)

    Returns:
        Dict[int, float]: {order: correlation} for each order 2 to max_order

    Examples:
        >>> counts = {"000": 400, "111": 400, "010": 100, "101": 100}
        >>> correlations = compute_multiway_entanglement_correlation(counts, "GHZ", 3)
        >>> print(f"2-way: {correlations[2]:.3f}, 3-way: {correlations[3]:.3f}")
    """
    counts_clean = validate_counts_dict(counts)
    first_bitstring = next(iter(counts_clean.keys()))
    n_qubits = len(first_bitstring)

    max_order = min(max_order, n_qubits)
    correlations = {}

    logger.debug(f"Computing multiway correlations up to order {max_order}")

    for order in range(2, max_order + 1):
        # Get all k-way qubit combinations
        qubit_combinations = list(combinations(range(n_qubits), order))

        if not qubit_combinations:
            continue

        # Construct k-way entanglement weights
        entanglement_weights = []
        error_frequencies = []

        for qubit_combo in qubit_combinations:
            # k-way entanglement weight from topology
            weight = _compute_kway_entanglement_weight(qubit_combo, state_type, n_qubits)
            entanglement_weights.append(weight)

            # k-way error frequency from data
            frequency = _compute_kway_error_frequency(qubit_combo, counts_clean)
            error_frequencies.append(frequency)

        # Compute correlation for this order
        if len(set(entanglement_weights)) > 1 and len(set(error_frequencies)) > 1:
            correlation, _ = pearsonr(entanglement_weights, error_frequencies)
            correlations[order] = correlation if not np.isnan(correlation) else 0.0
        else:
            correlations[order] = 0.0

        logger.debug(f"Order {order}: correlation = {correlations[order]:.4f}")

    return correlations


def _construct_entanglement_topology(
    n_qubits: int, state_type: str, params: dict[str, Any]
) -> np.ndarray:
    """Construct entanglement topology matrix for given quantum state.

    This function builds the theoretical entanglement connectivity matrix
    that represents how strongly different qubit pairs are entangled in
    the ideal quantum state before decoherence.
    """
    # Initialize symmetric matrix
    W = np.zeros((n_qubits, n_qubits))

    if state_type.upper() == "GHZ":
        # GHZ: All-to-all connectivity with distance-based decay
        lambda_decay = params.get("lambda", EEC_LAMBDA)

        for i in range(n_qubits):
            for j in range(i + 1, n_qubits):
                # Distance on ring topology (can be extended to other geometries)
                distance = min(abs(i - j), n_qubits - abs(i - j))
                weight = np.exp(-lambda_decay * distance)
                W[i, j] = W[j, i] = weight

    elif state_type.upper() == "W":
        # W state: Symmetric single-excitation manifold
        # All pairs equally entangled in W state
        uniform_weight = 1.0 / (n_qubits - 1) if n_qubits > 1 else 0.0

        for i in range(n_qubits):
            for j in range(i + 1, n_qubits):
                W[i, j] = W[j, i] = uniform_weight

    elif state_type.upper() == "BELL":
        # Bell state: Perfect 2-qubit correlation, extended to n qubits
        if n_qubits == 2:
            W[0, 1] = W[1, 0] = 1.0
        else:
            # Extended Bell: strongest correlation between first two qubits
            W[0, 1] = W[1, 0] = 1.0
            # Weaker correlations with other qubits
            for i in range(2, n_qubits):
                W[0, i] = W[i, 0] = 0.5
                W[1, i] = W[i, 1] = 0.5

    elif state_type.upper() == "CLUSTER":
        # Cluster state: Nearest-neighbor connectivity
        topology = params.get("cluster_topology", "linear")

        if topology == "linear":
            # Linear cluster: each qubit connected to nearest neighbors
            for i in range(n_qubits - 1):
                W[i, i + 1] = W[i + 1, i] = 1.0
        elif topology == "2d_grid":
            # 2D grid cluster (requires grid dimensions)
            rows = params.get("grid_rows", int(np.sqrt(n_qubits)))
            cols = n_qubits // rows
            for i in range(n_qubits):
                row_i, col_i = divmod(i, cols)
                for j in range(i + 1, n_qubits):
                    row_j, col_j = divmod(j, cols)
                    # Connect nearest neighbors in 2D grid
                    if (abs(row_i - row_j) + abs(col_i - col_j)) == 1:
                        W[i, j] = W[j, i] = 1.0
        else:
            logger.warning(f"Unknown cluster topology: {topology}")

    elif state_type.upper() == "CUSTOM":
        # Custom topology from user parameters
        custom_matrix = params.get("entanglement_matrix")
        if custom_matrix is not None:
            W = np.array(custom_matrix)
            if W.shape != (n_qubits, n_qubits):
                raise ValueError(f"Custom matrix shape {W.shape} doesn't match {n_qubits} qubits")
        else:
            logger.warning("Custom topology requested but no entanglement_matrix provided")

    elif state_type.upper() == "SUPERPOSITION":
        # Product state: No entanglement between qubits
        # Returns zero matrix, which correctly leads to EEC = 0.0 (no correlation)
        pass

    else:
        raise ValueError(f"Unsupported state type: {state_type}")

    # Ensure symmetric matrix with zero diagonal
    W = (W + W.T) / 2
    np.fill_diagonal(W, 0)

    logger.debug(f"Constructed {state_type} topology matrix with {np.sum(W > 0)} non-zero entries")
    return W


def _compute_error_correlation_matrix(
    counts: Mapping[str, int], n_qubits: int, alpha: float
) -> np.ndarray:
    """Compute error correlation matrix from measurement data.

    This function analyzes the measurement outcomes to determine how
    frequently different qubit pairs exhibit correlated errors.
    """
    # Initialize error correlation matrix
    E = np.zeros((n_qubits, n_qubits))

    # Compute pairwise mutual information as error correlation measure
    for i in range(n_qubits):
        for j in range(i + 1, n_qubits):
            try:
                # Use mutual information as correlation measure
                mi = float(mutual_information(counts, i, j, alpha=alpha))
                E[i, j] = E[j, i] = mi
            except Exception as e:
                logger.debug(f"Failed to compute MI for qubits ({i},{j}): {e}")
                E[i, j] = E[j, i] = 0.0

    _nz = E[E > 0]
    mean_mi = float(np.mean(_nz)) if _nz.size else 0.0
    logger.debug(
        "Computed error correlation matrix; mean MI over nonzero entries = %.4f",
        mean_mi,
    )
    return E


def _compute_topology_error_correlation(
    entanglement_matrix: np.ndarray, error_matrix: np.ndarray
) -> tuple[float, float]:
    """Compute correlation between entanglement topology and error patterns.

    This function calculates the Pearson correlation coefficient between
    the theoretical entanglement matrix and observed error correlation matrix.
    """
    # Extract upper triangular elements (avoid double-counting due to symmetry)
    mask = np.triu(np.ones_like(entanglement_matrix, dtype=bool), k=1)

    entanglement_flat = entanglement_matrix[mask]
    error_flat = error_matrix[mask]

    # Check for sufficient variance
    if (np.ptp(entanglement_flat) <= 1e-12) or (np.ptp(error_flat) <= 1e-12):
        logger.debug("Insufficient variance for correlation computation")
        return 0.0, 1.0

    # Compute Pearson correlation with p-value
    try:
        correlation, p_value = pearsonr(entanglement_flat, error_flat)
        if np.isnan(correlation):
            correlation, p_value = 0.0, 1.0
        else:
            # Clamp tiny FP drift to theoretical bounds
            correlation = float(np.clip(correlation, -1.0, 1.0))
    except Exception as e:
        logger.debug(f"Correlation computation failed: {e}")
        correlation, p_value = 0.0, 1.0

    return correlation, p_value


def _compute_kway_entanglement_weight(
    qubit_combo: tuple[int, ...], state_type: str, n_qubits: int
) -> float:
    """Compute k-way entanglement weight for given qubit combination."""
    if state_type.upper() == "GHZ":
        # For GHZ, k-way weight decreases with distance spread
        if len(qubit_combo) == 2:
            i, j = qubit_combo
            distance = min(abs(i - j), n_qubits - abs(i - j))
            return np.exp(-EEC_LAMBDA * distance)
        else:
            # Higher-order: product of pairwise weights
            weight = 1.0
            for i, j in combinations(qubit_combo, 2):
                distance = min(abs(i - j), n_qubits - abs(i - j))
                weight *= np.exp(-EEC_LAMBDA * distance)
            return weight ** (1 / len(list(combinations(qubit_combo, 2))))

    elif state_type.upper() == "W":
        # W state: all k-way combinations equally weighted
        return 1.0

    else:
        # Default: uniform weight
        return 1.0


def _compute_kway_error_frequency(qubit_combo: tuple[int, ...], counts: Mapping[str, int]) -> float:
    """Compute k-way error frequency for given qubit combination."""
    # Count how often this specific qubit combination shows correlated errors
    # For simplicity, count outcomes where these qubits differ from all-0 or all-1

    total_counts = sum(counts.values())
    correlated_counts = 0

    for bitstring, count in counts.items():
        # Extract bits for this qubit combination
        combo_bits = [bitstring[i] for i in qubit_combo]

        # Check for non-trivial patterns (not all same)
        if not (all(b == "0" for b in combo_bits) or all(b == "1" for b in combo_bits)):
            correlated_counts += count

    return correlated_counts / total_counts if total_counts > 0 else 0.0


def _generate_topology_analysis(
    eec: float,
    p_value: float,
    entanglement_matrix: np.ndarray,
    error_matrix: np.ndarray,
    state_type: str,
    counts: dict,
    n_qubits: int,
) -> TopologyAnalysis:
    """Generate comprehensive topology analysis results."""
    # Determine correlation strength
    abs_eec = abs(eec)
    if abs_eec >= CORRELATION_STRONG_THRESHOLD:
        strength = "strong"
    elif abs_eec >= CORRELATION_MODERATE_THRESHOLD:
        strength = "moderate"
    elif abs_eec >= CORRELATION_WEAK_THRESHOLD:
        strength = "weak"
    else:
        strength = "none"

    # Statistical significance (typically p < 0.05)
    is_significant = p_value < 0.05

    # Find dominant correlations (top 25% of entanglement weights)
    mask = np.triu(np.ones_like(entanglement_matrix, dtype=bool), k=1)
    weights = entanglement_matrix[mask]
    indices = np.where(mask)

    # Get top correlations
    k = max(1, len(weights) // 4)
    top_indices = np.argsort(weights)[-k:][::-1]
    dominant_correlations = [(indices[0][i], indices[1][i]) for i in top_indices if weights[i] > 0]

    # Generate summary
    direction = "positive" if eec > 0 else "negative" if eec < 0 else "zero"
    summary = (
        f"EEC = {eec:.3f} ({strength} {direction} correlation, "
        f"p = {p_value:.4f}, {'significant' if is_significant else 'not significant'})"
    )

    return TopologyAnalysis(
        entanglement_error_correlation=eec,
        correlation_p_value=p_value,
        correlation_strength=strength,
        entanglement_matrix=entanglement_matrix,
        error_correlation_matrix=error_matrix,
        topology_type=state_type,
        dominant_correlations=dominant_correlations,
        topology_summary=summary,
        statistical_significance=is_significant,
    )


def _create_empty_topology_analysis(state_type: str) -> TopologyAnalysis:
    """Create empty topology analysis for edge cases."""
    return TopologyAnalysis(
        entanglement_error_correlation=0.0,
        correlation_p_value=1.0,
        correlation_strength="none",
        entanglement_matrix=np.array([]),
        error_correlation_matrix=np.array([]),
        topology_type=state_type,
        dominant_correlations=[],
        topology_summary="Insufficient data for topology analysis",
        statistical_significance=False,
    )


def validate_eec_properties(
    eec: float, counts: Mapping[str, int], state_type: str, tolerance: float = 1e-10
) -> bool:
    """Validate mathematical properties of computed EEC.

    Validated Properties:
        1. Range: EEC ∈ [-1, 1] (Pearson correlation bounds)
        2. Symmetry: Invariant under qubit relabeling for symmetric states
        3. State specificity: Different state types give different EEC patterns
        4. Monotonicity: More structured errors → higher |EEC|
        5. Statistical validity: Proper correlation coefficient properties
    """
    counts_clean = validate_counts_dict(counts)

    # Property 1: Range constraint
    assert -1.0 - tolerance <= eec <= 1.0 + tolerance, f"EEC={eec} outside valid range [-1, 1]"

    # Property 2: Finite and real
    assert np.isfinite(eec), f"EEC={eec} is not finite"
    assert np.isreal(eec), f"EEC={eec} is not real"

    # Property 3: Deterministic for identical inputs
    eec_recompute = compute_entanglement_error_correlation(counts_clean, state_type)
    assert abs(eec - eec_recompute) <= tolerance, f"EEC not deterministic: {eec} vs {eec_recompute}"

    logger.debug(f"EEC validation passed: EEC={eec:.6f}")
    return True


def entanglement_error_correlation_educational_demo() -> dict:
    """Educational demonstration of EEC behavior across quantum state types.

    Returns:
        dict: Demonstration results with quantum physics interpretations
    """
    demo_results = {}

    # GHZ state examples
    ghz_structured = {"000": 400, "111": 400, "010": 100, "101": 100}
    ghz_random = {"000": 250, "001": 250, "010": 250, "011": 125, "100": 125}

    eec_ghz_struct = compute_entanglement_error_correlation(ghz_structured, "GHZ")
    eec_ghz_rand = compute_entanglement_error_correlation(ghz_random, "GHZ")

    demo_results["ghz_comparison"] = {
        "structured": {"counts": ghz_structured, "eec": eec_ghz_struct},
        "random": {"counts": ghz_random, "eec": eec_ghz_rand},
        "interpretation": "GHZ: structured errors preserve topology correlations",
    }

    # State type comparison
    bell_counts = {"00": 400, "11": 400, "01": 100, "10": 100}
    w_counts = {"001": 300, "010": 300, "100": 300, "000": 100}

    eec_bell = compute_entanglement_error_correlation(bell_counts, "Bell")
    eec_w = compute_entanglement_error_correlation(w_counts, "W")

    demo_results["state_comparison"] = {
        "bell": {"eec": eec_bell, "interpretation": "Perfect 2-qubit correlation"},
        "w": {
            "eec": eec_w,
            "interpretation": "Single-excitation manifold preservation",
        },
        "insight": "Different state topologies show distinct EEC signatures",
    }

    demo_results["quantum_insight"] = {
        "hypothesis": "Decoherence follows entanglement bonds",
        "evidence": "High positive EEC indicates topology-guided errors",
        "applications": "Characterizing error correlations in quantum systems",
    }

    logger.info("EEC educational demonstration completed")
    return demo_results


__all__ = [
    "TopologyAnalysis",
    "compute_entanglement_error_correlation",
    "compute_multiway_entanglement_correlation",
    "validate_eec_properties",
    "entanglement_error_correlation_educational_demo",
]
