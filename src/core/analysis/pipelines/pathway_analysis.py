"""Pathway Analysis Pipeline - Orchestration and Convenience Functions.

This module provides high-level orchestration for the distribution-structure
metrics, keeping the core modules focused and avoiding tight coupling.

Usage:
    from src.core.analysis.pipelines.pathway_analysis import run_all_to_schema

    schema_result = run_all_to_schema(counts=measurement_data, rng=rng)
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from datetime import UTC
from typing import Any, cast

import numpy as np

from ..metrics.asymmetry_index import compute_asymmetry_index
from ..metrics.complexity_emergence_score import compute_complexity_emergence_score
from ..metrics.entanglement_error_correlation import (
    compute_entanglement_error_correlation,
)
from ..metrics.pathway_concentration_ratio import compute_pathway_concentration_ratio
from ..metrics.registry import compute_all
from ..metrics.schema_bridge import metrics_to_schema
from ..metrics.temporal_pathway_stability import compute_temporal_pathway_stability

logger = logging.getLogger(__name__)


def run_all_to_schema(
    counts: Mapping[str, int],
    rng: np.random.Generator | None = None,
    **kwargs: Any,
) -> dict:
    """Convenience pipeline: compute all registered metrics and convert to schema.

    Forward any extra kwargs (e.g., state_type, alpha, B) to the registry metrics.
    """
    results = compute_all(counts=counts, rng=rng, **kwargs)
    return metrics_to_schema(results)


def compute_all_pathway_metrics(
    counts: dict[str, int],
    state_type: str = "GHZ",
    num_qubits: int | None = None,
    historical_data: list[dict[str, int]] | None = None,
    multi_qubit_data: dict[int, dict[str, int]] | None = None,
) -> dict[str, Any]:
    """Compute all 5 pathway metrics.

    This is the main function for outcome-distribution analysis, computing
    all metrics that characterize non-uniformity, concentration, and
    correlation structure in the measurement data.

    Args:
        counts: Current measurement outcomes (bitstring -> count)
        state_type: Quantum state type ("GHZ", "W", "BELL", "CLUSTER")
        num_qubits: Number of qubits (auto-detected if None)
        historical_data: Previous measurement data for TPS calculation
        multi_qubit_data: Data across different qubit counts for CES calculation

    Returns:
        Dictionary containing all 5 pathway metrics plus analysis summary
    """
    if not counts:
        logger.warning("Empty counts provided for pathway analysis")
        return {}

    # Sanity: ensure all bitstrings have the same length
    bit_lens = {len(b) for b in counts.keys()}
    if len(bit_lens) > 1:
        logger.warning("Inconsistent bitstring lengths detected; using the most common length")
        # Keep only outcomes with the modal bit-length for downstream interpretation
        modal_len = max(
            ((L, sum(1 for b in counts if len(b) == L)) for L in bit_lens),
            key=lambda x: x[1],
        )[0]
        counts = {b: c for b, c in counts.items() if len(b) == modal_len}

    # Auto-detect number of qubits
    if num_qubits is None:
        first_bitstring = next(iter(counts.keys()))
        num_qubits = len(first_bitstring)

    logger.info(f"Computing pathway metrics for {num_qubits}-qubit {state_type} state")

    # Compute core metrics (return_analysis defaults to False -> plain floats)
    ai = compute_asymmetry_index(counts)
    pcr = compute_pathway_concentration_ratio(counts)
    eec = compute_entanglement_error_correlation(counts, state_type)

    metrics: dict[str, Any] = {
        "asymmetry_index": float(ai),
        "pathway_concentration_ratio": float(pcr) if np.isfinite(pcr) else float("inf"),
        "entanglement_error_correlation": float(np.clip(eec, -1.0, 1.0)),
    }

    # Compute temporal stability if historical data available
    if historical_data:
        pathway_rankings = _extract_pathway_rankings([counts] + historical_data)
        metrics["temporal_pathway_stability"] = compute_temporal_pathway_stability(pathway_rankings)
    else:
        metrics["temporal_pathway_stability"] = None
        logger.debug("No historical data provided - TPS not computed")

    # Compute complexity emergence if multi-qubit data available
    if multi_qubit_data:
        metrics["complexity_emergence_score"] = compute_complexity_emergence_score(
            cast("dict[int, Mapping[str, int]]", multi_qubit_data)
        )
    else:
        metrics["complexity_emergence_score"] = None
        logger.debug("No multi-qubit data provided - CES not computed")

    # Add metadata
    metrics["metadata"] = {
        "state_type": state_type,
        "num_qubits": num_qubits,
        "total_shots": int(sum(counts.values())),
        "unique_outcomes": int(len(counts)),
        "analysis_timestamp": _get_timestamp(),
    }

    # Generate pathway analysis summary
    metrics["pathway_analysis"] = _generate_pathway_summary(metrics, counts, state_type)

    logger.info(
        "Completed pathway analysis: AI=%.3f, PCR=%s, EEC=%.3f",
        metrics["asymmetry_index"],
        (
            "∞"
            if not np.isfinite(metrics["pathway_concentration_ratio"])
            else f"{metrics['pathway_concentration_ratio']:.3f}"
        ),
        metrics["entanglement_error_correlation"],
    )

    return metrics


def analyze_decoherence_structure(
    counts: dict[str, int],
    state_type: str = "GHZ",
    confidence_threshold: float = 0.7,
) -> dict[str, Any]:
    """High-level analysis of decoherence structure with interpretation.

    Provides structured analysis of whether the decoherence exhibits
    statistically significant structured patterns vs. random behavior.

    Args:
        counts: Measurement outcomes
        state_type: Quantum state type
        confidence_threshold: Threshold for detecting structured behavior

    Returns:
        Analysis results with structured/random classification
    """
    # Compute pathway metrics
    metrics = compute_all_pathway_metrics(counts, state_type)

    # Extract key indicators
    ai = float(metrics.get("asymmetry_index", 0.0))
    pcr = metrics.get("pathway_concentration_ratio", 1.0)
    eec = float(metrics.get("entanglement_error_correlation", 0.0))

    # Determine if decoherence appears structured
    structure_indicators: list[str] = []

    # High asymmetry suggests non-uniform patterns
    if ai > 0.3:
        structure_indicators.append("high_asymmetry")

    # High concentration suggests pathway preferences
    if np.isfinite(pcr) and pcr > 2.0:
        structure_indicators.append("pathway_concentration")
    elif not np.isfinite(pcr):
        structure_indicators.append("pathway_concentration_extreme")

    # Strong correlation suggests topology influence
    if abs(eec) > 0.5:
        structure_indicators.append("topology_correlation")

    # Calculate overall structure score (bounded ~[0,1.6], clamped to [0,1])
    structure_score = 0.0
    if ai > 0.2:
        structure_score += 0.4 * min(ai, 1.0)
    if np.isfinite(pcr) and pcr > 1.5:
        structure_score += 0.3 * min(pcr / 5.0, 1.0)
    elif not np.isfinite(pcr):
        structure_score += 0.3  # saturate the PCR contribution on ∞
    if abs(eec) > 0.3:
        structure_score += 0.3 * min(abs(eec), 1.0)
    structure_score = float(np.clip(structure_score, 0.0, 1.0))

    # Classification
    is_structured = structure_score > confidence_threshold
    confidence = structure_score

    analysis = {
        "classification": "structured" if is_structured else "random",
        "confidence": confidence,
        "structure_score": structure_score,
        "indicators": structure_indicators,
        "metrics": metrics,
        "interpretation": _generate_interpretation(metrics, is_structured, structure_indicators),
    }

    logger.info(
        "Decoherence analysis: %s (confidence: %.3f)",
        analysis["classification"],
        confidence,
    )

    return analysis


def _extract_pathway_rankings(data_sequence: list[dict[str, int]]) -> list[list[str]]:
    """Extract pathway rankings from sequence of measurement data."""
    rankings: list[list[str]] = []
    for counts in data_sequence:
        # Sort bitstrings by frequency (most frequent first)
        sorted_outcomes = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        ranking = [bitstring for bitstring, _ in sorted_outcomes]
        rankings.append(ranking)
    return rankings


def _generate_pathway_summary(
    metrics: dict[str, Any],
    counts: dict[str, int],
    state_type: str,
) -> dict[str, Any]:
    """Generate human-readable pathway analysis summary."""
    total_shots = sum(counts.values()) or 1  # avoid div-by-zero

    # Find most frequent pathways
    sorted_outcomes = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    top_pathways = sorted_outcomes[: min(5, len(sorted_outcomes))]

    # Calculate pathway probabilities
    pathway_probs = [(bitstring, count / total_shots) for bitstring, count in top_pathways]

    # Friendly PCR string
    pcr = metrics["pathway_concentration_ratio"]
    if np.isfinite(pcr):
        pcr_str = f"{pcr:.1f}×"
    else:
        pcr_str = "∞×"

    summary = {
        "dominant_pathways": pathway_probs,
        "pathway_concentration": f"Top 25% pathways contain {pcr_str} more events than bottom 25%",
        "asymmetry_level": _classify_asymmetry(metrics["asymmetry_index"]),
        "entanglement_influence": _classify_correlation(metrics["entanglement_error_correlation"]),
        "state_type": state_type,
        "total_outcomes": len(counts),
        "measurement_shots": int(total_shots),
    }

    return summary


def _classify_asymmetry(ai: float) -> str:
    """Classify asymmetry level."""
    if ai < 0.1:
        return "very_uniform"
    elif ai < 0.3:
        return "slight_asymmetry"
    elif ai < 0.6:
        return "moderate_asymmetry"
    else:
        return "high_asymmetry"


def _classify_correlation(eec: float) -> str:
    """Classify entanglement-error correlation."""
    abs_eec = abs(eec)
    if abs_eec < 0.2:
        return "no_correlation"
    elif abs_eec < 0.5:
        return "weak_correlation"
    elif abs_eec < 0.8:
        return "moderate_correlation"
    else:
        return "strong_correlation"


def _generate_interpretation(
    metrics: dict[str, Any],
    is_structured: bool,
    indicators: list[str],
) -> str:
    """Generate natural language interpretation of results."""
    if is_structured:
        interpretation = "Analysis indicates a STRUCTURED (non-uniform) error distribution. "

        if "high_asymmetry" in indicators:
            interpretation += (
                "Error distribution shows significant deviation from uniform randomness. "
            )

        if "pathway_concentration" in indicators or "pathway_concentration_extreme" in indicators:
            interpretation += "Errors are concentrated in preferred pathways. "

        if "topology_correlation" in indicators:
            interpretation += "Error patterns correlate with entanglement topology. "

        interpretation += "The error distribution deviates measurably from a random baseline."
    else:
        interpretation = "Analysis indicates RANDOM decoherence patterns. "
        interpretation += "Error distribution appears consistent with stochastic decoherence. "
        interpretation += "No clear evidence of structured pathway preferences detected."

    return interpretation


def _get_timestamp() -> str:
    """Get current timestamp (timezone-aware) for analysis metadata."""
    from datetime import datetime

    return datetime.now(UTC).isoformat()


__all__ = (
    "run_all_to_schema",
    "compute_all_pathway_metrics",
    "analyze_decoherence_structure",
)
