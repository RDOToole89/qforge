"""Multi-format figure export utility."""

from __future__ import annotations

import logging
from pathlib import Path

from matplotlib.figure import Figure

logger = logging.getLogger(__name__)


def save_figure(
    fig: Figure,
    base_path: str | Path,
    formats: list[str] | None = None,
    *,
    dpi: int = 300,
    transparent: bool = False,
) -> list[str]:
    """Save a matplotlib Figure in one or more formats.

    Args:
        fig: Matplotlib figure to save.
        base_path: Output path *without* extension (e.g. ``"out/histogram_abc123"``).
        formats: List of format strings (``"png"``, ``"pdf"``, ``"svg"``).
            Defaults to ``["png"]``.
        dpi: Resolution for raster formats.
        transparent: Transparent background.

    Returns:
        List of saved file paths (absolute strings).
    """
    if not formats:
        formats = ["png"]

    base = Path(base_path)
    base.parent.mkdir(parents=True, exist_ok=True)

    saved: list[str] = []
    for fmt in formats:
        out = base.with_suffix(f".{fmt}")
        fig.savefig(
            str(out),
            format=fmt,
            dpi=dpi,
            bbox_inches="tight",
            facecolor="white",
            transparent=transparent,
        )
        saved.append(str(out))
        logger.info("Saved %s figure to %s", fmt.upper(), out)

    return saved
