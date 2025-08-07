"""
Mixin classes for common experiment functionality.

Provides reusable mixins that can be combined with base experiment
classes to add specific capabilities like noise modeling, analysis,
visualization, and research-grade features.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger("QuantumExperiment.Components.Mixins")


class NoiseMixin(ABC):
    """
    Mixin for experiments that support noise modeling.

    Provides standardized interface for configuring and applying
    quantum noise models to experiments.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.noise_config: Dict[str, Any] = {}
        self.noise_enabled: bool = False

    def configure_noise(self,
                       noise_type: str,
                       error_rate: float = 0.01,
                       enabled: bool = True,
                       **noise_params) -> 'NoiseMixin':
        """
        Configure noise model for the experiment.

        Args:
            noise_type: Type of noise (DEPOLARIZING, PHASE_DAMPING, etc.)
            error_rate: Base error rate for the noise model
            enabled: Whether noise is enabled
            **noise_params: Additional noise-specific parameters

        Returns:
            Self for method chaining
        """
        self.noise_config = {
            "noise_type": noise_type,
            "error_rate": error_rate,
            "noise_enabled": enabled,
            **noise_params
        }
        self.noise_enabled = enabled
        logger.info(f"Configured {noise_type} noise (rate: {error_rate}, enabled: {enabled})")
        return self

    def get_noise_config(self) -> Dict[str, Any]:
        """Get current noise configuration."""
        return self.noise_config.copy()

    def disable_noise(self) -> 'NoiseMixin':
        """Disable noise for this experiment."""
        self.noise_enabled = False
        self.noise_config["noise_enabled"] = False
        return self


class AnalysisMixin(ABC):
    """
    Mixin for experiments that support advanced analysis.

    Provides interface for configuring analysis routines and
    metrics to be computed on experiment results.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.analysis_config: Dict[str, Any] = {}
        self.enabled_metrics: List[str] = []

    def configure_analysis(self,
                          metrics: List[str],
                          analysis_params: Optional[Dict[str, Any]] = None) -> 'AnalysisMixin':
        """
        Configure analysis metrics and parameters.

        Args:
            metrics: List of analysis metrics to compute
            analysis_params: Additional analysis parameters

        Returns:
            Self for method chaining
        """
        self.enabled_metrics = metrics
        self.analysis_config = analysis_params or {}
        logger.info(f"Configured analysis with metrics: {metrics}")
        return self

    def add_metric(self, metric: str) -> 'AnalysisMixin':
        """Add a single analysis metric."""
        if metric not in self.enabled_metrics:
            self.enabled_metrics.append(metric)
            logger.info(f"Added analysis metric: {metric}")
        return self

    def get_analysis_config(self) -> Dict[str, Any]:
        """Get current analysis configuration."""
        return {
            "enabled_metrics": self.enabled_metrics,
            "analysis_params": self.analysis_config
        }


class VisualizationMixin(ABC):
    """
    Mixin for experiments that support visualization.

    Provides interface for configuring visualization options
    and output formats.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.visualization_config: Dict[str, Any] = {}
        self.output_formats: List[str] = ["plot"]

    def configure_visualization(self,
                               visualization_type: str = "histogram",
                               output_formats: Optional[List[str]] = None,
                               **viz_params) -> 'VisualizationMixin':
        """
        Configure visualization options.

        Args:
            visualization_type: Type of visualization (histogram, hypergraph, etc.)
            output_formats: List of output formats (plot, save, etc.)
            **viz_params: Additional visualization parameters

        Returns:
            Self for method chaining
        """
        self.visualization_config = {
            "visualization_type": visualization_type,
            **viz_params
        }
        if output_formats:
            self.output_formats = output_formats

        logger.info(f"Configured {visualization_type} visualization")
        return self

    def get_visualization_config(self) -> Dict[str, Any]:
        """Get current visualization configuration."""
        return {
            "output_formats": self.output_formats,
            **self.visualization_config
        }


class ResearchMixin(ABC):
    """
    Mixin for research-grade experiments.

    Provides advanced features for scientific research including
    comprehensive metrics, statistical validation, and publication-ready output.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.research_config: Dict[str, Any] = {}
        self.research_enabled: bool = False

    def configure_research(self,
                          research_type: str,
                          enable_research_metrics: bool = True,
                          statistical_validation: bool = True,
                          **research_params) -> 'ResearchMixin':
        """
        Configure research-grade features.

        Args:
            research_type: Type of research (structured_decoherence, etc.)
            enable_research_metrics: Whether to compute research metrics
            statistical_validation: Whether to perform statistical validation
            **research_params: Additional research parameters

        Returns:
            Self for method chaining
        """
        self.research_config = {
            "research_type": research_type,
            "enable_research_metrics": enable_research_metrics,
            "statistical_validation": statistical_validation,
            **research_params
        }
        self.research_enabled = enable_research_metrics
        logger.info(f"Configured research mode: {research_type}")
        return self

    def enable_high_precision(self,
                             shots: int = 8192,
                             runs_per_config: int = 5) -> 'ResearchMixin':
        """
        Enable high-precision mode for research.

        Args:
            shots: Number of shots per run
            runs_per_config: Number of runs per configuration

        Returns:
            Self for method chaining
        """
        self.research_config.update({
            "high_precision": True,
            "shots": shots,
            "runs_per_config": runs_per_config
        })
        logger.info(f"Enabled high-precision mode ({shots} shots, {runs_per_config} runs)")
        return self

    def get_research_config(self) -> Dict[str, Any]:
        """Get current research configuration."""
        return self.research_config.copy()


class ComposableMixin(NoiseMixin, AnalysisMixin, VisualizationMixin, ResearchMixin):
    """
    Convenience mixin that combines all common experiment capabilities.

    Provides a single mixin that includes noise modeling, analysis,
    visualization, and research features.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info("Initialized composable experiment with all capabilities")

    def get_full_config(self) -> Dict[str, Any]:
        """Get complete configuration from all mixins."""
        config = {}

        # Only include configs for initialized mixins
        if hasattr(self, 'noise_config'):
            config["noise"] = self.get_noise_config()
        if hasattr(self, 'analysis_config'):
            config["analysis"] = self.get_analysis_config()
        if hasattr(self, 'visualization_config'):
            config["visualization"] = self.get_visualization_config()
        if hasattr(self, 'research_config'):
            config["research"] = self.get_research_config()

        return config
