# src/engine/viz_service.py

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
import json
import logging

from src.engine.models import ArtifactRef

logger = logging.getLogger("QuantumExperiment.Engine.VisualizationService")


@dataclass
class VisualizationRequest:
    """Request describing what to visualize.

    Attributes:
        viz_type: One of 'histogram' | 'density_matrix'.
        backend: Preferred backend; currently 'matplotlib' supported for saving.
        output_base_dir: Optional override for save base directory.
    """

    viz_type: str = "histogram"
    backend: str = "matplotlib"
    output_base_dir: Optional[str] = None


class VisualizationService:
    """Service that renders visualizations from engine analysis outputs.

    This wraps existing visualization modules and returns saved artifact references.
    """

    def __init__(self, default_backend: str = "matplotlib") -> None:
        self.default_backend = default_backend

    def render_from_json(
        self, analysis_json_path: str, request: Optional[VisualizationRequest] = None
    ) -> ArtifactRef:
        """Render a visualization from a saved analysis JSON file.

        Args:
            analysis_json_path: Path to a results JSON as produced by ResearchExperimentHandler/storage.
            request: Visualization parameters; defaults are applied if None.

        Returns:
            ArtifactRef pointing to the saved visualization artifact.
        """
        request = request or VisualizationRequest(viz_type="histogram", backend=self.default_backend)

        try:
            analysis = json.loads(Path(analysis_json_path).read_text(encoding="utf-8"))
        except Exception as e:
            raise ValueError(f"Failed to read analysis JSON '{analysis_json_path}': {e}") from e

        return self.render_from_analysis(analysis, request=request)

    def render_from_analysis(
        self, analysis: Dict[str, Any], request: Optional[VisualizationRequest] = None
    ) -> ArtifactRef:
        """Render visualization directly from the analysis dict.

        Chooses the appropriate adapter based on request.viz_type.
        """
        request = request or VisualizationRequest(viz_type="histogram", backend=self.default_backend)

        viz_type = request.viz_type
        if viz_type == "histogram":
            return self._render_histogram(analysis, request)
        elif viz_type == "density_matrix":
            return self._render_density_matrix(analysis, request)
        else:
            raise ValueError(f"Unsupported visualization type: {viz_type}")

    # Internal helpers

    def _resolve_paths(self, request: VisualizationRequest) -> None:
        """Optionally override the visualization base directory via save_manager."""
        if request.output_base_dir:
            try:
                from src.visualization.save_manager import set_save_manager_base_dir

                set_save_manager_base_dir(request.output_base_dir)
            except Exception as e:
                logger.warning(f"Could not set save base dir to '{request.output_base_dir}': {e}")

    def _render_histogram(self, analysis: Dict[str, Any], request: VisualizationRequest) -> ArtifactRef:
        self._resolve_paths(request)

        params = analysis.get("experiment_parameters", {})
        counts = (
            analysis.get("measurement_results", {}).get("raw_counts")
            or analysis.get("measurement_results", {}).get("counts")
            or {}
        )
        if not counts:
            raise ValueError("Analysis does not contain measurement counts for histogram visualization")

        # Compute a save path using the save manager
        from src.visualization.save_manager import get_organized_save_path

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

        # Render via matplotlib histogram module for persisted artifact
        from src.visualization.histogram import plot_histogram

        plot_histogram(
            counts=counts,
            state_type=params.get("state_type"),
            noise_type=params.get("noise_type"),
            noise_enabled=params.get("noise_enabled", True),
            num_qubits=int(params.get("num_qubits", 3) or 3),
            research_metrics=analysis.get("research_metrics"),
            save_path=save_path,
        )

        return ArtifactRef(kind="histogram", path=save_path, metadata={"backend": "matplotlib"})

    def _render_density_matrix(
        self, analysis: Dict[str, Any], request: VisualizationRequest
    ) -> ArtifactRef:
        self._resolve_paths(request)

        # Expect a density matrix presence under a conventional key if available
        dm_obj = analysis.get("state_reconstruction", {}).get("density_matrix")
        if dm_obj is None:
            raise ValueError("Analysis does not contain a density matrix for density_matrix visualization")

        # Construct a DensityMatrix object if necessary
        density_matrix = dm_obj
        try:
            from qiskit.quantum_info import DensityMatrix
            import numpy as np

            if not isinstance(dm_obj, DensityMatrix):
                density_matrix = DensityMatrix(np.array(dm_obj))
        except Exception as e:
            raise ValueError(f"Failed to construct DensityMatrix from analysis: {e}") from e

        params = analysis.get("experiment_parameters", {})

        from src.visualization.save_manager import get_organized_save_path

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

        from src.visualization.density_matrix import plot_density_matrix

        plot_density_matrix(
            density_matrix=density_matrix,
            state_type=params.get("state_type"),
            noise_type=params.get("noise_type"),
            research_metrics=analysis.get("research_metrics"),
            save_path=save_path,
        )

        return ArtifactRef(kind="density_matrix", path=save_path, metadata={"backend": "matplotlib"})