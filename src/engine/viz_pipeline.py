"""Visualization pipeline for experiment results.

Dispatches rendering of histograms, density matrices, correlation plots,
and circuit diagrams through the visualization service.
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
    if cfg.visualization_type == "none" or create_default_service is None:
        return []

    artifacts: list[ArtifactRef] = []
    try:
        service = create_default_service()
        viz_types = _resolve_viz_types(cfg.visualization_type, analysis, metrics_bundle)
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
    viz_type: str,
    analysis: ExperimentAnalysis,
    metrics_bundle: Any,
) -> list[str]:
    """Map visualization_type config value to a list of renderable types.

    "all" expands to every type whose data prerequisites are met.
    "none" returns an empty list. A single named type returns [type].
    """
    if viz_type == "none":
        return []

    if viz_type != "all":
        return [viz_type]

    # For "all", filter to types that have data available
    available: list[str] = []
    meas = analysis.measurement_results
    if meas.raw_counts:
        available.append("histogram")
    if meas.density_matrix:
        available.append("density_matrix")
    # Correlation needs EEC extras with matrices
    if metrics_bundle is not None:
        try:
            eec = metrics_bundle.metrics.get("entanglement_error_correlation")
            if eec and eec.extras and "error_correlation_matrix" in eec.extras:
                available.append("correlation")
        except Exception:
            pass
    # Circuit is always available (we pass the live object)
    available.append("circuit")
    return available
