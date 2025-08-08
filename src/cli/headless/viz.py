from __future__ import annotations

from typing import Optional

from main import visualize_from_json as legacy_viz


def render_from_json(
    path: str,
    viz_type: Optional[str] = None,
    backend: Optional[str] = None,
    outdir: Optional[str] = None,
) -> None:
    legacy_viz(path, viz_type=viz_type, backend=backend, outdir=outdir)
