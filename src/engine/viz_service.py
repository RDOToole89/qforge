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
        request = request or VisualizationRequest(
            viz_type="histogram", backend=self.default_backend
        )

        path_obj = Path(analysis_json_path)
        try:
            analysis = json.loads(path_obj.read_text(encoding="utf-8"))
        except Exception as e:
            raise ValueError(
                f"Failed to read analysis JSON '{analysis_json_path}': {e}"
            ) from e

        # If no explicit output_base_dir, infer run_dir/visualizations from analysis path
        if request and not request.output_base_dir:
            try:
                # Expect .../results/YYYYMMDD/HHMMSS_slug/analysis/analysis.json
                if path_obj.parent.name == "analysis":
                    run_dir = path_obj.parent.parent
                    inferred = run_dir / "visualizations"
                    from src.visualization.save_manager import set_save_manager_base_dir

                    set_save_manager_base_dir(str(inferred))
            except Exception:
                pass

        return self.render_from_analysis(analysis, request=request)

    def render_from_analysis(
        self, analysis: Dict[str, Any], request: Optional[VisualizationRequest] = None
    ) -> ArtifactRef:
        """Render visualization directly from the analysis dict.

        Chooses the appropriate adapter based on request.viz_type.
        """
        request = request or VisualizationRequest(
            viz_type="histogram", backend=self.default_backend
        )

        viz_type = request.viz_type
        if viz_type == "histogram":
            return self._render_histogram(analysis, request)
        elif viz_type == "density_matrix":
            return self._render_density_matrix(analysis, request)
        elif viz_type == "hypergraph":
            return self._render_hypergraph(analysis, request)
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
                logger.warning(
                    f"Could not set save base dir to '{request.output_base_dir}': {e}"
                )

    def _render_histogram(
        self, analysis: Dict[str, Any], request: VisualizationRequest
    ) -> ArtifactRef:
        self._resolve_paths(request)

        params = analysis.get("experiment_parameters", {})
        counts = (
            analysis.get("measurement_results", {}).get("raw_counts")
            or analysis.get("measurement_results", {}).get("counts")
            or {}
        )
        if not counts:
            raise ValueError(
                "Analysis does not contain measurement counts for histogram visualization"
            )

        # Compute a save path using the save manager
        from src.visualization.save_manager import get_organized_save_path

        if request.backend == "plotly":
            # Try Plotly adapter
            try:
                from src.visualization.backends.plotly_backend import plot_interactive_histogram  # type: ignore

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
                # If fig is available, persist it; otherwise fallback
                if fig is not None and hasattr(fig, "write_html"):
                    fig.write_html(save_path)
                    return ArtifactRef(
                        kind="histogram", path=save_path, metadata={"backend": "plotly"}
                    )
            except Exception as e:
                logger.warning(f"Plotly histogram fallback to matplotlib due to: {e}")

        # Matplotlib fallback / default
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
        return ArtifactRef(
            kind="histogram", path=save_path, metadata={"backend": "matplotlib"}
        )

    def _render_density_matrix(
        self, analysis: Dict[str, Any], request: VisualizationRequest
    ) -> ArtifactRef:
        self._resolve_paths(request)

        # Expect a density matrix presence under a conventional key if available
        dm_obj = analysis.get("state_reconstruction", {}).get("density_matrix")
        if dm_obj is None:
            raise ValueError(
                "Analysis does not contain a density matrix for density_matrix visualization"
            )

        # Construct a DensityMatrix object if necessary
        density_matrix = dm_obj
        try:
            from qiskit.quantum_info import DensityMatrix
            import numpy as np

            if not isinstance(dm_obj, DensityMatrix):
                density_matrix = DensityMatrix(np.array(dm_obj))
        except Exception as e:
            raise ValueError(
                f"Failed to construct DensityMatrix from analysis: {e}"
            ) from e

        params = analysis.get("experiment_parameters", {})

        from src.visualization.save_manager import get_organized_save_path

        if request.backend == "plotly":
            try:
                from src.visualization.backends.plotly_backend import plot_interactive_density_matrix  # type: ignore

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
                    density_matrix,
                    state_type=params.get("state_type"),
                    research_metrics=analysis.get("research_metrics"),
                )
                if fig is not None and hasattr(fig, "write_html"):
                    fig.write_html(save_path)
                    return ArtifactRef(
                        kind="density_matrix",
                        path=save_path,
                        metadata={"backend": "plotly"},
                    )
            except Exception as e:
                logger.warning(f"Plotly density fallback to matplotlib due to: {e}")

        # Matplotlib fallback / default
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
            density_matrix,
            state_type=params.get("state_type"),
            noise_type=params.get("noise_type"),
            research_metrics=analysis.get("research_metrics"),
            save_path=save_path,
        )
        return ArtifactRef(
            kind="density_matrix", path=save_path, metadata={"backend": "matplotlib"}
        )

    def _render_hypergraph(
        self, analysis: Dict[str, Any], request: VisualizationRequest
    ) -> ArtifactRef:
        self._resolve_paths(request)

        params = analysis.get("experiment_parameters", {})
        counts = (
            analysis.get("measurement_results", {}).get("raw_counts")
            or analysis.get("measurement_results", {}).get("counts")
            or {}
        )
        if not counts:
            raise ValueError(
                "Analysis does not contain measurement counts required for hypergraph visualization"
            )

        from src.visualization.save_manager import get_organized_save_path

        save_path = get_organized_save_path(
            viz_type="hypergraph",
            experiment_config={
                "state_type": params.get("state_type"),
                "noise_type": params.get("noise_type"),
                "num_qubits": params.get("num_qubits"),
            },
            custom_name=None,
            extension="png",
        )

        # Route through hypergraphs drawer (delegates to monolith for now)
        from src.visualization.plots.hypergraph import draw_hypergraph

        # Minimal config; users can later pass more via request metadata if needed
        draw_hypergraph(
            correlation_data=counts,
            state_type=params.get("state_type"),
            noise_type=params.get("noise_type"),
            save_path=save_path,
            config={},
        )

        # Ensure an artifact exists; if no significant correlations, the module may skip saving
        from pathlib import Path as _Path

        if not _Path(save_path).exists():
            try:
                import matplotlib.pyplot as _plt

                _plt.figure(figsize=(6, 4))
                _plt.title("No significant correlations found")
                _plt.text(0.5, 0.5, "No edges to plot", ha="center", va="center")
                _plt.axis("off")
                _plt.tight_layout()
                _plt.savefig(save_path, dpi=200, bbox_inches="tight")
                _plt.close()
            except Exception as e:
                logger.warning(f"Failed to save placeholder hypergraph: {e}")

        return ArtifactRef(
            kind="hypergraph", path=save_path, metadata={"backend": "matplotlib"}
        )
