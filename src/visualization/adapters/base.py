from __future__ import annotations

from enum import Enum
from typing import Protocol, Mapping, Any, List

from src.engine.models import ArtifactRef


class VizKind(str, Enum):
    histogram = "histogram"
    density_matrix = "density_matrix"


class VisualizationAdapter(Protocol):
    name: str
    supported_kinds: set[VizKind]

    def render_from_analysis(
        self,
        analysis: Mapping[str, Any],
        kind: VizKind,
        options: Mapping[str, Any] | None = None,
    ) -> List[ArtifactRef]: ...
