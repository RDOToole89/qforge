from __future__ import annotations

from typing import Mapping, Any, List

from src.visualization.adapters.base import VisualizationAdapter, VizKind
from src.engine.models import ArtifactRef
from src.visualization.save_manager import get_organized_save_path


class PlotlyAdapter:
    name = "plotly"
    supported_kinds = {VizKind.histogram, VizKind.density_matrix}

    def render_from_analysis(
        self,
        analysis: Mapping[str, Any],
        kind: VizKind,
        options: Mapping[str, Any] | None = None,
    ) -> List[ArtifactRef]:
        options = options or {}
        params = analysis.get("experiment_parameters", {})
        artifacts: List[ArtifactRef] = []
        if kind == VizKind.histogram:
            from src.visualization.backends.plotly_backend import (
                plot_interactive_histogram,
            )

            counts = (
                analysis.get("measurement_results", {}).get("raw_counts")
                or analysis.get("measurement_results", {}).get("counts")
                or {}
            )
            save_path = get_organized_save_path(
                viz_type="research",
                experiment_config={
                    "state_type": params.get("state_type"),
                    "noise_type": params.get("noise_type"),
                    "num_qubits": params.get("num_qubits"),
                },
                custom_name="histogram_interactive",
                extension="html",
            )
            fig = plot_interactive_histogram(
                counts=counts,
                state_type=params.get("state_type"),
                noise_type=params.get("noise_type"),
                research_metrics=analysis.get("research_metrics"),
            )
            if fig is not None and hasattr(fig, "write_html"):
                fig.write_html(save_path)
                artifacts.append(
                    ArtifactRef(
                        kind="histogram", path=save_path, metadata={"backend": "plotly"}
                    )
                )
        elif kind == VizKind.density_matrix:
            from src.visualization.backends.plotly_backend import (
                plot_interactive_density_matrix,
            )

            dm_obj = analysis.get("state_reconstruction", {}).get("density_matrix")
            if dm_obj is None:
                raise ValueError("No density matrix in analysis")
            save_path = get_organized_save_path(
                viz_type="research",
                experiment_config={
                    "state_type": params.get("state_type"),
                    "noise_type": params.get("noise_type"),
                    "num_qubits": params.get("num_qubits"),
                },
                custom_name="density_matrix_interactive",
                extension="html",
            )
            fig = plot_interactive_density_matrix(
                dm_obj,
                state_type=params.get("state_type"),
                research_metrics=analysis.get("research_metrics"),
            )
            if fig is not None and hasattr(fig, "write_html"):
                fig.write_html(save_path)
                artifacts.append(
                    ArtifactRef(
                        kind="density_matrix",
                        path=save_path,
                        metadata={"backend": "plotly"},
                    )
                )
        else:
            raise ValueError(f"Unsupported kind: {kind}")
        return artifacts
