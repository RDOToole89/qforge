"""Sweep-level visualization utilities.

These operate on collections of ExperimentResults (from sweep() calls),
not individual experiments. They are standalone functions, not part of
the per-experiment pipeline.

Usage:
    from src.engine.visualization.sweep_renderers import (
        render_sweep_summary,
        render_comparison_histograms,
    )

    # After a noise sweep
    results = get_experiment("dec_04_noise_resilience").run_sweep()
    render_sweep_summary(results, "error_rate", "structure_score", "sweep_plot")

    # After a topology comparison
    labeled = {"GHZ": ghz_counts, "W": w_counts, "Product": product_counts}
    render_comparison_histograms(labeled, "comparison_plot")
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import matplotlib
try:
    matplotlib.use("Agg")
except Exception:
    pass
import matplotlib.pyplot as plt
import numpy as np

from src.engine.models import ArtifactRef

from .export import save_figure

logger = logging.getLogger(__name__)


def render_sweep_summary(
    results: list[Any],
    parameter_name: str,
    metric_name: str = "structure_score",
    output_path: str = "sweep_summary",
    export_formats: list[str] | None = None,
) -> ArtifactRef:
    """Render a line plot of a metric vs a swept parameter.

    Args:
        results: List of ExperimentResult objects from a sweep
        parameter_name: Name of the swept parameter (e.g., "error_rate", "num_qubits")
        metric_name: Name of the metric to plot (e.g., "structure_score")
        output_path: Base path for saving the figure
        export_formats: List of formats (default: ["png"])

    Returns:
        ArtifactRef pointing to the saved figure
    """
    if export_formats is None:
        export_formats = ["png"]

    x_values = []
    y_values = []
    ci_lower = []
    ci_upper = []

    for result in results:
        # Extract parameter value
        params = result.analysis.experiment_parameters
        if isinstance(params, dict):
            x_val = params.get(parameter_name)
        else:
            x_val = getattr(params, parameter_name, None)

        if x_val is None:
            continue

        # Extract metric value
        mb = result.metrics_bundle
        if mb and mb.metrics:
            metric = mb.metrics.get(metric_name)
            if metric:
                val = metric.value if hasattr(metric, "value") else metric.get("value")
                if val is not None:
                    x_values.append(float(x_val))
                    y_values.append(float(val))
                    # Extract CI if available
                    ci = metric.ci95 if hasattr(metric, "ci95") else metric.get("ci95")
                    if ci and len(ci) == 2:
                        ci_lower.append(float(ci[0]))
                        ci_upper.append(float(ci[1]))

    if not x_values:
        raise ValueError(f"No data points found for {parameter_name} vs {metric_name}")

    # Sort by x value
    sorted_idx = np.argsort(x_values)
    x_values = [x_values[i] for i in sorted_idx]
    y_values = [y_values[i] for i in sorted_idx]

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(x_values, y_values, "o-", color="#2980b9", linewidth=2, markersize=8)

    # Add CI bands if available
    if len(ci_lower) == len(x_values):
        ci_lower = [ci_lower[i] for i in sorted_idx]
        ci_upper = [ci_upper[i] for i in sorted_idx]
        ax.fill_between(x_values, ci_lower, ci_upper, alpha=0.2, color="#2980b9")

    # Labels
    short_names = {
        "structure_score": "Structure Score",
        "total_correlation": "Total Correlation",
        "concentration_index": "Concentration Index",
        "entanglement_error_correlation": "EEC",
        "asymmetry_index": "Asymmetry Index",
        "error_rate": "Error Rate",
        "num_qubits": "Number of Qubits",
    }
    ax.set_xlabel(short_names.get(parameter_name, parameter_name), fontsize=12)
    ax.set_ylabel(short_names.get(metric_name, metric_name), fontsize=12)
    ax.set_title(
        f"{short_names.get(metric_name, metric_name)} vs {short_names.get(parameter_name, parameter_name)}",
        fontsize=14, fontweight="bold",
    )
    ax.grid(alpha=0.3)
    fig.tight_layout()

    saved_paths = save_figure(fig, output_path, export_formats)
    plt.close(fig)

    return ArtifactRef(
        kind="sweep_line",
        path=saved_paths[0] if saved_paths else output_path,
        metadata={
            "renderer": "render_sweep_summary",
            "parameter": parameter_name,
            "metric": metric_name,
            "data_points": len(x_values),
            "saved_formats": [Path(p).suffix.lstrip(".") for p in saved_paths],
        },
    )


def render_comparison_histograms(
    labeled_counts: dict[str, dict[str, int]],
    output_path: str = "comparison",
    export_formats: list[str] | None = None,
    top_k: int = 20,
) -> ArtifactRef:
    """Render grouped bar chart comparing measurement distributions.

    Args:
        labeled_counts: Dict mapping labels to count dicts, e.g.,
            {"GHZ": {"000": 400, "111": 400}, "Product": {"000": 125, ...}}
        output_path: Base path for saving the figure
        export_formats: List of formats (default: ["png"])
        top_k: Maximum number of bitstrings to show (most frequent across all)

    Returns:
        ArtifactRef pointing to the saved figure
    """
    if export_formats is None:
        export_formats = ["png"]

    labels = list(labeled_counts.keys())
    n_series = len(labels)

    # Find top-k bitstrings by total frequency across all series
    total_counts: dict[str, int] = {}
    for counts in labeled_counts.values():
        for bs, c in counts.items():
            total_counts[bs] = total_counts.get(bs, 0) + c

    top_bitstrings = sorted(total_counts, key=lambda x: -total_counts[x])[:top_k]

    # Build data matrix
    data = np.zeros((n_series, len(top_bitstrings)))
    for i, label in enumerate(labels):
        total = sum(labeled_counts[label].values())
        for j, bs in enumerate(top_bitstrings):
            data[i, j] = labeled_counts[label].get(bs, 0) / total * 100 if total > 0 else 0

    fig, ax = plt.subplots(figsize=(max(10, len(top_bitstrings) * 0.8), 6))

    x = np.arange(len(top_bitstrings))
    width = 0.8 / n_series
    colors = ["#2980b9", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6"]

    for i, label in enumerate(labels):
        offset = (i - n_series / 2 + 0.5) * width
        ax.bar(x + offset, data[i], width, label=label,
               color=colors[i % len(colors)], edgecolor="white")

    ax.set_xlabel("Measurement Outcome", fontsize=11)
    ax.set_ylabel("Probability (%)", fontsize=11)
    ax.set_title("Distribution Comparison", fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([f"|{bs}⟩" for bs in top_bitstrings], rotation=45, ha="right", fontsize=9)
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()

    saved_paths = save_figure(fig, output_path, export_formats)
    plt.close(fig)

    return ArtifactRef(
        kind="comparison",
        path=saved_paths[0] if saved_paths else output_path,
        metadata={
            "renderer": "render_comparison_histograms",
            "series": labels,
            "bitstrings_shown": len(top_bitstrings),
            "saved_formats": [Path(p).suffix.lstrip(".") for p in saved_paths],
        },
    )
