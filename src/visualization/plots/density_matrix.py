from __future__ import annotations

from typing import Optional, Dict

import matplotlib.pyplot as plt
import numpy as np


def render_density_matrix(
    density_matrix,
    *,
    state_type: Optional[str] = None,
    noise_type: Optional[str] = None,
    research_metrics: Optional[Dict] = None,
    save_path: Optional[str] = None,
):
    dm = np.array(density_matrix)
    fig, ax = plt.subplots(figsize=(12, 10))
    # Visual style inspired by earlier commit: viridis, grid overlay, labeled axes
    cax = ax.imshow(np.abs(dm), cmap="viridis", interpolation="nearest")
    cb = fig.colorbar(cax, ax=ax, fraction=0.046, pad=0.04)
    cb.ax.set_ylabel("Absolute Value", rotation=270, labelpad=12)
    title = "Density Matrix - Magnitude"
    if state_type:
        title += f" ({state_type if state_type != 'CUSTOM' else 'CUSTOM State'})"
    if noise_type:
        title += f" with {noise_type.upper()} Noise"
    ax.set_title(title)
    # Axis tick labels as basis states when size permits
    try:
        n = int(np.log2(dm.shape[0]))
        labels = [f"|{format(i, f'0{n}b')}⟩" for i in range(2**n)]
        ax.set_xticks(range(2**n))
        ax.set_yticks(range(2**n))
        ax.set_xticklabels(labels, rotation=45, ha="right")
        ax.set_yticklabels(labels)
    except Exception:
        pass
    ax.set_xlabel("Basis State ⟨j|")
    ax.set_ylabel("Basis State |i⟩")
    ax.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.25)
    # Optional research metrics box
    if research_metrics:
        info = research_metrics.get("information_theory", {})
        text_lines = []
        if "purity" in info:
            text_lines.append(f"Purity: {info['purity']:.4f}")
        if "von_neumann_entropy" in info:
            text_lines.append(f"Von Neumann Entropy: {info['von_neumann_entropy']:.4f}")
        if not text_lines:
            if "shannon_entropy" in info:
                text_lines.append(f"H: {info['shannon_entropy']:.3f}")
            if "normalized_entropy" in info:
                text_lines.append(f"Hn: {info['normalized_entropy']:.3f}")
        if text_lines:
            ax.text(
                0.98,
                0.02,
                "\n".join(text_lines),
                transform=ax.transAxes,
                ha="right",
                va="bottom",
                fontsize=9,
                bbox=dict(
                    boxstyle="round,pad=0.5",
                    facecolor="white",
                    alpha=0.9,
                    edgecolor="gray",
                ),
            )
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return save_path
    return fig
