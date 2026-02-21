"""
Research-focused visualization renderers.

Each renderer is a plugin that can create specific types of visualizations
from quantum experiment data.
"""

import logging
import math
from pathlib import Path
from typing import Any

# Use a headless backend if needed (safe in GUI too)
import matplotlib

try:
    matplotlib.use("Agg")  # no-op if already set
except Exception:
    pass
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

from src.engine.models import ArtifactRef

from .export import save_figure
from .service import VisualizationRenderer

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _build_title(params: dict[str, Any]) -> str:
    """Build a figure title from experiment parameters."""
    parts: list[str] = []
    st = params.get("state_type")
    if st:
        parts.append(f"{str(st).upper()} State")
    nq = params.get("num_qubits")
    if isinstance(nq, int) and nq > 0:
        parts.append(f"({nq} qubits)")

    if params.get("noise_enabled"):
        noise_type = str(params.get("noise_type", "noise")).replace("_", " ").title()
        er = params.get("error_rate")
        if isinstance(er, (int, float)):
            parts.append(f"{noise_type} (p={er:.3f})")
        else:
            parts.append(noise_type)

    return " - ".join(parts) if parts else "Measurement Results"


# ---------------------------------------------------------------------------
# HistogramRenderer
# ---------------------------------------------------------------------------


class HistogramRenderer(VisualizationRenderer):
    """
    Renders measurement histograms optimized for research analysis.

    Features:
    - Clean, publication-ready styling
    - Auto-detect counts vs probabilities (axis labeling)
    - Top-K compaction with 'OTHER' bucket for high-dimensional outcomes
    - Research metric annotations (AI / PCR / EEC) when provided
    - Optional highlight of top pathways when PCR is large
    - Stable sorting (value_desc by default; bitstring optional)
    - Multi-format export (PNG/PDF/SVG)

    Data contract (flexible):
      data = {
        "analysis": {
          "measurement_results": {
            "raw_counts": {bitstring: int, ...}  # preferred
            # or
            "outcome_probabilities": {bitstring: float, ...}
          },
          "experiment_parameters": {...}  # optional, used for title
        },
        # or directly:
        "counts": {bitstring: int|float},
        # optional rendering hints:
        "sort": "value_desc" | "bitstring",
        "top_k": int,                # default 64
        "highlight_top_n": int,      # default 2
        "transparent": bool,         # default False
        "export_formats": ["png"],   # list of formats
      }
    """

    def can_render(self, viz_type: str, data: dict[str, Any]) -> bool:
        if viz_type != "histogram":
            return False

        analysis = data.get("analysis", {})
        measurement_results = analysis.get("measurement_results", {})

        counts = (
            measurement_results.get("raw_counts")
            or measurement_results.get("outcome_probabilities")
            or data.get("counts")
        )
        return isinstance(counts, dict) and len(counts) > 0

    def render(self, data: dict[str, Any], output_path: str) -> ArtifactRef:
        analysis = data.get("analysis", {})
        measurement_results = analysis.get("measurement_results", {})
        experiment_params = analysis.get("experiment_parameters", {}) or {}
        research_metrics = data.get("metrics_bundle")
        export_formats = data.get("export_formats", ["png"])

        counts = (
            measurement_results.get("raw_counts")
            or measurement_results.get("outcome_probabilities")
            or data.get("counts")
        )
        if not counts:
            raise ValueError("No measurement counts or probabilities found in data")

        sort_mode = str(data.get("sort", "value_desc")).lower()
        top_k = int(data.get("top_k", 64))
        highlight_top_n = max(0, int(data.get("highlight_top_n", 2)))
        transparent = bool(data.get("transparent", False))

        is_prob, normalized_counts = self._normalize_if_probs(counts)

        reduced_labels, reduced_values, used_other = self._compact_top_k(
            normalized_counts, top_k=top_k, sort_mode=sort_mode
        )

        fig, ax = plt.subplots(figsize=(10, 6))

        indices = np.arange(len(reduced_labels))
        bars = ax.bar(indices, reduced_values, linewidth=0.5)

        for b in bars:
            b.set_alpha(0.9)

        ax.set_xlabel("Measurement Outcomes", fontsize=12, fontweight="bold")
        ax.set_ylabel("Probability" if is_prob else "Counts", fontsize=12, fontweight="bold")

        ax.set_xticks(indices)
        rot = 45 if len(reduced_labels) > 12 else 0
        ax.set_xticklabels(reduced_labels, rotation=rot, ha="right" if rot else "center")

        if not is_prob:
            ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{int(x):,}"))
        else:
            ax.set_ylim(0, min(1.0, max(0.05, max(reduced_values) * 1.15)))

        ax.set_title(_build_title(experiment_params), fontsize=14, fontweight="bold", pad=20)

        self._annotate_metrics(ax, research_metrics)

        if research_metrics:
            try:
                ci_entry = (research_metrics.get("metrics", {}) or {}).get(
                    "concentration_index", {}
                )
                pcr = float(ci_entry.get("value", 1.0)) if isinstance(ci_entry, dict) else 1.0
            except Exception:
                pcr = 1.0
            if pcr > 2.0 and highlight_top_n > 0:
                top_idx = np.argsort(reduced_values)[::-1][:highlight_top_n]
                for i in top_idx:
                    bars[i].set_edgecolor("black")
                    bars[i].set_linewidth(1.5)
                    bars[i].set_alpha(1.0)

        ax.grid(True, axis="y", alpha=0.3)
        plt.tight_layout()

        # --- Save via multi-format utility ---
        base = Path(output_path)
        # Strip any existing extension so save_figure can add per-format suffixes
        base_no_ext = base.parent / base.stem
        saved_paths = save_figure(fig, base_no_ext, export_formats, transparent=transparent)
        plt.close(fig)

        primary_path = saved_paths[0] if saved_paths else str(base)
        logger.info("Saved research histogram to %s", primary_path)

        meta_total_shots = None
        if not is_prob:
            try:
                if self._looks_like_counts(counts):
                    meta_total_shots = int(sum(int(v) for v in counts.values()))
            except Exception:
                meta_total_shots = None

        return ArtifactRef(
            kind="histogram",
            path=primary_path,
            metadata={
                "renderer": "HistogramRenderer",
                "experiment_type": experiment_params.get("state_type"),
                "num_outcomes": len(counts),
                "displayed_bars": len(reduced_labels),
                "used_other_bucket": used_other,
                "sorted_by": sort_mode,
                "is_probability": is_prob,
                "total_shots": meta_total_shots,
                "has_research_metrics": research_metrics is not None,
                "saved_formats": [Path(p).suffix.lstrip(".") for p in saved_paths],
            },
        )

    # ----------------- helpers -----------------

    def _annotate_metrics(self, ax, bundle_data: dict[str, Any] | None) -> None:
        if not bundle_data:
            return

        metrics_dict = bundle_data.get("metrics", {})
        if not metrics_dict:
            return

        abbrevs = {
            "structure_score": "SS",
            "concentration_index": "CI",
            "entanglement_error_correlation": "EEC",
            "total_correlation": "TC",
            "pathway_persistence": "TPS",
            "complexity_emergence_score": "CES",
        }

        text_bits = []
        try:
            for name, entry in metrics_dict.items():
                if isinstance(entry, dict) and "value" in entry:
                    label = abbrevs.get(name, name)
                    text_bits.append(f"{label}: {float(entry['value']):.3f}")
        except Exception:
            pass

        if text_bits:
            ax.text(
                0.02,
                0.98,
                "Metrics: " + " | ".join(text_bits),
                transform=ax.transAxes,
                fontsize=10,
                va="top",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="0.9", edgecolor="0.8"),
            )

    def _normalize_if_probs(self, counts: dict[str, Any]) -> tuple[bool, dict[str, float]]:
        vals = list(counts.values())
        if not vals:
            return False, {}

        def _to_float(x):
            try:
                return float(x)
            except Exception:
                return math.nan

        fvals = [_to_float(v) for v in vals]
        finite = [v for v in fvals if math.isfinite(v)]
        if not finite:
            return False, {k: 0.0 for k in counts.keys()}

        total = sum(finite)
        looks_prob = 0.98 <= total <= 1.02 and all(0.0 <= v <= 1.0 for v in finite)
        looks_counts = self._looks_like_counts(counts)

        if looks_prob and not looks_counts:
            norm = total if total != 0 else 1.0
            return True, {
                k: (float(counts[k]) / norm if math.isfinite(_to_float(counts[k])) else 0.0)
                for k in counts.keys()
            }
        else:
            return False, {
                k: float(counts[k]) if math.isfinite(_to_float(counts[k])) else 0.0
                for k in counts.keys()
            }

    def _looks_like_counts(self, counts: dict[str, Any]) -> bool:
        vals = list(counts.values())
        if not vals:
            return False
        try:
            fvals = [float(v) for v in vals]
        except Exception:
            return False
        if sum(fvals) <= 1.5:
            return False
        near_int = sum(1 for v in fvals if abs(v - round(v)) < 1e-6)
        return near_int / len(fvals) >= 0.95

    def _compact_top_k(
        self,
        mapping: dict[str, float],
        top_k: int,
        sort_mode: str = "value_desc",
    ) -> tuple[list[str], list[float], bool]:
        items = list(mapping.items())
        if sort_mode == "bitstring":
            items.sort(key=lambda kv: kv[0])
        else:
            items.sort(key=lambda kv: kv[1], reverse=True)

        if len(items) <= top_k or top_k < 1:
            labels, vals = zip(*items)
            return list(labels), list(vals), False

        head = items[:top_k]
        tail = items[top_k:]
        other_sum = sum(v for _, v in tail)

        labels = [k for k, _ in head] + ["OTHER"]
        values = [v for _, v in head] + [other_sum]
        return labels, values, True


# ---------------------------------------------------------------------------
# DensityMatrixRenderer
# ---------------------------------------------------------------------------


class DensityMatrixRenderer(VisualizationRenderer):
    """Renders density matrix heatmap with eigenvalue spectrum.

    Data contract:
      data["analysis"]["measurement_results"]["density_matrix"] must exist
      as a list-of-lists in ``[[real, imag], ...]`` format.
    """

    def can_render(self, viz_type: str, data: dict[str, Any]) -> bool:
        if viz_type != "density_matrix":
            return False
        dm = (
            data.get("analysis", {})
            .get("measurement_results", {})
            .get("density_matrix")
        )
        return isinstance(dm, list) and len(dm) > 0

    def render(self, data: dict[str, Any], output_path: str) -> ArtifactRef:
        analysis = data.get("analysis", {})
        meas = analysis.get("measurement_results", {})
        experiment_params = analysis.get("experiment_parameters", {}) or {}
        export_formats = data.get("export_formats", ["png"])

        dm_raw = meas["density_matrix"]
        # Reconstruct complex NxN matrix from [[real, imag], ...] format
        n = len(dm_raw)
        rho = np.zeros((n, n), dtype=complex)
        for i, row in enumerate(dm_raw):
            for j, entry in enumerate(row):
                rho[i, j] = complex(entry[0], entry[1])

        mag = np.abs(rho)
        eigenvalues = np.sort(np.real(np.linalg.eigvalsh(rho)))[::-1]
        purity = float(np.real(np.trace(rho @ rho)))
        fidelity = meas.get("fidelity")

        # --- Plot ---
        fig, (ax_heatmap, ax_eigen) = plt.subplots(
            1, 2, figsize=(14, 6), gridspec_kw={"width_ratios": [2, 1]}
        )

        # Main panel: magnitude heatmap
        im = ax_heatmap.imshow(mag, cmap="viridis", interpolation="nearest")
        fig.colorbar(im, ax=ax_heatmap, label=r"$|\rho_{ij}|$", shrink=0.8)
        ax_heatmap.set_xlabel("Column index")
        ax_heatmap.set_ylabel("Row index")
        ax_heatmap.set_title("Density Matrix Magnitude")

        # Annotation box
        ann_lines = [f"Purity Tr($\\rho^2$) = {purity:.4f}"]
        if fidelity is not None:
            ann_lines.append(f"Fidelity = {float(fidelity):.4f}")
        ann_lines.append(f"Dimension = {n}x{n}")
        ax_heatmap.text(
            0.02, 0.98, "\n".join(ann_lines),
            transform=ax_heatmap.transAxes, fontsize=9, va="top",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="0.95", edgecolor="0.8"),
        )

        # Subplot: eigenvalue spectrum
        ax_eigen.bar(range(len(eigenvalues)), eigenvalues, color="steelblue", alpha=0.85)
        ax_eigen.set_xlabel("Eigenvalue index")
        ax_eigen.set_ylabel("Eigenvalue")
        ax_eigen.set_title("Eigenvalue Spectrum")
        ax_eigen.axhline(y=0, color="gray", linewidth=0.5, linestyle="--")

        # Super-title
        fig.suptitle(
            f"Density Matrix — {_build_title(experiment_params)}",
            fontsize=14, fontweight="bold", y=1.02,
        )
        plt.tight_layout()

        # --- Save ---
        base = Path(output_path)
        base_no_ext = base.parent / base.stem
        saved_paths = save_figure(fig, base_no_ext, export_formats)
        plt.close(fig)

        primary_path = saved_paths[0] if saved_paths else str(base)
        logger.info("Saved density matrix visualization to %s", primary_path)

        return ArtifactRef(
            kind="density_matrix",
            path=primary_path,
            metadata={
                "renderer": "DensityMatrixRenderer",
                "dimension": n,
                "purity": purity,
                "fidelity": fidelity,
                "saved_formats": [Path(p).suffix.lstrip(".") for p in saved_paths],
            },
        )


# ---------------------------------------------------------------------------
# CorrelationRenderer
# ---------------------------------------------------------------------------


class CorrelationRenderer(VisualizationRenderer):
    """Renders MI and entanglement topology heatmaps side by side.

    Requires EEC extras containing ``error_correlation_matrix`` and
    ``entanglement_matrix`` in ``metrics_bundle.metrics.entanglement_error_correlation.extras``.
    """

    def can_render(self, viz_type: str, data: dict[str, Any]) -> bool:
        if viz_type != "correlation":
            return False
        extras = self._get_eec_extras(data)
        return (
            extras is not None
            and "error_correlation_matrix" in extras
            and "entanglement_matrix" in extras
        )

    def render(self, data: dict[str, Any], output_path: str) -> ArtifactRef:
        analysis = data.get("analysis", {})
        experiment_params = analysis.get("experiment_parameters", {}) or {}
        export_formats = data.get("export_formats", ["png"])

        extras = self._get_eec_extras(data) or {}
        mi_matrix = np.array(extras["error_correlation_matrix"])
        ent_matrix = np.array(extras["entanglement_matrix"])

        # Get EEC scalar value
        eec_entry = (
            data.get("metrics_bundle", {})
            .get("metrics", {})
            .get("entanglement_error_correlation", {})
        )
        eec_value = float(eec_entry.get("value", 0.0)) if isinstance(eec_entry, dict) else 0.0

        n = mi_matrix.shape[0]
        qubit_labels = [f"Q{i}" for i in range(n)]

        fig, (ax_mi, ax_ent) = plt.subplots(1, 2, figsize=(14, 6))

        # Left panel: MI (error correlation) heatmap
        im1 = ax_mi.imshow(mi_matrix, cmap="Reds", interpolation="nearest")
        fig.colorbar(im1, ax=ax_mi, label="Mutual Information", shrink=0.8)
        ax_mi.set_xticks(range(n))
        ax_mi.set_yticks(range(n))
        ax_mi.set_xticklabels(qubit_labels)
        ax_mi.set_yticklabels(qubit_labels)
        ax_mi.set_title("Error Correlation (MI)")

        # Right panel: entanglement topology heatmap
        im2 = ax_ent.imshow(ent_matrix, cmap="Blues", interpolation="nearest")
        fig.colorbar(im2, ax=ax_ent, label="Entanglement Weight", shrink=0.8)
        ax_ent.set_xticks(range(n))
        ax_ent.set_yticks(range(n))
        ax_ent.set_xticklabels(qubit_labels)
        ax_ent.set_yticklabels(qubit_labels)
        ax_ent.set_title("Entanglement Topology")

        # EEC annotation
        fig.text(
            0.5, 0.01,
            f"EEC = {eec_value:.4f}",
            ha="center", fontsize=12, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="lightyellow", edgecolor="gray"),
        )

        fig.suptitle(
            f"Correlation Analysis — {_build_title(experiment_params)}",
            fontsize=14, fontweight="bold", y=1.02,
        )
        plt.tight_layout(rect=[0, 0.04, 1, 1])

        # --- Save ---
        base = Path(output_path)
        base_no_ext = base.parent / base.stem
        saved_paths = save_figure(fig, base_no_ext, export_formats)
        plt.close(fig)

        primary_path = saved_paths[0] if saved_paths else str(base)
        logger.info("Saved correlation visualization to %s", primary_path)

        return ArtifactRef(
            kind="correlation",
            path=primary_path,
            metadata={
                "renderer": "CorrelationRenderer",
                "num_qubits": n,
                "eec_value": eec_value,
                "saved_formats": [Path(p).suffix.lstrip(".") for p in saved_paths],
            },
        )

    @staticmethod
    def _get_eec_extras(data: dict[str, Any]) -> dict[str, Any] | None:
        try:
            return (
                data.get("metrics_bundle", {})
                .get("metrics", {})
                .get("entanglement_error_correlation", {})
                .get("extras")
            )
        except Exception:
            return None


# ---------------------------------------------------------------------------
# CircuitDiagramRenderer
# ---------------------------------------------------------------------------


class CircuitDiagramRenderer(VisualizationRenderer):
    """Renders a Qiskit QuantumCircuit diagram via ``circuit.draw(output='mpl')``.

    Requires ``data["circuit"]`` to be a live ``QuantumCircuit`` object.
    """

    def can_render(self, viz_type: str, data: dict[str, Any]) -> bool:
        if viz_type != "circuit":
            return False
        circuit = data.get("circuit")
        # Check for QuantumCircuit without importing it at module level
        return circuit is not None and hasattr(circuit, "draw") and hasattr(circuit, "depth")

    def render(self, data: dict[str, Any], output_path: str) -> ArtifactRef:
        circuit = data["circuit"]
        export_formats = data.get("export_formats", ["png"])
        experiment_params = data.get("analysis", {}).get("experiment_parameters", {}) or {}

        fig = circuit.draw(output="mpl")
        # Annotate with depth and gate count
        depth = circuit.depth()
        num_gates = len(circuit.data)
        fig.text(
            0.99, 0.01,
            f"Depth: {depth}  |  Gates: {num_gates}",
            ha="right", va="bottom", fontsize=9,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="0.95", edgecolor="0.8"),
        )

        # --- Save ---
        base = Path(output_path)
        base_no_ext = base.parent / base.stem
        saved_paths = save_figure(fig, base_no_ext, export_formats)
        plt.close(fig)

        primary_path = saved_paths[0] if saved_paths else str(base)
        logger.info("Saved circuit diagram to %s", primary_path)

        return ArtifactRef(
            kind="circuit",
            path=primary_path,
            metadata={
                "renderer": "CircuitDiagramRenderer",
                "depth": depth,
                "num_gates": num_gates,
                "num_qubits": circuit.num_qubits,
                "saved_formats": [Path(p).suffix.lstrip(".") for p in saved_paths],
            },
        )
