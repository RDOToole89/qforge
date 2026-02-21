"""
Research Integration Module

Bridge between engine API and core analysis metrics.
Provides clean integration for computing a generic MetricsBundle.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from src.core.analysis.metrics.profiles import resolve_metrics
from src.core.analysis.metrics.registry import compute_all
from src.engine.models.config import ExperimentConfig
from src.engine.models.research import (
    AnalysisMetadata,
    MetricEntry,
    MetricsBundle,
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
# Generic metrics computation
# ---------------------------------------------------------------------------


def compute_metrics_bundle(
    counts: dict[str, int],
    config: ExperimentConfig,
) -> MetricsBundle | None:
    """
    Compute requested metrics and return a typed MetricsBundle.

    Uses config.metrics (profile name, explicit list, or None) to decide
    which metrics to compute via the core registry.

    Args:
        counts: Canonical measurement counts {bitstring: count}
        config: Experiment configuration (reads .metrics, .state_type, etc.)

    Returns:
        MetricsBundle with computed metrics, or None if no metrics requested.
    """
    metric_names = resolve_metrics(config.metrics)
    if metric_names is None:
        return None

    if not counts:
        logger.warning("No measurement counts available for metrics computation")
        return None

    # Determine profile name (if a string was passed)
    profile = config.metrics if isinstance(config.metrics, str) else None

    # Compute through the registry (single source of truth)
    results = compute_all(
        metric_names=metric_names,
        counts=counts,
        state_type=config.state_type,
        error_rate=getattr(config, "error_rate", None),
        balance_circuit=getattr(config, "balance_circuit", None),
    )

    # Convert MetricResult TypedDicts -> MetricEntry Pydantic models
    entries: dict[str, MetricEntry] = {}
    for name, result in results.items():
        entries[name] = MetricEntry(
            value=float(result.get("value", 0.0)),
            ci95=result.get("ci95"),
            status=str(result.get("status", "experimental")),
            extras=result.get("extras", {}),
        )

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

    bundle = MetricsBundle(
        metrics=entries,
        profile=profile,
        metadata=metadata,
    )

    logger.info(
        "Computed %d metrics (profile=%s): %s",
        len(entries),
        profile,
        ", ".join(f"{k}={v.value:.4f}" for k, v in entries.items()),
    )
    return bundle


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

    if getattr(config, "z_prob", None) is not None:
        conditions["z_prob"] = config.z_prob
    if getattr(config, "i_prob", None) is not None:
        conditions["i_prob"] = config.i_prob
    if getattr(config, "t1", None) is not None:
        conditions["t1"] = config.t1
    if getattr(config, "t2", None) is not None:
        conditions["t2"] = config.t2

    return conditions
