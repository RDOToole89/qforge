from __future__ import annotations

from typing import Mapping, Any, List

from src.visualization.adapters.base import VisualizationAdapter, VizKind
from src.engine.models import ArtifactRef
from src.visualization.save_manager import get_organized_save_path


class MatplotlibAdapter:
    name = "matplotlib"
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
            counts = (
                analysis.get("measurement_results", {}).get("raw_counts")
                or analysis.get("measurement_results", {}).get("counts")
                or {}
            )
            save_path = get_organized_save_path(
                viz_type="histogram",
                experiment_config={
                    "state_type": params.get("state_type"),
                    "noise_type": params.get("noise_type"),
                    "noise_enabled": params.get("noise_enabled"),
                    "num_qubits": params.get("num_qubits"),
                    "error_rate": params.get("error_rate"),
                },
                custom_name=None,
                extension="png",
            )
            from src.visualization.plots.histogram import render_histogram

            render_histogram(
                counts,
                state_type=params.get("state_type"),
                noise_type=params.get("noise_type"),
                noise_enabled=params.get("noise_enabled", True),
                num_qubits=int(params.get("num_qubits", 3) or 3),
                research_metrics=analysis.get("research_metrics"),
                save_path=save_path,
            )
            artifacts.append(
                ArtifactRef(
                    kind="histogram", path=save_path, metadata={"backend": "matplotlib"}
                )
            )
        elif kind == VizKind.density_matrix:
            sr = analysis.get("state_reconstruction", {})
            dm_obj = sr.get("density_matrix")
            if (
                dm_obj is None
                and "density_matrix_real" in sr
                and "density_matrix_imag" in sr
            ):
                # Recompose complex matrix if available
                import numpy as _np

                dm_obj = _np.array(sr["density_matrix_real"]) + 1j * _np.array(
                    sr["density_matrix_imag"]
                )
            if dm_obj is None:
                raise ValueError("No density matrix in analysis")
            from qiskit.quantum_info import DensityMatrix
            import numpy as np

            if not isinstance(dm_obj, DensityMatrix):
                dm_obj = DensityMatrix(np.array(dm_obj))
            save_path = get_organized_save_path(
                viz_type="density_matrix",
                experiment_config={
                    "state_type": params.get("state_type"),
                    "noise_type": params.get("noise_type"),
                    "num_qubits": params.get("num_qubits"),
                },
                custom_name=None,
                extension="png",
            )
            from src.visualization.plots.density_matrix import render_density_matrix

            render_density_matrix(
                dm_obj,
                state_type=params.get("state_type"),
                noise_type=params.get("noise_type"),
                research_metrics=analysis.get("research_metrics"),
                save_path=save_path,
            )
            artifacts.append(
                ArtifactRef(
                    kind="density_matrix",
                    path=save_path,
                    metadata={"backend": "matplotlib"},
                )
            )
        # Hypergraph support removed for cleanup
        else:
            raise ValueError(f"Unsupported kind: {kind}")
        return artifacts
