"""
Research Integration Module

Bridge between engine API and core structured decoherence analysis.
Provides clean integration for computing research metrics.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

# Canonical metrics registry + schema bridge (single source of truth)
from src.core.analysis.metrics.registry import compute_all
from src.core.analysis.metrics.schema_bridge import metrics_to_schema
from src.engine.models.config import ExperimentConfig
from src.engine.models.research import (
    AnalysisMetadata,
    PathwayAnalysis,
    StructuredDecoherenceMetrics,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Counts extraction
# ---------------------------------------------------------------------------


def extract_counts_from_result(raw_result: Any, *, num_qubits: int | None = None) -> dict[str, int]:
    """
    Extract measurement counts from Qiskit results and canonicalize.

    Canonicalization:
      - Remove spaces (Qiskit can space-separate classical registers)
      - If `num_qubits` is provided, left-pad to that width; if longer, keep the
        least-significant `num_qubits` bits (rightmost)
      - MSB-left bitstring order

    Args:
        raw_result: Qiskit Result or dict-like (may be {'counts': {...}} or {...})
        num_qubits: If provided, enforce fixed-length bitstrings (recommended)

    Returns:
        {bitstring: count} with MSB-left bitstrings.
    """
    try:
        # Qiskit Result
        if hasattr(raw_result, "get_counts"):
            try:
                counts_raw = raw_result.get_counts()
            except Exception:
                counts_raw = raw_result.get_counts(0)
        # Dict with explicit 'counts' field
        elif isinstance(raw_result, dict) and "counts" in raw_result:
            counts_raw = raw_result["counts"]
        # Plain dict of bitstring -> count
        elif isinstance(raw_result, dict):
            counts_raw = raw_result
        else:
            logger.error(f"Unsupported result format: {type(raw_result)}")
            return {}

        # Optional width inference if not provided
        if num_qubits is None:
            try:
                first_key = next(iter(counts_raw.keys()))
                num_qubits = len(str(first_key).replace(" ", ""))
            except Exception:
                pass

        clean_counts: dict[str, int] = {}
        for bitstring, count in counts_raw.items():
            key = str(bitstring).replace(" ", "")
            if num_qubits is not None:
                if len(key) < num_qubits:
                    key = key.rjust(num_qubits, "0")
                elif len(key) > num_qubits:
                    key = key[-num_qubits:]
            clean_counts[key] = int(count)

        return clean_counts
    except Exception as e:
        logger.error(f"Failed to extract counts from result: {e}")
        return {}


# ---------------------------------------------------------------------------
# Schema-first computation
# ---------------------------------------------------------------------------


def compute_research_schema(
    counts: dict[str, int],
    config: ExperimentConfig,
) -> dict[str, Any] | None:
    """
    Compute all registered metrics and return **schema v1** output.

    This is the preferred integration point for engine → analysis now that
    the registry and schema bridge are in place.

    Args:
        counts: Canonical measurement counts {bitstring: count}
        config: Experiment configuration

    Returns:
        Dict compliant with schema v1, or None if disabled / invalid
    """
    if not config.enable_research_metrics:
        return None

    if config.research_type not in (None, "structured_decoherence"):
        logger.warning(
            f"Research type '{config.research_type}' not supported for structured decoherence metrics"
        )
        return None

    if not counts:
        logger.warning("No measurement counts available for research metrics")
        return None

    # Compute through the registry (single source of truth).
    # Pass state_type if your registry uses it; otherwise it will ignore extras.
    results = compute_all(counts=counts, state_type=config.state_type)
    schema = metrics_to_schema(results)
    return schema


# ---------------------------------------------------------------------------
# Typed engine models (StructuredDecoherenceMetrics)
# ---------------------------------------------------------------------------


def compute_research_metrics(
    counts: dict[str, int], config: ExperimentConfig
) -> StructuredDecoherenceMetrics | None:
    """
    Compute structured decoherence metrics and return *typed* engine models.

    This wrapper builds your existing `StructuredDecoherenceMetrics` using values
    from the registry/schema so results stay consistent across the codebase.

    Prefer `compute_research_schema()` if your downstream accepts schema_v1 directly.
    """
    schema = compute_research_schema(counts, config)
    if schema is None:
        return None

    # Helper to pull a numeric `value` from a metric block
    def _val(name: str, default: float = 0.0) -> float:
        block = schema.get(name)
        if isinstance(block, dict):
            try:
                return float(block.get("value", default))
            except Exception:
                return default
        return default

    # Pull canonical metrics; fallbacks keep older semantics intact.
    ai_schema = _val("asymmetry_index", None)  # may not exist in all schemas
    ss = _val("structure_score", 0.0)
    ai = ai_schema if ai_schema is not None else ss  # fallback: AI≈SS

    eec = _val("entanglement_error_correlation", 0.0)
    ci = _val("concentration_index", 1.0)
    tc = _val("total_correlation", 0.0)

    # Optional / nullable
    tps_block = schema.get("pathway_persistence") or schema.get("temporal_pathway_stability")
    ces_block = schema.get("complexity_emergence_score")
    tps = (
        float(tps_block.get("value"))
        if isinstance(tps_block, dict) and "value" in tps_block
        else None
    )
    ces = (
        float(ces_block.get("value"))
        if isinstance(ces_block, dict) and "value" in ces_block
        else None
    )

    # If the schema exposes PCR explicitly, you can read it; otherwise map from CI
    pcr_block = schema.get("pathway_concentration_ratio")
    if isinstance(pcr_block, dict) and "value" in pcr_block:
        pcr = float(pcr_block["value"])
    else:
        pcr = ci  # proxy

    # Build metadata
    total_shots = sum(counts.values())
    unique_outcomes = len(counts)
    metadata = AnalysisMetadata(
        state_type=config.state_type,
        num_qubits=config.num_qubits,
        total_shots=total_shots,
        unique_outcomes=unique_outcomes,
        analysis_timestamp=datetime.now().isoformat(),
        noise_conditions=_extract_noise_conditions(config),
    )

    pathway_analysis = _create_pathway_analysis(counts, ai, pcr, eec)

    metrics = StructuredDecoherenceMetrics(
        asymmetry_index=ai,
        pathway_concentration_ratio=pcr,
        entanglement_error_correlation=eec,
        temporal_pathway_stability=tps,
        complexity_emergence_score=ces,
        structure_score=ss,
        concentration_index=ci,
        total_correlation=tc,
        metadata=metadata,
        pathway_analysis=pathway_analysis,
    )

    logger.info(
        "Research metrics (schema-aligned): "
        f"AI/SS={ai:.4f}, PCR/CI={pcr:.4f}/{ci:.4f}, EEC={eec:.4f}, TC={tc:.4f}"
    )
    return metrics


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------


def _extract_noise_conditions(config: ExperimentConfig) -> dict[str, Any] | None:
    """Extract noise conditions from config for metadata."""
    if not getattr(config, "noise_enabled", False):
        return None

    conditions = {
        "noise_type": getattr(config, "noise_type", None),
        "error_rate": getattr(config, "error_rate", None),
    }

    # Add additional noise parameters if present
    if getattr(config, "z_prob", None) is not None:
        conditions["z_prob"] = config.z_prob
    if getattr(config, "i_prob", None) is not None:
        conditions["i_prob"] = config.i_prob
    if getattr(config, "t1", None) is not None:
        conditions["t1"] = config.t1
    if getattr(config, "t2", None) is not None:
        conditions["t2"] = config.t2

    return conditions


def _create_pathway_analysis(
    counts: dict[str, int], ai: float, pcr: float, eec: float
) -> PathwayAnalysis:
    """Create human-readable pathway analysis."""
    total_shots = max(1, sum(counts.values()))

    # Dominant pathways as (bitstring, probability) tuples
    sorted_outcomes = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    dominant_pathways = [
        (bitstring, count / total_shots) for bitstring, count in sorted_outcomes[:5]
    ]

    # Qualitative tiers
    if pcr > 5.0:
        pathway_concentration = "very_high"
    elif pcr > 2.0:
        pathway_concentration = "high"
    elif pcr > 1.5:
        pathway_concentration = "moderate"
    elif pcr > 1.1:
        pathway_concentration = "low"
    else:
        pathway_concentration = "very_low"

    if ai > 1.0:
        asymmetry_level = "high_asymmetry"
    elif ai > 0.5:
        asymmetry_level = "moderate_asymmetry"
    elif ai > 0.2:
        asymmetry_level = "slight_asymmetry"
    else:
        asymmetry_level = "very_uniform"

    abs_eec = abs(eec)
    if abs_eec > 0.5:
        entanglement_influence = "strong_correlation"
    elif abs_eec > 0.2:
        entanglement_influence = "moderate_correlation"
    elif abs_eec > 0.05:
        entanglement_influence = "weak_correlation"
    else:
        entanglement_influence = "no_correlation"

    return PathwayAnalysis(
        dominant_pathways=dominant_pathways,
        pathway_concentration=pathway_concentration,
        asymmetry_level=asymmetry_level,
        entanglement_influence=entanglement_influence,
        total_outcomes=len(counts),
        measurement_shots=sum(counts.values()),
    )
