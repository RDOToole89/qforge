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
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(range(len(values)), list(values), color="#4C78A8")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=90)
    ax.set_title("Histogram")
    ax.set_ylabel("Probability" if values and max(values) <= 1.0 else "Counts")
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return save_path
    return fig
