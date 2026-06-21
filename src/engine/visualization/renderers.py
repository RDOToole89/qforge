"""Research-focused visualization renderers.

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
    """Renders measurement histograms optimized for research analysis.

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
        """Check whether this renderer can handle the given visualization type and data."""
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
        """Render a measurement histogram and save it to disk."""
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

        # Improvement 6: Ghost overlay showing ideal (noiseless) distribution
        state_type = experiment_params.get("state_type", "").upper()
        num_qubits = int(experiment_params.get("num_qubits", 0))
        total_shots = sum(int(v) for v in normalized_counts.values()) if not is_prob else 1
        ideal_values = self._get_ideal_distribution(
            state_type, num_qubits, reduced_labels, is_prob, total_shots
        )

        if ideal_values is not None:
            ax.bar(
                indices,
                ideal_values,
                linewidth=1.5,
                edgecolor="#aaa",
                facecolor="none",
                linestyle="--",
                label="Ideal (noiseless)",
            )

        bars = ax.bar(indices, reduced_values, linewidth=0.5, alpha=0.9, label="Measured")

        ax.set_xlabel("Measurement Outcomes", fontsize=12, fontweight="bold")
        ax.set_ylabel("Probability" if is_prob else "Counts", fontsize=12, fontweight="bold")

        # Improvement 3: Ket notation for x-axis labels
        ket_labels = [f"|{lbl}⟩" if lbl != "OTHER" else lbl for lbl in reduced_labels]
        ax.set_xticks(indices)
        rot = 45 if len(ket_labels) > 12 else 0
        ax.set_xticklabels(ket_labels, rotation=rot, ha="right" if rot else "center")

        if ideal_values is not None:
            ax.legend(fontsize=9, loc="upper right")

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

    def _annotate_metrics(self, ax: Any, bundle_data: dict[str, Any] | None) -> None:
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
                    val = float(entry["value"])
                    if abs(val) < 1e-6:
                        continue  # Filter out zero-value metrics
                    label = abbrevs.get(name, name)
                    text_bits.append(f"{label}: {val:.3f}")
        except Exception:
            pass

        if text_bits:
            # Place metrics ABOVE the plot area (below the title) to avoid
            # overlapping bars. Uses figure coordinates, not axes coordinates.
            fig = ax.get_figure()
            fig.text(
                0.5,
                0.92,
                "Metrics: " + " | ".join(text_bits),
                fontsize=9,
                ha="center",
                va="top",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="0.95", edgecolor="0.85"),
            )
            # Add top margin so metrics text doesn't overlap the plot
            fig.subplots_adjust(top=0.88)

    @staticmethod
    def _get_ideal_distribution(
        state_type: str,
        num_qubits: int,
        labels: list[str],
        is_prob: bool,
        total_shots: int,
    ) -> list[float] | None:
        """Compute ideal (noiseless) distribution for ghost overlay."""
        if num_qubits < 1 or num_qubits > 8:
            return None

        ideal: dict[str, float] = {}
        if state_type == "GHZ":
            zeros = "0" * num_qubits
            ones = "1" * num_qubits
            ideal = {zeros: 0.5, ones: 0.5}
        elif state_type == "W":
            for i in range(num_qubits):
                bs = "0" * i + "1" + "0" * (num_qubits - i - 1)
                ideal[bs] = 1.0 / num_qubits
        elif state_type == "SUPERPOSITION":
            n_outcomes = 2**num_qubits
            for i in range(n_outcomes):
                ideal[f"{i:0{num_qubits}b}"] = 1.0 / n_outcomes
        elif state_type == "BELL":
            ideal = {"00": 0.5, "11": 0.5}
        else:
            return None  # Unknown state type, skip ghost

        if not ideal:
            return None

        # Map to the label order used in the histogram
        multiplier = total_shots if not is_prob else 1.0
        return [ideal.get(lbl, 0) * multiplier for lbl in labels]

    def _normalize_if_probs(self, counts: dict[str, Any]) -> tuple[bool, dict[str, float]]:
        vals = list(counts.values())
        if not vals:
            return False, {}

        def _to_float(x: Any) -> float:
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
            zlabels, zvals = zip(*items, strict=True)
            return list(zlabels), list(zvals), False

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
        """Check whether density matrix data is available for rendering."""
        if viz_type != "density_matrix":
            return False
        dm = data.get("analysis", {}).get("measurement_results", {}).get("density_matrix")
        return isinstance(dm, list) and len(dm) > 0

    def render(self, data: dict[str, Any], output_path: str) -> ArtifactRef:
        """Render a density matrix heatmap with eigenvalue spectrum and save it to disk."""
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

        # Improvement 2: Basis state labels
        num_qubits = int(np.log2(n)) if n > 0 and (n & (n - 1)) == 0 else 0
        if num_qubits > 0 and num_qubits <= 6:
            basis_labels = [f"|{i:0{num_qubits}b}⟩" for i in range(n)]
        else:
            basis_labels = [str(i) for i in range(n)]

        # Main panel: magnitude heatmap
        im = ax_heatmap.imshow(mag, cmap="viridis", interpolation="nearest")
        fig.colorbar(im, ax=ax_heatmap, label=r"$|\rho_{ij}|$", shrink=0.8)
        ax_heatmap.set_xticks(range(n))
        ax_heatmap.set_yticks(range(n))
        ax_heatmap.set_xticklabels(basis_labels, fontsize=8, rotation=45, ha="right")
        ax_heatmap.set_yticklabels(basis_labels, fontsize=8)
        ax_heatmap.set_xlabel("Column")
        ax_heatmap.set_ylabel("Row")
        ax_heatmap.set_title("Density Matrix Magnitude")

        # Improvement 4: Value annotations inside cells (for small matrices)
        if n <= 8:
            for i in range(n):
                for j in range(n):
                    val = mag[i, j]
                    color = "white" if val > mag.max() * 0.5 else "black"
                    ax_heatmap.text(
                        j,
                        i,
                        f"{val:.2f}",
                        ha="center",
                        va="center",
                        fontsize=7 if n <= 4 else 5,
                        color=color,
                    )

        # Annotation box
        purity_pct = purity * 100
        ann_lines = [f"Purity Tr($\\rho^2$) = {purity:.4f} ({purity_pct:.1f}%)"]
        if fidelity is not None:
            ann_lines.append(f"Fidelity = {float(fidelity):.4f}")
        ann_lines.append(f"Dimension = {n}x{n} ({num_qubits} qubits)")
        ax_heatmap.text(
            0.02,
            0.98,
            "\n".join(ann_lines),
            transform=ax_heatmap.transAxes,
            fontsize=9,
            va="top",
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
            fontsize=14,
            fontweight="bold",
            y=1.02,
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
        """Check whether correlation matrix data is available for rendering."""
        if viz_type != "correlation":
            return False
        extras = self._get_eec_extras(data)
        return (
            extras is not None
            and "error_correlation_matrix" in extras
            and "entanglement_matrix" in extras
        )

    def render(self, data: dict[str, Any], output_path: str) -> ArtifactRef:
        """Render MI and entanglement topology heatmaps side by side and save to disk."""
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

        # Add MI values inside cells
        if n <= 8:
            for i in range(n):
                for j in range(n):
                    val = mi_matrix[i, j]
                    color = "white" if val > mi_matrix.max() * 0.5 else "black"
                    ax_mi.text(
                        j,
                        i,
                        f"{val:.2f}",
                        ha="center",
                        va="center",
                        fontsize=7 if n <= 4 else 5,
                        color=color,
                    )

        # Right panel: entanglement topology heatmap
        im2 = ax_ent.imshow(ent_matrix, cmap="Blues", interpolation="nearest")
        fig.colorbar(im2, ax=ax_ent, label="Entanglement Weight", shrink=0.8)
        ax_ent.set_xticks(range(n))
        ax_ent.set_yticks(range(n))
        ax_ent.set_xticklabels(qubit_labels)
        ax_ent.set_yticklabels(qubit_labels)
        ax_ent.set_title("Entanglement Topology")

        # Add entanglement values inside cells
        if n <= 8:
            for i in range(n):
                for j in range(n):
                    val = ent_matrix[i, j]
                    color = "white" if val > ent_matrix.max() * 0.5 else "black"
                    ax_ent.text(
                        j,
                        i,
                        f"{val:.2f}",
                        ha="center",
                        va="center",
                        fontsize=7 if n <= 4 else 5,
                        color=color,
                    )

        # Improvement 5: EEC annotation with context for small qubit counts
        num_pairs = n * (n - 1) // 2
        if num_pairs <= 1:
            eec_text = f"EEC = {eec_value:.4f}  (N/A — need 3+ qubits for meaningful correlation)"
        elif eec_value > 0.3:
            eec_text = f"EEC = {eec_value:.4f}  (strong topology-error correlation)"
        elif eec_value > 0.1:
            eec_text = f"EEC = {eec_value:.4f}  (moderate correlation)"
        else:
            eec_text = f"EEC = {eec_value:.4f}  (weak or no correlation)"

        # Place EEC well below the plots — increase figure height and bottom margin
        fig.set_size_inches(14, 7.5)
        fig.subplots_adjust(bottom=0.18)
        fig.text(
            0.5,
            0.02,
            eec_text,
            ha="center",
            fontsize=11,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="lightyellow", edgecolor="gray"),
        )

        fig.suptitle(
            f"Correlation Analysis — {_build_title(experiment_params)}",
            fontsize=14,
            fontweight="bold",
            y=1.02,
        )
        plt.tight_layout(rect=(0, 0.04, 1, 1))

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
            extras: dict[str, Any] | None = (
                data.get("metrics_bundle", {})
                .get("metrics", {})
                .get("entanglement_error_correlation", {})
                .get("extras")
            )
            return extras
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
        """Check whether a drawable quantum circuit is present in the data."""
        if viz_type != "circuit":
            return False
        circuit = data.get("circuit")
        # Check for QuantumCircuit without importing it at module level
        return circuit is not None and hasattr(circuit, "draw") and hasattr(circuit, "depth")

    def render(self, data: dict[str, Any], output_path: str) -> ArtifactRef:
        """Render a quantum circuit diagram and save it to disk."""
        circuit = data["circuit"]
        export_formats = data.get("export_formats", ["png"])
        data.get("analysis", {}).get("experiment_parameters", {}) or {}

        fig = circuit.draw(output="mpl")
        # Annotate with depth and gate count
        depth = circuit.depth()
        num_gates = len(circuit.data)
        fig.text(
            0.99,
            0.01,
            f"Depth: {depth}  |  Gates: {num_gates}",
            ha="right",
            va="bottom",
            fontsize=9,
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


# ---------------------------------------------------------------------------
# MetricsSummaryRenderer
# ---------------------------------------------------------------------------


class MetricsSummaryRenderer(VisualizationRenderer):
    """Render a horizontal bar chart of structured decoherence metrics."""

    def can_render(self, viz_type: str, data: dict[str, Any]) -> bool:
        """Return True if a metrics bundle is available for a metrics summary."""
        if viz_type != "metrics_summary":
            return False
        mb = data.get("metrics_bundle")
        return mb is not None and isinstance(mb, dict) and bool(mb.get("metrics"))

    def render(self, data: dict[str, Any], output_path: str) -> ArtifactRef:
        """Render the metrics summary bar chart and return its artifact reference."""
        mb = data["metrics_bundle"]
        metrics = mb.get("metrics", {})
        params = data.get("analysis", {}).get("experiment_parameters", {})
        export_formats = data.get("export_formats", ["png"])

        SHORT_NAMES = {
            "structure_score": "SS",
            "total_correlation": "TC",
            "concentration_index": "CI",
            "entanglement_error_correlation": "EEC",
            "asymmetry_index": "AI",
            "pathway_concentration_ratio": "PCR",
            "temporal_pathway_stability": "TPS",
            "complexity_emergence_score": "CES",
            "pathway_persistence": "PP",
            "noise_topology_correlation": "NTC",
        }

        # Extract metrics with values, CIs, and filter out zeros
        entries = []
        for name, entry in metrics.items():
            if isinstance(entry, dict):
                val = entry.get("value")
                ci = entry.get("ci95")
            else:
                val = getattr(entry, "value", None)
                ci = getattr(entry, "ci95", None)

            if val is None or not isinstance(val, (int, float)):
                continue
            val = float(val)

            # Filter out zero-value metrics (uninformative)
            if abs(val) < 1e-6:
                continue

            short = SHORT_NAMES.get(name, name)
            ci_lo = float(ci[0]) if ci and len(ci) == 2 else None
            ci_hi = float(ci[1]) if ci and len(ci) == 2 else None
            entries.append((short, val, ci_lo, ci_hi))

        if not entries:
            raise ValueError("No non-zero metrics to render")

        # Sort by value descending (most interesting first)
        entries.sort(key=lambda x: -abs(x[1]))

        # Split into normalized (0-1 range) and unbounded (CI, PCR > 2)
        norm = [(n, v, lo, hi) for n, v, lo, hi in entries if n not in ("CI", "PCR") or v <= 2.0]
        big = [(n, v, lo, hi) for n, v, lo, hi in entries if n in ("CI", "PCR") and v > 2.0]

        has_big = bool(big)
        n_rows = max(len(norm), 1)
        if has_big:
            fig, (ax_norm, ax_big) = plt.subplots(
                1,
                2,
                figsize=(11, max(2.5, n_rows * 0.55)),
                gridspec_kw={"width_ratios": [3, 1]},
            )
        else:
            fig, ax_norm = plt.subplots(figsize=(8, max(2.5, n_rows * 0.55)))
            ax_big = None

        # Color: green if CI doesn't include zero (significant), amber if marginal, gray otherwise
        def _color(val: float, ci_lo: float | None, ci_hi: float | None) -> str:
            if ci_lo is not None and ci_lo > 0:
                return "#27ae60"  # significant (CI above zero)
            if val > 0.3:
                return "#2ecc71"  # strong value
            if val > 0.05:
                return "#f39c12"  # moderate
            return "#bdc3c7"  # weak

        # --- Normalized panel ---
        if norm:
            n_names = [e[0] for e in norm]
            n_vals = [e[1] for e in norm]
            n_colors = [_color(e[1], e[2], e[3]) for e in norm]

            # CI error bars (asymmetric)
            xerr_lo = [max(0, e[1] - e[2]) if e[2] is not None else 0 for e in norm]
            xerr_hi = [max(0, e[3] - e[1]) if e[3] is not None else 0 for e in norm]
            has_ci = any(x > 0 for x in xerr_lo + xerr_hi)

            bars = ax_norm.barh(
                range(len(n_names)),
                n_vals,
                color=n_colors,
                edgecolor="white",
                height=0.55,
                xerr=[xerr_lo, xerr_hi] if has_ci else None,
                error_kw={"capsize": 3, "color": "#555", "linewidth": 1},
            )

            ax_norm.set_yticks(range(len(n_names)))
            ax_norm.set_yticklabels(n_names, fontsize=11, fontweight="bold")
            ax_norm.set_xlabel("Value", fontsize=10)
            ax_norm.set_title("Structure Metrics", fontsize=11, fontweight="bold")
            ax_norm.invert_yaxis()

            # Reference lines for context
            max_norm = max(n_vals) if n_vals else 1
            if max_norm <= 1.5:
                ax_norm.axvline(0.5, color="#aaa", linestyle="--", linewidth=0.8, alpha=0.5)
                ax_norm.axvline(0.1, color="#ddd", linestyle=":", linewidth=0.8, alpha=0.5)
                ax_norm.set_xlim(0, max(max_norm * 1.35, 0.6))
            else:
                ax_norm.set_xlim(0, max_norm * 1.35)

            ax_norm.grid(axis="x", alpha=0.2)

            for bar, val in zip(bars, n_vals, strict=True):
                label = f"{val:.4f}" if val < 10 else f"{val:.2f}"
                ax_norm.text(
                    bar.get_width() + max_norm * 0.04,
                    bar.get_y() + bar.get_height() / 2,
                    label,
                    va="center",
                    fontsize=9,
                    color="#333",
                )

        # --- Unbounded panel (CI, PCR) ---
        if ax_big and big:
            b_names = [e[0] for e in big]
            b_vals = [e[1] for e in big]
            b_colors = ["#27ae60" for _ in big]

            bars = ax_big.barh(
                range(len(b_names)), b_vals, color=b_colors, edgecolor="white", height=0.55
            )
            ax_big.set_yticks(range(len(b_names)))
            ax_big.set_yticklabels(b_names, fontsize=11, fontweight="bold")
            ax_big.set_xlabel("Value", fontsize=10)
            ax_big.set_title("Concentration", fontsize=11, fontweight="bold")
            ax_big.invert_yaxis()
            ax_big.set_xlim(0, max(b_vals) * 1.3)
            ax_big.grid(axis="x", alpha=0.2)
            for bar, val in zip(bars, b_vals, strict=True):
                ax_big.text(
                    bar.get_width() + max(b_vals) * 0.03,
                    bar.get_y() + bar.get_height() / 2,
                    f"{val:.1f}",
                    va="center",
                    fontsize=9,
                    color="#333",
                )

        fig.suptitle(_build_title(params) + " — Metrics", fontsize=12, fontweight="bold")
        fig.tight_layout(rect=(0, 0, 1, 0.93))

        saved_paths = save_figure(fig, output_path, export_formats)
        plt.close(fig)

        return ArtifactRef(
            kind="metrics_summary",
            path=saved_paths[0] if saved_paths else output_path,
            metadata={
                "renderer": "MetricsSummaryRenderer",
                "num_metrics": len(entries),
                "metrics": {e[0]: e[1] for e in entries},
                "saved_formats": [Path(p).suffix.lstrip(".") for p in saved_paths],
            },
        )


# ---------------------------------------------------------------------------
# BlochSphereRenderer
# ---------------------------------------------------------------------------


class BlochSphereRenderer(VisualizationRenderer):
    """Render Bloch sphere visualization for 1-2 qubit states."""

    def can_render(self, viz_type: str, data: dict[str, Any]) -> bool:
        """Return True for 1-2 qubit states with a statevector or density matrix."""
        if viz_type != "bloch_sphere":
            return False
        analysis = data.get("analysis", {})
        meas = analysis.get("measurement_results", {})
        params = analysis.get("experiment_parameters", {})
        n_qubits = params.get("num_qubits", 0)
        has_state = meas.get("statevector") or meas.get("density_matrix")
        return bool(has_state) and 1 <= n_qubits <= 2

    def render(self, data: dict[str, Any], output_path: str) -> ArtifactRef:
        """Render the Bloch sphere visualization and return its artifact reference."""
        analysis = data["analysis"]
        meas = analysis.get("measurement_results", {})
        params = analysis.get("experiment_parameters", {})
        export_formats = data.get("export_formats", ["png"])
        n_qubits = params.get("num_qubits", 1)

        try:
            from qiskit.quantum_info import DensityMatrix, Statevector
            from qiskit.visualization import plot_bloch_multivector

            # Reconstruct quantum state object
            if meas.get("statevector"):
                sv_data = meas["statevector"]
                sv = np.array([complex(r, i) for r, i in sv_data])
                state = Statevector(sv)
            elif meas.get("density_matrix"):
                dm_data = meas["density_matrix"]
                n = len(dm_data)
                rho = np.zeros((n, n), dtype=complex)
                for i in range(n):
                    for j in range(n):
                        r, im = dm_data[i][j]
                        rho[i, j] = complex(r, im)
                state = DensityMatrix(rho)
            else:
                raise ValueError("No statevector or density_matrix available")

            fig = plot_bloch_multivector(state)
            fig.suptitle(
                _build_title(params) + " — Bloch Sphere",
                fontsize=12,
                fontweight="bold",
                y=1.02,
            )

        except ImportError:
            # Fallback: simple text-based Bloch info
            logger.warning("Qiskit visualization not available for Bloch sphere")
            fig, ax = plt.subplots(figsize=(6, 6))
            ax.text(
                0.5,
                0.5,
                "Bloch sphere requires\nqiskit.visualization",
                ha="center",
                va="center",
                fontsize=14,
            )
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis("off")

        saved_paths = save_figure(fig, output_path, export_formats)
        plt.close(fig)

        return ArtifactRef(
            kind="bloch_sphere",
            path=saved_paths[0] if saved_paths else output_path,
            metadata={
                "renderer": "BlochSphereRenderer",
                "num_qubits": n_qubits,
                "saved_formats": [Path(p).suffix.lstrip(".") for p in saved_paths],
            },
        )
