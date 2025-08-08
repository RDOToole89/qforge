# src/cli/interactive/viz.py

from __future__ import annotations

from typing import Any, Dict


class VisualizationOrchestrator:
    """Encapsulates visualization selection and rendering for interactive CLI."""

    def __init__(self, display_manager):
        self.display_manager = display_manager

    def show(self, results: Dict[str, Any], params: Dict[str, Any], viz_type: str) -> None:
        try:
            self.display_manager.display_info_message(
                f"🎨 Generating {viz_type} visualization..."
            )

            # Determine counts (for histogram/hypergraph)
            if viz_type == "density_matrix":
                counts = {}
            else:
                if hasattr(results, "get"):
                    counts = results.get("counts", {})
                else:
                    self.display_manager.display_warning_message(
                        "⚠️ No measurement data available for visualization"
                    )
                    return
                if not counts:
                    self.display_manager.display_warning_message(
                        "⚠️ No measurement data available for visualization"
                    )
                    return

            num_qubits = params.get("num_qubits", 3)
            state_type = params.get("state_type", "GHZ")
            noise_type = params.get("noise_type", "DEPOLARIZING")
            noise_enabled = params.get("noise_enabled", True)

            if viz_type == "histogram":
                from src.visualization import get_histogram_visualizer

                plot_function = get_histogram_visualizer()

                research_metrics = None
                if hasattr(self, "_last_research_analysis"):
                    research_metrics = self._last_research_analysis.get(
                        "research_metrics"
                    )

                plot_function(
                    counts=counts,
                    state_type=state_type,
                    noise_type=noise_type,
                    noise_enabled=noise_enabled,
                    num_qubits=num_qubits,
                    research_metrics=research_metrics,
                    save_path=None,
                )

            elif viz_type == "density_matrix":
                from src.visualization import get_density_matrix_visualizer

                if params.get("sim_mode") != "density":
                    self.display_manager.display_warning_message(
                        "⚠️ Density matrix visualization requires density simulation mode"
                    )
                    return

                if hasattr(results, "data") and hasattr(results, "draw"):
                    density_matrix = results
                elif isinstance(results, dict) and "density_matrix" in results:
                    density_matrix = results["density_matrix"]
                else:
                    self.display_manager.display_warning_message(
                        "⚠️ No density matrix data available"
                    )
                    return

                research_metrics = None
                if hasattr(self, "_last_research_analysis"):
                    research_metrics = self._last_research_analysis.get(
                        "research_metrics"
                    )

                plot_function = get_density_matrix_visualizer()
                plot_function(
                    density_matrix,
                    state_type=state_type,
                    noise_type=noise_type,
                    research_metrics=research_metrics,
                )

            elif viz_type == "hypergraph":
                from src.visualization import get_hypergraph_visualizer

                plot_function = get_hypergraph_visualizer()
                plot_function(
                    correlation_data=counts,
                    state_type=state_type,
                    noise_type=noise_type,
                    config={},
                )

            self.display_manager.display_success_message(
                f"✅ {viz_type.title()} visualization displayed!"
            )
        except Exception as e:
            self.display_manager.display_error_message(f"❌ Visualization error: {str(e)}")