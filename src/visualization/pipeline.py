"""Deprecated monolithic pipeline.

This module is retained temporarily as a façade for backwards compatibility.
New code should import helpers from `src.visualization.pipeline.*` modules.
"""

from typing import Dict, List, Optional, Any, Callable, Tuple
import logging
from dataclasses import dataclass, field
from .backends import get_backend_registry, set_visualization_backend

logger = logging.getLogger("QuantumExperiment.Visualization.Pipeline")


@dataclass
class AnalysisStep:
    """Single analysis step in a pipeline."""

    function: Callable
    kwargs: Dict[str, Any] = field(default_factory=dict)
    name: Optional[str] = None

    def execute(self, data: Any, context: Dict[str, Any]) -> Any:
        """Execute this analysis step."""
        try:
            # Merge context and step-specific kwargs
            merged_kwargs = {**context, **self.kwargs}
            result = self.function(data, **merged_kwargs)

            logger.debug(
                f"Analysis step '{self.name or 'unnamed'}' completed successfully"
            )
            return result

        except Exception as e:
            logger.error(f"Analysis step '{self.name or 'unnamed'}' failed: {e}")
            raise


@dataclass
class RenderStep:
    """Single rendering step in a pipeline."""

    function: Callable
    kwargs: Dict[str, Any] = field(default_factory=dict)
    name: Optional[str] = None

    def execute(self, analysis_result: Any, context: Dict[str, Any]) -> Any:
        """Execute this rendering step."""
        try:
            # Merge context and step-specific kwargs
            merged_kwargs = {**context, **self.kwargs}
            result = self.function(analysis_result, **merged_kwargs)

            logger.debug(
                f"Render step '{self.name or 'unnamed'}' completed successfully"
            )
            return result

        except Exception as e:
            logger.error(f"Render step '{self.name or 'unnamed'}' failed: {e}")
            raise


@dataclass
class PostProcessStep:
    """Single post-processing step in a pipeline."""

    function: Callable
    kwargs: Dict[str, Any] = field(default_factory=dict)
    name: Optional[str] = None

    def execute(self, render_result: Any, context: Dict[str, Any]) -> Any:
        """Execute this post-processing step."""
        try:
            # Merge context and step-specific kwargs
            merged_kwargs = {**context, **self.kwargs}
            result = self.function(render_result, **merged_kwargs)

            logger.debug(
                f"Post-process step '{self.name or 'unnamed'}' completed successfully"
            )
            return result

        except Exception as e:
            logger.error(f"Post-process step '{self.name or 'unnamed'}' failed: {e}")
            raise


class VisualizationPipeline:
    """
    Composable visualization pipeline for quantum experiments.

    Allows dynamic composition of analysis, rendering, and post-processing steps
    to create custom visualization workflows without modifying core code.
    """

    def __init__(self, name: str, description: str = ""):
        """
        Initialize a new visualization pipeline.

        Args:
            name (str): Name of this pipeline
            description (str): Optional description of what this pipeline does
        """
        self.name = name
        self.description = description
        self.analysis_steps: List[AnalysisStep] = []
        self.rendering_steps: List[RenderStep] = []
        self.post_processing: List[PostProcessStep] = []

        logger.info(f"Created visualization pipeline: {name}")
        if description:
            logger.info(f"  Description: {description}")

    def add_analysis(
        self, function: Callable, name: str = None, **kwargs
    ) -> "VisualizationPipeline":
        """Add an analysis step to the pipeline."""
        step = AnalysisStep(function=function, kwargs=kwargs, name=name)
        self.analysis_steps.append(step)
        logger.debug(f"Added analysis step: {name or function.__name__}")
        return self

    def add_renderer(
        self, function: Callable, name: str = None, **kwargs
    ) -> "VisualizationPipeline":
        """Add a rendering step to the pipeline."""
        step = RenderStep(function=function, kwargs=kwargs, name=name)
        self.rendering_steps.append(step)
        logger.debug(f"Added render step: {name or function.__name__}")
        return self

    def add_post_processor(
        self, function: Callable, name: str = None, **kwargs
    ) -> "VisualizationPipeline":
        """Add a post-processing step to the pipeline."""
        step = PostProcessStep(function=function, kwargs=kwargs, name=name)
        self.post_processing.append(step)
        logger.debug(f"Added post-process step: {name or function.__name__}")
        return self

    def execute(
        self, data: Any, context: Optional[Dict[str, Any]] = None
    ) -> Tuple[Any, Any, Any]:
        """
        Execute the complete pipeline.

        Args:
            data: Input data for analysis
            context: Additional context to pass to all steps

        Returns:
            Tuple of (analysis_result, render_result, final_result)
        """
        context = context or {}
        logger.info(f"Executing pipeline: {self.name}")

        # Analysis phase
        analysis_result = data
        for step in self.analysis_steps:
            analysis_result = step.execute(analysis_result, context)

        logger.debug(f"Analysis phase completed ({len(self.analysis_steps)} steps)")

        # Rendering phase
        render_result = analysis_result
        for step in self.rendering_steps:
            render_result = step.execute(render_result, context)

        logger.debug(f"Rendering phase completed ({len(self.rendering_steps)} steps)")

        # Post-processing phase
        final_result = render_result
        for step in self.post_processing:
            final_result = step.execute(final_result, context)

        logger.debug(
            f"Post-processing phase completed ({len(self.post_processing)} steps)"
        )
        logger.info(f"Pipeline '{self.name}' execution completed successfully")

        return analysis_result, render_result, final_result


class PipelineTemplates:
    """Pre-configured pipeline templates for common visualization tasks."""

    @staticmethod
    def basic_histogram(
        state_type: str = "GHZ", research_grade: bool = True
    ) -> VisualizationPipeline:
        """Create a basic histogram visualization pipeline."""
        pipeline = VisualizationPipeline(
            name="Basic Histogram",
            description=f"Histogram visualization for {state_type} states",
        )

        # Analysis: Extract counts and compute basic statistics
        def extract_counts(data):
            if isinstance(data, dict) and "counts" in data:
                return data["counts"]
            return data

        def compute_statistics(counts):
            total = sum(int(count) for count in counts.values())
            probabilities = {
                state: int(count) / total for state, count in counts.items()
            }
            return {"counts": counts, "probabilities": probabilities, "total": total}

        pipeline.add_analysis(extract_counts, "extract_counts")
        pipeline.add_analysis(compute_statistics, "compute_statistics")

        return pipeline

    @staticmethod
    def enhanced_density_matrix(state_type: str = "GHZ") -> VisualizationPipeline:
        """Create an enhanced density matrix visualization pipeline."""
        pipeline = VisualizationPipeline(
            name="Enhanced Density Matrix",
            description=f"Advanced density matrix visualization for {state_type} states",
        )

        # Analysis: Compute quantum metrics
        def extract_density_matrix(data):
            if hasattr(data, "data"):  # DensityMatrix object
                return data
            elif isinstance(data, dict) and "density" in data:
                from qiskit.quantum_info import DensityMatrix
                import numpy as np

                return DensityMatrix(np.array(data["density"]))
            return data

        pipeline.add_analysis(extract_density_matrix, "extract_density_matrix")

        return pipeline

    @staticmethod
    def correlation_hypergraph(
        state_type: str = "GHZ", adaptive_threshold: bool = True
    ) -> VisualizationPipeline:
        """Create a correlation hypergraph visualization pipeline."""
        pipeline = VisualizationPipeline(
            name="Correlation Hypergraph",
            description=f"Hypergraph correlation analysis for {state_type} states",
        )

        # Analysis: Compute correlations
        def prepare_correlation_data(data):
            # Handle both counts and density matrix data
            if isinstance(data, dict) and "counts" in data:
                return data["counts"]
            return data

        pipeline.add_analysis(prepare_correlation_data, "prepare_data")

        return pipeline


class AdvancedVisualizationPipeline(VisualizationPipeline):
    """
    Comprehensive pipeline with multi-backend support and advanced features.

    Supports:
    - Multiple visualization backends (matplotlib, plotly, bokeh)
    - Animated visualizations
    - Interactive plots
    - Custom export formats
    - Research workflow integration
    """

    def __init__(self, name: str, description: str = "", backend: str = "matplotlib"):
        super().__init__(name, description)
        self.backend = backend
        self.backend_registry = get_backend_registry()
        self.export_config = {}

    def set_backend(self, backend: str) -> "AdvancedVisualizationPipeline":
        """Set visualization backend (matplotlib, plotly, bokeh, etc.)."""
        self.backend = backend
        set_visualization_backend(backend)
        logger.info(f"Pipeline '{self.name}' using backend: {backend}")
        return self

    def set_export_config(self, **config) -> "AdvancedVisualizationPipeline":
        """Configure export settings (format, dpi, size, etc.)."""
        self.export_config.update(config)
        return self

    def add_animation(
        self, func: Callable, name: Optional[str] = None, **kwargs
    ) -> "AdvancedVisualizationPipeline":
        """Add animation step to pipeline."""
        kwargs["animation"] = True
        kwargs["backend"] = self.backend
        return self.add_renderer(func, name, **kwargs)

    def add_interactive_plot(
        self, func: Callable, name: Optional[str] = None, **kwargs
    ) -> "AdvancedVisualizationPipeline":
        """Add interactive visualization step."""
        kwargs["interactive"] = True
        kwargs["backend"] = self.backend
        return self.add_renderer(func, name, **kwargs)

    def execute(self, data: Any, **runtime_context) -> Dict[str, Any]:
        """Execute pipeline with backend-specific handling."""

        # Set backend context
        runtime_context["backend"] = self.backend
        runtime_context["export_config"] = self.export_config

        # Execute base pipeline
        results = super().execute(data, **runtime_context)

        # Add backend-specific post-processing
        if self.export_config:
            results["exports"] = self._handle_exports(results)

        return results

    def _handle_exports(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Handle export of visualizations based on config."""
        exports = {}

        for render_name, render_result in results.get("rendering", {}).items():
            if hasattr(render_result, "write_html"):  # Plotly figure
                if self.export_config.get("html"):
                    from .save_manager import get_organized_save_path

                    html_path = get_organized_save_path(
                        viz_type="research",
                        experiment_config=self.export_config.get("experiment_config"),
                        custom_name=render_name,
                        extension="html",
                    )
                    render_result.write_html(html_path)
                    exports[f"{render_name}_html"] = html_path

            elif hasattr(render_result, "savefig"):  # Matplotlib figure
                if self.export_config.get("png"):
                    from .save_manager import get_organized_save_path

                    png_path = get_organized_save_path(
                        viz_type="research",
                        experiment_config=self.export_config.get("experiment_config"),
                        custom_name=render_name,
                        extension="png",
                    )
                    render_result.savefig(
                        png_path, dpi=self.export_config.get("dpi", 300)
                    )
                    exports[f"{render_name}_png"] = png_path

        return exports


class AdvancedPipelineTemplates(PipelineTemplates):
    """Advanced pipeline templates with multi-backend support."""

    @staticmethod
    def interactive_research_histogram(
        backend: str = "plotly",
    ) -> AdvancedVisualizationPipeline:
        """Interactive histogram with research analysis."""
        from src.core.analysis.information_theory import (
            compute_shannon_entropy,
            compute_research_metrics,
        )

        pipeline = AdvancedVisualizationPipeline(
            name="interactive_research_histogram",
            description="Interactive histogram with comprehensive research analysis",
            backend=backend,
        )

        # Research-grade analysis
        pipeline.add_analysis(compute_research_metrics, name="research_metrics")
        pipeline.add_analysis(compute_shannon_entropy, name="entropy", normalize=True)

        # Interactive visualization based on backend
        if backend == "plotly":
            from src.visualization.backends.plotly_backend import (
                plot_interactive_histogram,
            )

            pipeline.add_interactive_plot(
                plot_interactive_histogram, name="interactive_histogram"
            )
        else:
            # Fallback to standard histogram
            from src.visualization.histogram import plot_histogram

            pipeline.add_renderer(
                plot_histogram, name="histogram", research_metrics=True
            )

        return pipeline

    @staticmethod
    def bloch_sphere_decoherence_animation(
        backend: str = "plotly",
    ) -> AdvancedVisualizationPipeline:
        """
        YOUR ANIMATED BLOCH SPHERE DECOHERENCE PIPELINE!

        This is the pipeline for your brilliant animation idea.
        """
        from src.visualization.animations import (
            create_decoherence_animation,
            analyze_decoherence_patterns,
        )
        from src.core.analysis.bloch import compute_bloch_vectors_for_all_qubits

        pipeline = AdvancedVisualizationPipeline(
            name="bloch_decoherence_animation",
            description="Animated Bloch sphere showing quantum decoherence patterns",
            backend=backend,
        )

        # Analysis for decoherence patterns
        pipeline.add_analysis(
            compute_bloch_vectors_for_all_qubits, name="bloch_vectors"
        )
        pipeline.add_analysis(analyze_decoherence_patterns, name="decoherence_analysis")

        # Animated visualization
        pipeline.add_animation(
            create_decoherence_animation, name="decoherence_animation"
        )

        # Export configuration for research
        pipeline.set_export_config(
            html=True,  # Interactive HTML
            mp4=True,  # Video export
            dpi=300,  # High resolution
        )

        return pipeline

    @staticmethod
    def comprehensive_3d_density_matrix(
        backend: str = "plotly",
    ) -> AdvancedVisualizationPipeline:
        """3D interactive density matrix with quantum metrics."""
        from src.visualization.density_matrix import compute_quantum_metrics

        pipeline = AdvancedVisualizationPipeline(
            name="3d_density_matrix",
            description="3D interactive density matrix visualization",
            backend=backend,
        )

        # Quantum state analysis
        pipeline.add_analysis(compute_quantum_metrics, name="quantum_metrics")

        # 3D interactive visualization
        if backend == "plotly":
            from src.visualization.backends.plotly_backend import (
                plot_interactive_density_matrix,
            )

            pipeline.add_interactive_plot(
                plot_interactive_density_matrix, name="3d_density"
            )
        else:
            from src.visualization.density_matrix import plot_density_matrix

            pipeline.add_renderer(plot_density_matrix, name="density_matrix")

        return pipeline

    @staticmethod
    def multi_backend_comparison(
        data_type: str = "histogram",
    ) -> Dict[str, AdvancedVisualizationPipeline]:
        """Create the same visualization in multiple backends for comparison."""

        backends = ["matplotlib", "plotly"]
        if data_type == "histogram":
            pipelines = {
                backend: AdvancedPipelineTemplates.interactive_research_histogram(
                    backend
                )
                for backend in backends
            }
        elif data_type == "density_matrix":
            pipelines = {
                backend: AdvancedPipelineTemplates.comprehensive_3d_density_matrix(
                    backend
                )
                for backend in backends
            }
        else:
            raise ValueError(f"Unsupported data type: {data_type}")

        return pipelines


# Usage examples for your research
def create_structured_decoherence_study():
    """
    YOUR STRUCTURED DECOHERENCE STUDY PIPELINE!

    This creates the complete analysis pipeline for your research hypothesis.
    """

    # Main analysis pipeline
    study_pipeline = AdvancedVisualizationPipeline(
        name="ghz_structured_decoherence_study",
        description="Complete GHZ structured decoherence analysis with animations",
        backend="plotly",
    )

    # Comprehensive analysis chain
    from src.core.analysis.information_theory import compute_research_metrics
    from src.core.analysis.correlations import compute_pairwise_correlations
    from src.core.analysis.symmetry import compute_su2_symmetry
    from src.visualization.animations import analyze_decoherence_patterns

    study_pipeline.add_analysis(compute_research_metrics, name="research_metrics")
    study_pipeline.add_analysis(compute_pairwise_correlations, name="correlations")
    study_pipeline.add_analysis(compute_su2_symmetry, name="symmetry")
    study_pipeline.add_analysis(
        analyze_decoherence_patterns, name="decoherence_patterns"
    )

    # Multi-modal visualization
    from src.visualization.backends.plotly_backend import plot_interactive_histogram
    from src.visualization.animations import create_decoherence_animation

    study_pipeline.add_interactive_plot(
        plot_interactive_histogram, name="interactive_histogram"
    )
    study_pipeline.add_animation(create_decoherence_animation, name="bloch_animation")

    # Research export configuration
    study_pipeline.set_export_config(
        html=True,  # Interactive plots
        png=True,  # Publication figures
        mp4=True,  # Animations
        json=True,  # Raw data
        dpi=300,  # High resolution
    )

    return study_pipeline


# Quick setup function
def setup_multi_backend_environment():
    """Setup all available visualization backends."""

    # Register backends
    try:
        from .backends.plotly_backend import register_plotly_backend

        register_plotly_backend()
        logger.info("✅ Plotly backend registered")
    except ImportError:
        logger.warning("⚠️ Plotly backend not available")

    # Add more backends as needed
    # from .backends.bokeh_backend import register_bokeh_backend
    # from .backends.manim_backend import register_manim_backend

    # Print available backends
    registry = get_backend_registry()
    available = registry.list_backends()

    logger.info("📊 Available visualization backends:")
    for backend, functions in available.items():
        logger.info(f"   {backend}: {', '.join(functions)}")

    return available
