"""
Experiment Program Base Classes

This module defines the ExperimentProgram protocol and BaseExperiment helper class
for creating pluggable, discoverable experiment programs.

All experiments should implement the ExperimentProgram protocol, either directly
or by inheriting from BaseExperiment.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol, runtime_checkable

from src.engine.models import ExperimentConfig, ExperimentResult


@runtime_checkable
class ExperimentProgram(Protocol):
    """
    Protocol for pluggable experiment programs.

    This defines the contract that all experiment programs must follow.
    Experiments can implement this protocol directly or inherit from BaseExperiment.

    Attributes:
        name: Short identifier for the experiment (used in registry/CLI)
        description: Human-readable description of what the experiment tests

    Methods:
        default_config: Returns the default ExperimentConfig for this experiment
        run: Executes the experiment with optional config overrides
    """

    name: str
    description: str

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        ...

    def run(self, overrides: Mapping[str, Any] | None = None, *, ctx: Any | None = None) -> ExperimentResult:
        """
        Run the experiment with optional config overrides.

        Args:
            overrides: Optional dict of config fields to override
            ctx: Optional AppContext for session grouping

        Returns:
            ExperimentResult with full analysis and metrics
        """
        ...


class BaseExperiment:
    """
    Base class providing common experiment functionality.

    Subclasses must:
    - Set `name` and `description` class attributes
    - Implement `default_config()` method

    The `run()` and `sweep()` methods are provided and use the engine API.

    Example:
        class MyExperiment(BaseExperiment):
            name = "my_exp"
            description = "Tests something interesting"

            def default_config(self) -> ExperimentConfig:
                return ExperimentConfig(
                    num_qubits=4,
                    state_type="GHZ",
                    ...
                )

        # Usage
        exp = MyExperiment()
        result = exp.run()
        result = exp.run({"error_rate": 0.1})  # With overrides
    """

    name: str
    description: str

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        raise NotImplementedError("Subclasses must implement default_config()")

    def run(
        self,
        overrides: Mapping[str, Any] | None = None,
        *,
        ctx: Any | None = None,
    ) -> ExperimentResult:
        """
        Run experiment using the engine API.

        Args:
            overrides: Optional dict of config fields to override
            ctx: Optional AppContext for session grouping and storage control

        Returns:
            ExperimentResult with full analysis and metrics
        """
        from src.engine.api import run

        config = self.default_config()

        if overrides:
            # Create new config with overrides applied
            config_dict = config.model_dump()
            config_dict.update(overrides)
            config = ExperimentConfig(**config_dict)

        return run(config, ctx=ctx)

    def sweep(
        self,
        parameter_ranges: dict[str, list[Any]],
        **base_overrides: Any,
    ) -> list[ExperimentResult]:
        """
        Run parameter sweep using the engine API.

        Args:
            parameter_ranges: Dict mapping parameter names to lists of values
                             e.g., {"error_rate": [0.01, 0.05, 0.1]}
            **base_overrides: Additional overrides applied to base config

        Returns:
            List of ExperimentResult, one per parameter combination
        """
        from src.engine.api import sweep
        from src.engine.models import SweepManifest

        base_config = self.default_config()

        if base_overrides:
            config_dict = base_config.model_dump()
            config_dict.update(base_overrides)
            base_config = ExperimentConfig(**config_dict)

        manifest = SweepManifest(
            base_config=base_config,
            parameter_ranges=parameter_ranges,
        )

        return sweep(manifest)
