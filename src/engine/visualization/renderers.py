"""
Research-focused visualization renderers.

Each renderer is a plugin that can create specific types of visualizations
from quantum experiment data.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Tuple, List
import math

# Use a headless backend if needed (safe in GUI too)
import matplotlib

try:
    matplotlib.use("Agg")  # no-op if already set
except Exception:
    pass
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

import numpy as np

from .service import VisualizationRenderer
from src.engine.models import ArtifactRef

logger = logging.getLogger(__name__)


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
      }
    """

    def can_render(self, viz_type: str, data: Dict[str, Any]) -> bool:
        """Check if this is a histogram request with measurement counts/probabilities."""
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

    def render(self, data: Dict[str, Any], output_path: str) -> ArtifactRef:
        """Render research-focused histogram and return an ArtifactRef."""
        # ------- Extract inputs -------
        analysis = data.get("analysis", {})
        measurement_results = analysis.get("measurement_results", {})
        experiment_params = analysis.get("experiment_parameters", {}) or {}
        research_metrics = data.get("structured_decoherence_metrics")

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

        # ------- Determine counts vs probabilities -------
        is_prob, normalized_counts = self._normalize_if_probs(counts)

        # ------- Reduce cardinality if needed (top-K + OTHER) -------
        reduced_labels, reduced_values, used_other = self._compact_top_k(
            normalized_counts, top_k=top_k, sort_mode=sort_mode
        )

        # ------- Plot -------
        fig, ax = plt.subplots(figsize=(10, 6))

        indices = np.arange(len(reduced_labels))
        bars = ax.bar(indices, reduced_values, linewidth=0.5)

        # Style
        for b in bars:
            b.set_alpha(0.9)
        # Use a neutral color; downstream themes can recolor if needed
        # (keeping default matplotlib color cycle for variety across runs)

        # Axis labeling
        ax.set_xlabel("Measurement Outcomes", fontsize=12, fontweight="bold")
        ax.set_ylabel(
            "Probability" if is_prob else "Counts", fontsize=12, fontweight="bold"
        )

        # Ticks
        ax.set_xticks(indices)
        rot = 45 if len(reduced_labels) > 12 else 0
        ax.set_xticklabels(
            reduced_labels, rotation=rot, ha="right" if rot else "center"
        )

        # Format large integers nicely
        if not is_prob:
            ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{int(x):,}"))
        else:
            ax.set_ylim(0, min(1.0, max(0.05, max(reduced_values) * 1.15)))

        # Title
        ax.set_title(
            self._build_title(experiment_params), fontsize=14, fontweight="bold", pad=20
        )

        # Research metrics annotation
        self._annotate_metrics(ax, research_metrics)

        # Highlight top bars if PCR indicates concentration
        if research_metrics:
            try:
                pcr = float(research_metrics.get("pathway_concentration_ratio", 1.0))
            except Exception:
                pcr = 1.0
            if pcr > 2.0 and highlight_top_n > 0:
                top_idx = np.argsort(reduced_values)[::-1][:highlight_top_n]
                for i in top_idx:
                    bars[i].set_edgecolor("black")
                    bars[i].set_linewidth(1.5)
                    bars[i].set_alpha(1.0)

        # Grid + layout
        ax.grid(True, axis="y", alpha=0.3)
        plt.tight_layout()

        # ------- Save -------
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(
            out,
            dpi=300,
            bbox_inches="tight",
            facecolor="white",
            transparent=transparent,
        )
        plt.close(fig)

        logger.info(f"Saved research histogram to {out}")

        # ------- Artifact metadata -------
        meta_total_shots = None
        if not is_prob:
            try:
                # only report shots when original looked like integer counts
                if self._looks_like_counts(counts):
                    meta_total_shots = int(sum(int(v) for v in counts.values()))
            except Exception:
                meta_total_shots = None

        return ArtifactRef(
            kind="histogram",
            path=str(out),
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
            },
        )

    # ----------------- helpers -----------------

    def _build_title(self, params: Dict[str, Any]) -> str:
        parts: List[str] = []
        st = params.get("state_type")
        if st:
            parts.append(f"{str(st).upper()} State")
        nq = params.get("num_qubits")
        if isinstance(nq, int) and nq > 0:
            parts.append(f"({nq} qubits)")

        if params.get("noise_enabled"):
            noise_type = (
                str(params.get("noise_type", "noise")).replace("_", " ").title()
            )
            er = params.get("error_rate")
            if isinstance(er, (int, float)):
                parts.append(f"{noise_type} (p={er:.3f})")
            else:
                parts.append(noise_type)

        return " - ".join(parts) if parts else "Measurement Results"

    def _annotate_metrics(self, ax, metrics: Dict[str, Any] | None) -> None:
        if not metrics:
            return
        text_bits = []
        ai = metrics.get("asymmetry_index")
        pcr = metrics.get("pathway_concentration_ratio")
        eec = metrics.get("entanglement_error_correlation")
        try:
            if ai is not None:
                text_bits.append(f"AI: {float(ai):.3f}")
            if pcr is not None:
                text_bits.append(f"PCR: {float(pcr):.3f}")
            if eec is not None:
                text_bits.append(f"EEC: {float(eec):.3f}")
        except Exception:
            # Be forgiving if types are unexpected
            pass

        if text_bits:
            ax.text(
                0.02,
                0.98,
                "Research Metrics: " + " | ".join(text_bits),
                transform=ax.transAxes,
                fontsize=10,
                va="top",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="0.9", edgecolor="0.8"),
            )

    def _normalize_if_probs(
        self, counts: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, float]]:
        """
        Decide if mapping looks like probabilities or raw counts.
        Returns (is_probability, mapping suitable for plotting).
        """
        vals = list(counts.values())
        # graceful empty guard
        if not vals:
            return False, {}

        # Coerce to float when possible
        def _to_float(x):
            try:
                return float(x)
            except Exception:
                return math.nan

        fvals = [_to_float(v) for v in vals]
        finite = [v for v in fvals if math.isfinite(v)]
        if not finite:
            # fallback: treat as zero
            return False, {k: 0.0 for k in counts.keys()}

        total = sum(finite)
        # heuristics
        looks_prob = 0.98 <= total <= 1.02 and all(0.0 <= v <= 1.0 for v in finite)
        looks_counts = self._looks_like_counts(counts)

        if looks_prob and not looks_counts:
            # Already probabilities (normalize slight drift)
            norm = total if total != 0 else 1.0
            return True, {
                k: (
                    float(counts[k]) / norm
                    if math.isfinite(_to_float(counts[k]))
                    else 0.0
                )
                for k in counts.keys()
            }
        else:
            # Treat as counts (keep as floats for plotting); don't normalize
            return False, {
                k: float(counts[k]) if math.isfinite(_to_float(counts[k])) else 0.0
                for k in counts.keys()
            }

    def _looks_like_counts(self, counts: Dict[str, Any]) -> bool:
        """Heuristic: values are all near integers and sum is reasonably > 1."""
        vals = list(counts.values())
        if not vals:
            return False
        try:
            fvals = [float(v) for v in vals]
        except Exception:
            return False
        # sum much greater than 1 and most entries very close to integers
        if sum(fvals) <= 1.5:
            return False
        near_int = sum(1 for v in fvals if abs(v - round(v)) < 1e-6)
        return near_int / len(fvals) >= 0.95

    def _compact_top_k(
        self,
        mapping: Dict[str, float],
        top_k: int,
        sort_mode: str = "value_desc",
    ) -> Tuple[List[str], List[float], bool]:
        """Return (labels, values, used_other_bucket)."""
        items = list(mapping.items())
        if sort_mode == "bitstring":
            items.sort(key=lambda kv: kv[0])
        else:  # value_desc default
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
