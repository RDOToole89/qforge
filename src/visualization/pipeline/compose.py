from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from src.engine.viz_service import VisualizationRequest


@dataclass
class ComposeContext:
    viz_type: str
    backend: str = "matplotlib"
    output_base_dir: Optional[str] = None


def build_request(ctx: ComposeContext) -> VisualizationRequest:
    return VisualizationRequest(
        viz_type=ctx.viz_type,
        backend=ctx.backend,
        output_base_dir=ctx.output_base_dir,
    )
