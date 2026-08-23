"""Visualization system for quantum experiments.

This package provides clean, extensible visualization capabilities with a
plugin architecture:

- Thread-safe renderer registry
- Priority-based renderer selection
- 6 built-in renderers (histogram, density matrix, correlation, circuit,
  metrics summary, Bloch sphere)
- Sweep-level visualization utilities (line plots, comparison histograms)

Typical usage:
    from qforge.engine.visualization import create_default_service
    service = create_default_service()
    artifact = service.render_or_none("histogram", result.model_dump(), "out/hist.png")

    # Sweep visualization
    from qforge.engine.visualization import render_sweep_summary
    render_sweep_summary(results, "error_rate", "structure_score", "sweep_plot")
"""

from __future__ import annotations

from .export import save_figure
from .gate_explainers import explain_circuit_gates
from .renderers import (
    BlochSphereRenderer,
    CircuitDiagramRenderer,
    CorrelationRenderer,
    DensityMatrixRenderer,
    HistogramRenderer,
    MetricsSummaryRenderer,
)
from .service import (
    RendererRegistryError,
    VisualizationRenderer,
    VisualizationService,
    create_default_service,
)
from .sweep_renderers import render_comparison_histograms, render_sweep_summary

__all__ = [
    "VisualizationService",
    "VisualizationRenderer",
    "RendererRegistryError",
    "HistogramRenderer",
    "DensityMatrixRenderer",
    "CorrelationRenderer",
    "CircuitDiagramRenderer",
    "MetricsSummaryRenderer",
    "BlochSphereRenderer",
    "save_figure",
    "create_default_service",
    "explain_circuit_gates",
    "render_sweep_summary",
    "render_comparison_histograms",
]
