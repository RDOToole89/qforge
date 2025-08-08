from __future__ import annotations

from typing import Mapping, Optional

import matplotlib.pyplot as plt


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
    labels, values = zip(*sorted(counts.items())) if counts else ([], [])
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
    ax.set_xticklabels(labels, rotation=90)
    ax.set_title(
        f"Histogram{' — ' + (state_type or '') if state_type else ''}"
        + (f" (noise: {noise_type.lower()})" if noise_type and noise_enabled else "")
    )
    ax.set_ylabel("Probability" if values and max(values) <= 1.0 else "Counts")
    ax.grid(axis="y", linestyle=":", alpha=0.4)
    # Annotate top bars for quick read (only up to 10 to avoid clutter)
    try:
        import numpy as _np

        top_idx = _np.argsort(values)[-10:]
        for i in top_idx:
            ax.annotate(
                f"{values[i]:.3f}" if max(values) <= 1.0 else str(values[i]),
                (i, values[i]),
                textcoords="offset points",
                xytext=(0, 3),
                ha="center",
                fontsize=8,
                color="#2F3B52",
            )
    except Exception:
        pass
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return save_path
    return fig
