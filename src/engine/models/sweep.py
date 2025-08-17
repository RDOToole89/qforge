"""
Parameter Sweep Models

Purpose: Define models for parameter sweep configurations and results.
Sweeps enable systematic exploration of quantum experiment parameter spaces
for research studies and optimization.

Key Features:
- Flexible parameter range specification
- Research-optimized sweep configurations
- Statistical aggregation support
- Result correlation analysis

Dependencies: Pydantic, config models
Used by: Engine sweep API, research campaigns, parameter optimization
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Union, Iterator, Tuple
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from itertools import product
from datetime import datetime
import math

from .config import ExperimentConfig
from .results import ExperimentResult


class SweepManifest(BaseModel):
    """
    Complete specification for a parameter sweep.

    Defines the base configuration and parameter ranges for systematic
    exploration of quantum experiment parameter space.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    # ===== Base Configuration =====
    base_preset: Optional[str] = Field(
        default=None,
        description="Base preset name (legacy support, prefer base_config)",
    )

    base_config: Optional[ExperimentConfig] = Field(
        default=None,
        description="Base experiment configuration (preferred over base_preset)",
    )

    # ===== Parameter Ranges =====
    parameter_ranges: Dict[str, List[Any]] = Field(
        description="Parameter ranges to sweep: {parameter_name: [values]}"
    )

    # ===== Execution Configuration =====
    runs_per_config: int = Field(
        default=1,
        ge=1,
        le=100,
        description="Number of runs per parameter combination for statistical analysis",
    )

    rng_seed: Optional[int] = Field(
        default=None, description="Base random seed (incremented for each run)"
    )

    # ===== Override Parameters =====
    override: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Parameters to override in base configuration for all sweep runs",
    )

    # ===== Research Configuration =====
    research_metadata: Optional["SweepResearchMetadata"] = Field(
        default=None, description="Research-specific metadata for parameter sweeps"
    )

    # ===== Execution Control =====
    parallel_execution: bool = Field(
        default=False, description="Enable parallel execution of sweep combinations"
    )

    max_concurrent: Optional[int] = Field(
        default=None,
        ge=1,
        le=20,
        description="Maximum concurrent experiments (if parallel_execution=True)",
    )

    timeout_seconds: Optional[int] = Field(
        default=None, ge=1, description="Timeout per experiment in seconds"
    )

    # ===== Validation =====
    @field_validator("parameter_ranges")
    @classmethod
    def validate_parameter_ranges(cls, v: Dict[str, List[Any]]) -> Dict[str, List[Any]]:
        """Validate parameter ranges are non-empty lists."""
        if not v:
            raise ValueError("parameter_ranges cannot be empty")
        for param_name, values in v.items():
            if not isinstance(values, list):
                raise ValueError(f"Parameter range for '{param_name}' must be a list")
            if len(values) == 0:
                raise ValueError(f"Parameter range for '{param_name}' cannot be empty")
        return v

    @field_validator("base_config")
    @classmethod
    def validate_base_config_or_preset(
        cls, v: Optional[ExperimentConfig], info
    ) -> Optional[ExperimentConfig]:
        """
        Ensure either base_config or base_preset is provided.
        NOTE: Grid expansion helpers use base_config; base_preset is kept for legacy but not expanded.
        """
        base_preset = info.data.get("base_preset")
        if v is None and base_preset is None:
            raise ValueError("Either base_config or base_preset must be provided")
        return v

    @field_validator("rng_seed")
    @classmethod
    def validate_seed(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError("rng_seed must be non-negative if provided")
        return v

    @model_validator(mode="after")
    def validate_parallelism(self) -> "SweepManifest":
        # If parallel_execution is requested and max_concurrent not set, pick a conservative default
        if self.parallel_execution and self.max_concurrent is None:
            # Default to min(total combinations, 4) — simple, portable, safe
            try:
                default_mc = min(max(1, self.total_combinations), 4)
            except Exception:
                default_mc = 4
            object.__setattr__(self, "max_concurrent", default_mc)
        return self

    # ===== Computed Properties =====
    @property
    def total_combinations(self) -> int:
        """Calculate total number of parameter combinations."""
        total = 1
        for values in self.parameter_ranges.values():
            total *= len(values)
        return total

    @property
    def total_experiments(self) -> int:
        """Calculate total number of experiments (combinations × runs)."""
        return self.total_combinations * self.runs_per_config

    @property
    def estimated_duration_minutes(self) -> Optional[float]:
        """Estimate total sweep duration based on typical experiment time (heuristic: 30s/experiment)."""
        if self.total_experiments > 0:
            return (self.total_experiments * 30.0) / 60.0
        return None

    # ===== Helpers (engine-facing) =====
    def parameter_grid(self) -> List[Dict[str, Any]]:
        """
        Build a cartesian grid of all parameter combinations.
        Returns a list of {param: value} dicts (order is deterministic).
        """
        if not self.parameter_ranges:
            return []
        keys = sorted(self.parameter_ranges.keys())
        value_lists = [self.parameter_ranges[k] for k in keys]
        combos = []
        for values in product(*value_lists):
            combos.append({k: v for k, v in zip(keys, values)})
        return combos

    def _apply_overrides(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Apply global overrides (if any) to a parameter dictionary non-destructively."""
        if not self.override:
            return params
        merged = dict(params)
        merged.update(self.override)
        return merged

    def iter_experiment_configs(
        self,
    ) -> Iterator[Tuple[ExperimentConfig, int, Dict[str, Any]]]:
        """
        Yield concrete ExperimentConfig instances for each combination and run.
        Yields (config, run_index, param_combo_dict).
        Requires base_config (base_preset is not expanded here).
        """
        if self.base_config is None:
            raise ValueError(
                "iter_experiment_configs requires base_config (base_preset expansion is not supported)"
            )

        base = self.base_config
        combos = self.parameter_grid()
        for combo in combos:
            # merge overrides
            effective = self._apply_overrides(combo)
            # Create a config by copying base and updating fields present in ExperimentConfig
            cfg_data = base.model_dump()
            for k, v in effective.items():
                if k in cfg_data:
                    cfg_data[k] = v
                else:
                    # allow adding to custom_params if it's a non-schema param
                    custom = (cfg_data.get("custom_params") or {}).copy()
                    custom[k] = v
                    cfg_data["custom_params"] = custom

            # runs
            for r in range(self.runs_per_config):
                # seed progression: base + linear offset
                if self.rng_seed is not None:
                    cfg_data["rng_seed"] = int(self.rng_seed + r)
                yield ExperimentConfig(**cfg_data), r, combo


class SweepResearchMetadata(BaseModel):
    """Research-specific metadata for parameter sweeps."""

    # Research context
    hypothesis: Optional[str] = Field(
        default=None, description="Research hypothesis being tested by this sweep"
    )

    research_phase: Optional[str] = Field(
        default=None,
        description="Phase of research (exploration, validation, optimization, etc.)",
    )

    expected_trends: Optional[List[str]] = Field(
        default=None,
        description="Expected trends or relationships in the parameter space",
    )

    # Statistical requirements
    significance_level: float = Field(
        default=0.05,
        ge=0.001,
        le=0.1,
        description="Required statistical significance level",
    )

    minimum_effect_size: Optional[float] = Field(
        default=None, ge=0.0, description="Minimum effect size of interest"
    )

    # Analysis preferences
    correlation_analysis: bool = Field(
        default=True,
        description="Perform correlation analysis between parameters and metrics",
    )

    trend_analysis: bool = Field(
        default=True, description="Perform trend analysis across parameter ranges"
    )

    statistical_tests: List[str] = Field(
        default_factory=lambda: ["anova", "correlation"],
        description="Statistical tests to perform on sweep results",
    )


class SweepResult(BaseModel):
    """
    Complete results from a parameter sweep.

    Contains all individual experiment results plus aggregated analysis
    across the parameter space.
    """

    model_config = ConfigDict(extra="allow")

    # ===== Sweep Configuration =====
    manifest: SweepManifest = Field(
        description="Original sweep manifest used to generate results"
    )

    # ===== Individual Results =====
    experiment_results: List[ExperimentResult] = Field(
        description="Results from each individual experiment in the sweep"
    )

    # ===== Aggregated Analysis =====
    parameter_analysis: "ParameterAnalysis" = Field(
        description="Analysis of parameter effects and relationships"
    )

    statistical_summary: "StatisticalSummary" = Field(
        description="Statistical summary across all experiments"
    )

    # ===== Research Analysis =====
    research_insights: Optional["SweepResearchInsights"] = Field(
        default=None, description="Research insights from sweep analysis"
    )

    # ===== Execution Metadata =====
    execution_metadata: "SweepExecutionMetadata" = Field(
        description="Information about sweep execution"
    )

    # ===== Computed Properties =====
    @property
    def successful_experiments(self) -> List[ExperimentResult]:
        """Get only successfully completed experiments."""
        return [r for r in self.experiment_results if r.status == "completed"]

    @property
    def success_rate(self) -> float:
        """Calculate the success rate of experiments in the sweep."""
        if not self.experiment_results:
            return 0.0
        return len(self.successful_experiments) / len(self.experiment_results)

    @property
    def has_research_metrics(self) -> bool:
        """Check if any experiments have structured decoherence metrics."""
        return any(
            r.structured_decoherence_metrics is not None
            for r in self.experiment_results
        )


class ParameterAnalysis(BaseModel):
    """Analysis of parameter effects and relationships in sweep."""

    # Parameter effects
    main_effects: Dict[str, "ParameterEffect"] = Field(
        description="Main effect of each parameter on outcome metrics"
    )

    interaction_effects: Optional[Dict[str, "InteractionEffect"]] = Field(
        default=None, description="Interaction effects between parameter pairs"
    )

    # Sensitivity analysis
    sensitivity_ranking: List[str] = Field(
        description="Parameters ranked by their effect on outcomes"
    )

    optimal_regions: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="Parameter regions that produce optimal results"
    )


class ParameterEffect(BaseModel):
    """Effect of a single parameter on outcome metrics."""

    parameter_name: str = Field(description="Name of the parameter")
    effect_size: float = Field(description="Statistical effect size")
    significance: float = Field(
        ge=0.0, le=1.0, description="Statistical significance (p-value)"
    )

    # Effect characteristics
    direction: str = Field(
        description="Direction of effect (positive, negative, nonlinear)"
    )
    strength: str = Field(description="Strength of effect (weak, moderate, strong)")

    # Detailed analysis
    correlation_coefficient: Optional[float] = Field(
        default=None,
        ge=-1.0,
        le=1.0,
        description="Correlation with primary outcome metric",
    )

    trend_analysis: Optional[Dict[str, Any]] = Field(
        default=None, description="Detailed trend analysis across parameter range"
    )


class InteractionEffect(BaseModel):
    """Interaction effect between parameter pairs."""

    parameter_pair: List[str] = Field(description="Names of interacting parameters")
    interaction_strength: float = Field(description="Strength of interaction effect")
    significance: float = Field(ge=0.0, le=1.0, description="Statistical significance")

    interaction_type: str = Field(
        description="Type of interaction (synergistic, antagonistic, threshold)"
    )


class StatisticalSummary(BaseModel):
    """Statistical summary across all sweep experiments."""

    # Basic statistics
    total_experiments: int = Field(ge=0, description="Total number of experiments")
    successful_experiments: int = Field(
        ge=0, description="Number of successful experiments"
    )

    # Outcome distributions
    outcome_statistics: Dict[str, "OutcomeStatistics"] = Field(
        description="Statistics for each outcome metric"
    )

    # Convergence analysis
    convergence_achieved: bool = Field(
        description="Whether statistical convergence was achieved"
    )
    confidence_intervals: Dict[str, List[float]] = Field(
        description="95% confidence intervals for key metrics"
    )

    # Quality metrics
    data_quality_score: float = Field(
        ge=0.0, le=1.0, description="Overall data quality score"
    )


class OutcomeStatistics(BaseModel):
    """Statistics for a single outcome metric across sweep."""

    metric_name: str = Field(description="Name of the outcome metric")

    # Basic statistics
    mean: float = Field(description="Mean value")
    std: float = Field(ge=0.0, description="Standard deviation")
    min_value: float = Field(description="Minimum value")
    max_value: float = Field(description="Maximum value")

    # Distribution characteristics
    skewness: Optional[float] = Field(default=None, description="Distribution skewness")
    kurtosis: Optional[float] = Field(default=None, description="Distribution kurtosis")

    # Confidence intervals
    ci_95_lower: float = Field(description="95% confidence interval lower bound")
    ci_95_upper: float = Field(description="95% confidence interval upper bound")


class SweepResearchInsights(BaseModel):
    """Research insights extracted from sweep analysis."""

    # Key findings
    key_findings: List[str] = Field(description="Main research findings from the sweep")

    # Hypothesis validation
    hypothesis_supported: Optional[bool] = Field(
        default=None,
        description="Whether the research hypothesis is supported by results",
    )

    evidence_strength: Optional[str] = Field(
        default=None, description="Strength of evidence (weak, moderate, strong)"
    )

    # Recommendations
    follow_up_experiments: List[str] = Field(
        default_factory=list, description="Recommended follow-up experiments"
    )

    parameter_recommendations: Dict[str, str] = Field(
        default_factory=dict, description="Recommendations for parameter settings"
    )

    # Research impact
    significance_assessment: Optional[str] = Field(
        default=None, description="Assessment of research significance"
    )

    publication_potential: Optional[str] = Field(
        default=None, description="Assessment of publication potential"
    )


class SweepExecutionMetadata(BaseModel):
    """Metadata about sweep execution."""

    # Timing
    start_time: str = Field(description="When sweep execution started (ISO 8601)")
    end_time: Optional[str] = Field(
        default=None, description="When sweep execution completed (ISO 8601)"
    )
    total_duration_seconds: Optional[float] = Field(
        default=None, ge=0.0, description="Total execution time"
    )

    # Execution details
    parallel_execution_used: bool = Field(
        description="Whether parallel execution was used"
    )
    max_concurrent_achieved: Optional[int] = Field(
        default=None, description="Maximum concurrent experiments"
    )

    # Resource usage
    peak_memory_mb: Optional[float] = Field(
        default=None, ge=0.0, description="Peak memory usage"
    )
    total_cpu_time_seconds: Optional[float] = Field(
        default=None, ge=0.0, description="Total CPU time used"
    )

    # Error tracking
    failed_experiments: int = Field(ge=0, description="Number of failed experiments")
    error_summary: Dict[str, int] = Field(
        default_factory=dict, description="Summary of error types and counts"
    )

    @model_validator(mode="after")
    def compute_duration_if_missing(self) -> "SweepExecutionMetadata":
        """If total_duration_seconds is missing but times are present, compute it."""
        if self.total_duration_seconds is None and self.start_time and self.end_time:
            try:
                # Minimal ISO parsing (no external deps)
                start = datetime.fromisoformat(self.start_time.replace("Z", "+00:00"))
                end = datetime.fromisoformat(self.end_time.replace("Z", "+00:00"))
                dur = max(0.0, (end - start).total_seconds())
                object.__setattr__(self, "total_duration_seconds", dur)
            except Exception:
                # Leave as None if parsing fails
                pass
        return self
