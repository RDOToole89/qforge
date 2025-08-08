from __future__ import annotations

from typing import Optional

import matplotlib.pyplot as plt
import numpy as np


def render_density_matrix(
    density_matrix,
    *,
    state_type: Optional[str] = None,
    noise_type: Optional[str] = None,
    research_metrics: Optional[dict] = None,
    save_path: Optional[str] = None,
):
    dm = np.array(density_matrix)
    fig, ax = plt.subplots(figsize=(6, 5))
    cax = ax.imshow(np.abs(dm), cmap="viridis", interpolation="nearest")
    cb = fig.colorbar(cax, ax=ax, fraction=0.046, pad=0.04)
    cb.ax.set_ylabel("Magnitude", rotation=270, labelpad=12)
    ax.set_title(
        f"|Density Matrix|{' — ' + (state_type or '') if state_type else ''}"
        + (f" (noise: {noise_type.lower()})" if noise_type else "")
    )
    ax.grid(False)
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return save_path
    return fig
