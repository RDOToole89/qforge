from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Mapping, Any

from src.engine.models import ArtifactRef
from src.visualization.adapters.base import VizKind, VisualizationAdapter
from src.visualization.adapters.matplotlib_adapter import MatplotlibAdapter
# PlotlyAdapter removed - using matplotlib only


@dataclass
class VizRequest:
    viz_type: str = "histogram"
    backend: str = "matplotlib"
    output_base_dir: Optional[str] = None


class VisualizationService:
    """Facade for visualization rendering with adapters."""

    def __init__(self, default_backend: str = "matplotlib") -> None:
        self._default_backend = default_backend
        self._adapters: dict[str, VisualizationAdapter] = {
            "matplotlib": MatplotlibAdapter(),
        }

    def render_from_json(self, json_path: str, request: VizRequest) -> ArtifactRef:
        import json
        from pathlib import Path
        from src.visualization.save_manager import set_save_manager_base_dir

        if request.output_base_dir:
            try:
                set_save_manager_base_dir(request.output_base_dir)
            except Exception:
                pass
        analysis = json.loads(Path(json_path).read_text(encoding="utf-8"))
        return self.render_from_analysis(analysis, request)

    def render_from_analysis(
        self, analysis: Mapping[str, Any], request: VizRequest
    ) -> ArtifactRef:
        kind = VizKind(request.viz_type)
        backend = (request.backend or self._default_backend).lower()
        adapter = self._adapters.get(backend)
        if adapter is None or kind not in adapter.supported_kinds:
            # fallback to matplotlib when unsupported
            adapter = self._adapters["matplotlib"]
        artifacts = adapter.render_from_analysis(analysis, kind, options={})
        if not artifacts:
            raise ValueError("Adapter produced no artifacts")
        return artifacts[0]
