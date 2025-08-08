from __future__ import annotations

from typing import Mapping, Any, Optional

from src.visualization.pipeline.io import read_analysis_json, configure_output_base_dir
from src.visualization.pipeline.compose import ComposeContext, build_request
from src.visualization.service import VisualizationService


def render_from_json(
    json_path: str,
    *,
    viz_type: str,
    backend: str = "matplotlib",
    output_base_dir: Optional[str] = None,
):
    configure_output_base_dir(output_base_dir)
    analysis = read_analysis_json(json_path)
    svc = VisualizationService(default_backend=backend)
    req = build_request(
        ComposeContext(
            viz_type=viz_type, backend=backend, output_base_dir=output_base_dir
        )
    )
    return svc.render_from_analysis(analysis, request=req)


def render_from_analysis(
    analysis: Mapping[str, Any],
    *,
    viz_type: str,
    backend: str = "matplotlib",
    output_base_dir: Optional[str] = None,
):
    configure_output_base_dir(output_base_dir)
    svc = VisualizationService(default_backend=backend)
    req = build_request(
        ComposeContext(
            viz_type=viz_type, backend=backend, output_base_dir=output_base_dir
        )
    )
    return svc.render_from_analysis(analysis, request=req)
