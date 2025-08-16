"""
Base classes for experiment components and experiments.

Provides foundational classes that define the core interfaces and
patterns for composable quantum experiments.
"""

import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type, Union
from datetime import datetime
import logging

from .metadata import ExperimentMetadata, ComponentMetadata

logger = logging.getLogger("QuantumExperiment.Components.Base")


class ExperimentComponent(ABC):
    """
    Base class for all experiment components.

    Components are modular, reusable pieces that can be composed
    to build complex experiments. Examples include state preparation,
    noise models, analysis routines, and visualization components.
    """

    def __init__(self, name: str, version: str = "1.0.0", **kwargs):
        """
        Initialize the experiment component.

        Args:
            name: Human-readable name for the component
            version: Semantic version of the component
            **kwargs: Additional component-specific parameters
        """
        self.metadata = ComponentMetadata(
            name=name,
            version=version,
            component_type=self.__class__.__name__,
            created_at=datetime.now(),
            **kwargs
        )
        self.logger = logging.getLogger(f"QuantumExperiment.Components.{name}")

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the component's functionality.

        Args:
            context: Execution context containing inputs and shared state

        Returns:
            Results dictionary with component outputs
        """
        pass

    @abstractmethod
    def validate_inputs(self, context: Dict[str, Any]) -> bool:
        """
        Validate that the component has required inputs in the context.

        Args:
            context: Execution context to validate

        Returns:
            True if inputs are valid, False otherwise
        """
        pass

    def get_dependencies(self) -> List[str]:
        """
        Get list of component dependencies (by name).

        Returns:
            List of component names this component depends on
        """
        return []

    def get_outputs(self) -> List[str]:
        """
        Get list of outputs this component produces.

        Returns:
            List of output keys this component adds to context
        """
        return []


class BaseExperiment(ABC):
    """
    Base class for all quantum experiments.

    Experiments are composed of multiple components that work together
    to execute a complete quantum experiment workflow.
    """

    def __init__(self, name: str, description: str = "", **config):
        """
        Initialize the experiment.

        Args:
            name: Human-readable name for the experiment
            description: Detailed description of the experiment
            **config: Experiment configuration parameters
        """
        self.experiment_id = str(uuid.uuid4())[:8]
        self.metadata = ExperimentMetadata(
            name=name,
            description=description,
            experiment_id=self.experiment_id,
            created_at=datetime.now(),
            **config
        )
        self.components: List[ExperimentComponent] = []
        self.config = config
        self.context: Dict[str, Any] = {}
        self.logger = logging.getLogger(f"QuantumExperiment.Experiments.{name}")

    def add_component(self, component: ExperimentComponent) -> 'BaseExperiment':
        """
        Add a component to the experiment pipeline.

        Args:
            component: Component to add to the experiment

        Returns:
            Self for method chaining
        """
        self.components.append(component)
        self.logger.info(f"Added component: {component.metadata.name}")
        return self

    def validate_pipeline(self) -> bool:
        """
        Validate that the experiment pipeline is valid.

        Checks component dependencies and input/output compatibility.

        Returns:
            True if pipeline is valid, False otherwise
        """
        # Build dependency graph
        available_outputs = set()

        for component in self.components:
            # Check if dependencies are satisfied
            for dep in component.get_dependencies():
                if dep not in available_outputs:
                    self.logger.error(f"Component {component.metadata.name} missing dependency: {dep}")
                    return False

            # Add outputs to available set
            available_outputs.update(component.get_outputs())

        return True

    def execute(self) -> Dict[str, Any]:
        """
        Execute the complete experiment pipeline.

        Returns:
            Dictionary containing experiment results
        """
        if not self.validate_pipeline():
            raise ValueError("Experiment pipeline validation failed")

        self.logger.info(f"Starting experiment: {self.metadata.name}")
        start_time = datetime.now()

        # Initialize context with experiment config
        self.context = {
            "experiment_id": self.experiment_id,
            "experiment_config": self.config,
            "metadata": self.metadata,
            **self.config
        }

        # Execute components in order
        for component in self.components:
            self.logger.info(f"Executing component: {component.metadata.name}")

            # Validate component inputs
            if not component.validate_inputs(self.context):
                raise ValueError(f"Component {component.metadata.name} input validation failed")

            # Execute component
            try:
                component_results = component.execute(self.context)
                self.context.update(component_results)
                self.logger.info(f"Component {component.metadata.name} completed successfully")
            except Exception as e:
                self.logger.error(f"Component {component.metadata.name} failed: {e}")
                raise

        # Add execution metadata
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        self.context.update({
            "execution_metadata": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "execution_time_seconds": execution_time,
                "components_executed": len(self.components),
                "success": True
            }
        })

        self.logger.info(f"Experiment {self.metadata.name} completed in {execution_time:.2f}s")
        return self.context

    @abstractmethod
    def configure(self) -> None:
        """
        Configure the experiment by adding and configuring components.

        This method should be implemented by concrete experiment classes
        to define their specific component pipeline.
        """
        pass

    def to_experiment_spec(self) -> Dict[str, Any]:
        """
        Convert experiment to experiment_spec format.
        
        Returns:
            Dictionary in current experiment_spec schema format
        """
        from ..validation import SchemaValidator
        from datetime import datetime
        import uuid
        
        # Get current schema version dynamically
        validator = SchemaValidator()
        
        experiment_spec = {
            "$schema": f"../../../{validator.version}/core/experiment_spec.schema.json",
            "experiment_metadata": {
                "experiment_id": self.experiment_id,
                "name": self.metadata.name,
                "description": self.metadata.description,
                "phase": "planning",
                "created_timestamp": datetime.now().isoformat(),
                "tags": getattr(self.metadata, 'tags', []),
                "difficulty_level": getattr(self.metadata, 'difficulty_level', 'intermediate')
            },
            "quantum_configuration": {
                "num_qubits": self.config.get("num_qubits", 3),
                "state_type": self.config.get("state_type", "GHZ"),
                "shots": self.config.get("shots", 1024)
            },
            "noise_configuration": {
                "noise_enabled": self.config.get("noise_enabled", False)
            },
            "research_configuration": {
                "research_type": getattr(self.metadata, 'research_type', 'general'),
                "enable_research_metrics": self.config.get("enable_research_metrics", False),
                "statistical_validation": True
            },
            "provenance": {
                "created_by": "base_experiment",
                "creation_method": "component_system",
                "framework_version": validator.version,
                "experiment_class": self.__class__.__name__
            }
        }
        
        # Add noise configuration details if enabled
        if self.config.get("noise_enabled", False):
            experiment_spec["noise_configuration"].update({
                "noise_type": self.config.get("noise_type", "depolarizing"),
                "error_rate": self.config.get("error_rate", 0.01)
            })
            
            # Add noise-specific parameters
            for param in ["t1", "t2", "z_prob", "i_prob", "gamma"]:
                if param in self.config:
                    experiment_spec["noise_configuration"][param] = self.config[param]
        
        return experiment_spec

    def validate_schema_compatibility(self) -> bool:
        """
        Validate that this experiment is compatible with current schemas.
        
        Returns:
            True if compatible, False otherwise
        """
        try:
            experiment_spec = self.to_experiment_spec()
            from ..validation import SchemaValidator
            validator = SchemaValidator()
            return validator.validate(experiment_spec)
        except Exception as e:
            self.logger.error(f"Schema validation failed: {e}")
            return False

    def get_validation_errors(self) -> List[str]:
        """
        Get schema validation errors for this experiment.
        
        Returns:
            List of validation error messages
        """
        try:
            experiment_spec = self.to_experiment_spec()
            from ..validation import SchemaValidator
            validator = SchemaValidator()
            return validator.get_validation_errors(experiment_spec)
        except Exception as e:
            return [f"Failed to generate experiment spec: {e}"]
