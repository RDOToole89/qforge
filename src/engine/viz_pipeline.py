"""Visualization pipeline for experiment results.

Dispatches rendering of histograms, density matrices, correlation plots,
circuit diagrams, metrics summaries, and Bloch sphere plots through the
visualization service.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from src.engine.models import ArtifactRef, ExperimentAnalysis, ExperimentConfig

logger = logging.getLogger(__name__)

# Optional visualization (gracefully skipped if not installed)
try:
    from src.engine.visualization import create_default_service
except Exception:
    create_default_service = None  # type: ignore


def render_visualizations(
    cfg: ExperimentConfig,
    analysis: ExperimentAnalysis,
    metrics_bundle: Any,
    saved_path: str,
) -> list[ArtifactRef]:
    """Render all configured visualizations, returning artifact references.

    Non-fatal: if rendering fails for any type, it is logged and skipped.
    Returns an empty list if visualization is disabled or unavailable.
    """
    viz_config = cfg.visualization_type

    # Handle "none" — string or list containing "none"
    if viz_config == "none" or viz_config == ["none"]:
        return []
    if create_default_service is None:
        return []

    artifacts: list[ArtifactRef] = []
    try:
        service = create_default_service()
        viz_types = _resolve_viz_types(viz_config, analysis, metrics_bundle)
        for vt in viz_types:
            try:
                viz_payload: dict[str, Any] = {
                    "analysis": analysis.model_dump(),
                    "metrics_bundle": (metrics_bundle.model_dump() if metrics_bundle else None),
                    "export_formats": cfg.export_formats,
                }
                out_path = os.path.join(os.path.dirname(saved_path), vt)
                artifact = service.render_or_none(vt, viz_payload, out_path)
                if artifact:
                    artifacts.append(artifact)
            except Exception as e:
                logger.warning("Visualization '%s' skipped: %s", vt, e)
    except Exception as e:
        logger.warning("Visualization service init failed: %s", e)

    return artifacts


def _resolve_viz_types(
    viz_config: list[str] | str,
    analysis: ExperimentAnalysis,
    metrics_bundle: Any,
) -> list[str]:
    """Map visualization_type config value to a list of renderable types.

    Accepts a string (single type) or a list of strings (multiple types).
    "all" expands to every type whose data prerequisites are met.
    "none" returns an empty list.
    """
    # Normalize to list
    if isinstance(viz_config, str):
        types = [viz_config]
    else:
        types = list(viz_config)

    # Filter out "none"
    types = [t for t in types if t != "none"]
    if not types:
        return []

    # If "all" is in the list, expand it
    if "all" in types:
        return _expand_all(analysis, metrics_bundle)

    return types


def _expand_all(analysis: ExperimentAnalysis, metrics_bundle: Any) -> list[str]:
    """Expand "all" into every visualization type whose data is available."""
    available: list[str] = []
    meas = analysis.measurement_results

    if meas.raw_counts:
        available.append("histogram")

    if meas.density_matrix:
        available.append("density_matrix")

    if meas.statevector or meas.density_matrix:
        params = analysis.experiment_parameters
        n_qubits = params.get("num_qubits", 0) if isinstance(params, dict) else 0
        if 1 <= n_qubits <= 2:
            available.append("bloch_sphere")

    # Correlation needs EEC extras with matrices
    if metrics_bundle is not None:
        try:
            eec = metrics_bundle.metrics.get("entanglement_error_correlation")
            if eec and eec.extras and "error_correlation_matrix" in eec.extras:
                available.append("correlation")
        except Exception:
            pass

        # Metrics summary when any metrics are available
        try:
            if metrics_bundle.metrics:
                available.append("metrics_summary")
        except Exception:
            pass

    # Circuit is always available
    available.append("circuit")

    return available
