from __future__ import annotations

from typing import Mapping, Optional, Dict, List

import matplotlib.pyplot as plt


def _quantum_color_scheme(
    states: List[str], state_type: Optional[str], num_qubits: int, noise_enabled: bool
) -> List[str]:
    if not state_type:
        return ["#4C78A8" if not noise_enabled else "#E45756"] * len(states)
    st = str(state_type).upper()
    colors: List[str] = []
    if st == "GHZ":
        ideal0 = "0" * num_qubits
        ideal1 = "1" * num_qubits
        for s in states:
            if s in {ideal0, ideal1}:
                # Emphasize expected peaks in GHZ with a strong red
                colors.append("#d9534f")
            else:
                # Non-ideal outcomes in warm orange
                colors.append("#f39c12")
        return colors
    if st == "W":
        w_states = [format(1 << i, f"0{num_qubits}b") for i in range(num_qubits)]
        for s in states:
            colors.append("#2ca02c" if s in w_states else "#98df8a")
        return colors
    if st == "BELL":
        for s in states:
            colors.append("#17becf" if s in {"00", "11"} else "#9edae5")
        return colors
    return ["#4C78A8"] * len(states)


def _ideal_distribution(state_type: Optional[str], num_qubits: int) -> Dict[str, float]:
    if not state_type:
        return {}
    st = str(state_type).upper()
    total = 2**num_qubits
    if st == "GHZ":
        ideal0 = "0" * num_qubits
        ideal1 = "1" * num_qubits
        return {
            format(i, f"0{num_qubits}b"): (
                0.5 if format(i, f"0{num_qubits}b") in {ideal0, ideal1} else 0.0
            )
            for i in range(total)
        }
    if st == "W":
        w_states = {format(1 << i, f"0{num_qubits}b") for i in range(num_qubits)}
        p = 1.0 / num_qubits
        return {
            format(i, f"0{num_qubits}b"): (
                p if format(i, f"0{num_qubits}b") in w_states else 0.0
            )
            for i in range(total)
        }
    if st == "BELL" and num_qubits == 2:
        return {"00": 0.5, "11": 0.5, "01": 0.0, "10": 0.0}
    return {}


def render_histogram(
    counts: Mapping[str, int] | Mapping[str, float],
    *,
    state_type: Optional[str] = None,
    noise_type: Optional[str] = None,
    noise_enabled: bool = True,
    num_qubits: int = 3,
    research_metrics: Optional[dict] = None,
    save_path: Optional[str] = None,
):
    # Prepare analysis payload
    try:
        from src.visualization.analysis.histogram import prepare_histogram_data

        payload = prepare_histogram_data(
            dict(counts), state_type=state_type, num_qubits=num_qubits
        )
        labels: List[str] = list(payload["states"])  # type: ignore
        values: List[float] = list(payload["probabilities"])  # type: ignore
        ideals: List[float] = list(payload.get("ideal", []))  # type: ignore
        counts_list: List[int] = list(payload.get("counts", []))  # type: ignore
        ci_low: List[float] = list(payload.get("ci_low", []))  # type: ignore
        ci_high: List[float] = list(payload.get("ci_high", []))  # type: ignore
        expected_mask: List[bool] = list(payload.get("expected_mask", []))  # type: ignore
    except Exception:
        labels, values = zip(*sorted(counts.items())) if counts else ([], [])
        ideals, counts_list, ci_low, ci_high, expected_mask = [], [], [], [], []
    fig, ax = plt.subplots(figsize=(10, 5))
    # Style similar to earlier commit: gridlines, nicer colors, edge, alpha
    bars = ax.bar(
        range(len(values)),
        list(values),
        color="#4C78A8",
        edgecolor="#2F3B52",
        alpha=0.85,
    )
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=10)
    # Rich, informative title like earlier visuals
    title_lines = []
    if state_type:
        shots_count = 0
        try:
            shots_count = int(payload.get("shots", 0))  # type: ignore
        except Exception:
            pass
        title_lines.append(
            f"{state_type} State Distribution ({num_qubits} qubits, {shots_count} shots)"
        )
    else:
        title_lines.append("Quantum State Distribution")
    subtitle = []
    if noise_enabled and noise_type:
        subtitle.append(f"with {str(noise_type).upper()} Noise")
    # Metrics summary (if provided)
    if research_metrics:
        info = research_metrics.get("information_theory", {})
        parts = []
        if "shannon_entropy" in info:
            parts.append(f"H = {info['shannon_entropy']:.3f}")
        if "normalized_entropy" in info:
            parts.append(f"norm: {info['normalized_entropy']:.3f}")
        dist = research_metrics.get("distribution_comparison", {})
        if "kl_divergence" in dist:
            parts.append(f"KL: {dist['kl_divergence']:.4f}")
        if "total_variation_distance" in dist:
            parts.append(f"TVD: {dist['total_variation_distance']:.4f}")
        if parts:
            subtitle.append(" | ".join(parts))
    ax.set_title(
        "\n".join([title_lines[0], " ".join(subtitle)]) if subtitle else title_lines[0]
    )
    is_prob = bool(values) and max(values) <= 1.0
    ax.set_ylabel("Probability" if is_prob else "Counts")
    ax.grid(axis="y", linestyle=":", alpha=0.4)
    # Ideal overlay: mark only expected states (no misleading diagonals)
    try:
        if ideals:
            idx = [i for i, v in enumerate(ideals) if v and v > 0]
            y = [ideals[i] for i in idx]
            if idx:
                # Short dashed tick at each ideal point
                for i, yy in zip(idx, y):
                    ax.hlines(yy, i - 0.3, i + 0.3, colors="k", linestyles="--", alpha=0.7)
                ax.scatter(idx, y, color="k", s=18, zorder=3, label=f"Ideal {state_type}")
                ax.legend(loc="upper right")
    except Exception:
        pass
    # Research-aware bar colors
    try:
        num_q = num_qubits or (len(labels[0]) if labels else 1)
        colors = _quantum_color_scheme(
            list(labels), state_type, int(num_q), bool(noise_enabled)
        )
        for bar, color in zip(bars, colors):
            bar.set_facecolor(color)
    except Exception:
        pass
    # Annotate top bars for quick read (only up to 10 to avoid clutter)
    try:
        import numpy as _np

        top_idx = _np.argsort(values)[-10:]
        for i in top_idx:
            ax.annotate(
                f"{values[i]:.3f}" if is_prob else str(values[i]),
                (i, values[i]),
                textcoords="offset points",
                xytext=(0, 3),
                ha="center",
                fontsize=8,
                color="#2F3B52",
            )
    except Exception:
        pass
    # Counts labels and CI whiskers
    try:
        for i, bar in enumerate(bars):
            if counts_list:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height(),
                    str(counts_list[i]),
                    ha="center",
                    va="bottom",
                    fontsize=7,
                )
            if ci_low and ci_high:
                ax.vlines(
                    i, ci_low[i], ci_high[i], colors="#444", alpha=0.8, linewidth=1.2
                )
    except Exception:
        pass
    # Expected-set highlight via edge color
    try:
        for i, is_exp in enumerate(expected_mask):
            if is_exp:
                bars[i].set_edgecolor("#BF3F3F")
                bars[i].set_linewidth(1.8)
    except Exception:
        pass
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return save_path
    return fig
