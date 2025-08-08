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
    fig, ax = plt.subplots(figsize=(5, 4))
    cax = ax.imshow(np.abs(dm), cmap="viridis")
    fig.colorbar(cax, ax=ax)
    ax.set_title("|Density Matrix|")
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return save_path
    return fig
