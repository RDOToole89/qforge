"""
Experiment Manager for the Quantum Experiment Framework.

This module provides centralized experiment management including
discovery, loading, validation, and execution of experiments.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from src.config.settings import settings
from src.core.experiment_runner import ExperimentRunner


class ExperimentManager:
    """
    Centralized experiment management system.

    This class provides comprehensive experiment management including
    discovery, loading, validation, and execution of experiments.
    """

    def __init__(self):
        """Initialize the experiment manager."""
        self.logger = logging.getLogger("QuantumExperiment.ExperimentManager")
        self.experiments: Dict[str, Dict[str, Any]] = {}
        self.categories: Dict[str, List[str]] = {}
        self.difficulty_levels: Dict[str, List[str]] = {}

        # Load experiments
        self._load_preset_experiments()
        self._load_custom_experiments()
        self._load_plugins()

        # Organize by categories and difficulty
        self._organize_experiments()

    def _load_preset_experiments(self) -> None:
        """Load preset experiments from the presets directory."""
        try:
            from .presets import load_preset_experiments

            preset_experiments = load_preset_experiments()
            self.experiments.update(preset_experiments)
            self.logger.info(f"Loaded {len(preset_experiments)} preset experiments")
        except ImportError:
            self.logger.warning("Preset experiments not available yet")

    def _load_custom_experiments(self) -> None:
        """Load custom experiments from the experiments directory."""
        experiments_dir = Path(settings.EXPERIMENT_DIR)
        if not experiments_dir.exists():
            self.logger.info(f"Creating experiments directory: {experiments_dir}")
            experiments_dir.mkdir(parents=True, exist_ok=True)
            return

        for experiment_file in experiments_dir.glob("*.json"):
            try:
                with open(experiment_file, "r") as f:
                    experiment_data = json.load(f)

                experiment_id = experiment_file.stem
                experiment_data["id"] = experiment_id
                experiment_data["source"] = "custom"
                experiment_data["file_path"] = str(experiment_file)

                self.experiments[experiment_id] = experiment_data
                self.logger.info(f"Loaded custom experiment: {experiment_id}")

            except Exception as e:
                self.logger.error(f"Failed to load experiment {experiment_file}: {e}")

    def _load_plugins(self) -> None:
        """Load experiment plugins."""
        try:
            from .plugins import load_plugins

            plugin_experiments = load_plugins()
            self.experiments.update(plugin_experiments)
            self.logger.info(f"Loaded {len(plugin_experiments)} plugin experiments")
        except ImportError:
            self.logger.warning("Plugin system not available yet")

    def _organize_experiments(self) -> None:
        """Organize experiments by categories and difficulty levels."""
        for experiment_id, experiment in self.experiments.items():
            # Organize by category
            category = experiment.get("category", "unknown")
            if category not in self.categories:
                self.categories[category] = []
            self.categories[category].append(experiment_id)

            # Organize by difficulty
            difficulty = experiment.get("difficulty", "unknown")
            if difficulty not in self.difficulty_levels:
                self.difficulty_levels[difficulty] = []
            self.difficulty_levels[difficulty].append(experiment_id)

    def get_experiment(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific experiment by ID.

        Args:
            experiment_id (str): The experiment ID.

        Returns:
            Optional[Dict[str, Any]]: The experiment configuration or None.
        """
        return self.experiments.get(experiment_id)

    def list_experiments(
        self, category: Optional[str] = None, difficulty: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List experiments with optional filtering.

        Args:
            category (str, optional): Filter by category.
            difficulty (str, optional): Filter by difficulty.

        Returns:
            List[Dict[str, Any]]: List of experiment configurations.
        """
        filtered_experiments = []

        for experiment_id, experiment in self.experiments.items():
            # Apply category filter
            if category and experiment.get("category") != category:
                continue

            # Apply difficulty filter
            if difficulty and experiment.get("difficulty") != difficulty:
                continue

            filtered_experiments.append({"id": experiment_id, **experiment})

        return filtered_experiments

    def get_categories(self) -> List[str]:
        """
        Get all available experiment categories.

        Returns:
            List[str]: List of category names.
        """
        return list(self.categories.keys())

    def get_difficulty_levels(self) -> List[str]:
        """
        Get all available difficulty levels.

        Returns:
            List[str]: List of difficulty levels.
        """
        return list(self.difficulty_levels.keys())

    def search_experiments(self, query: str) -> List[Dict[str, Any]]:
        """
        Search experiments by name or description.

        Args:
            query (str): Search query.

        Returns:
            List[Dict[str, Any]]: Matching experiments.
        """
        query = query.lower()
        matching_experiments = []

        for experiment_id, experiment in self.experiments.items():
            name = experiment.get("name", "").lower()
            description = experiment.get("description", "").lower()

            if query in name or query in description:
                matching_experiments.append({"id": experiment_id, **experiment})

        return matching_experiments

    def add_experiment(
        self, experiment_id: str, experiment_config: Dict[str, Any]
    ) -> bool:
        """
        Add a new experiment.

        Args:
            experiment_id (str): Unique experiment ID.
            experiment_config (Dict[str, Any]): Experiment configuration.

        Returns:
            bool: True if added successfully.
        """
        try:
            # Validate experiment configuration using version-agnostic schemas
            from .validation import validate_experiment

            if not validate_experiment(experiment_config):
                return False

            # Add experiment
            experiment_config["id"] = experiment_id
            experiment_config["source"] = "custom"
            self.experiments[experiment_id] = experiment_config

            # Reorganize
            self._organize_experiments()

            self.logger.info(f"Added experiment: {experiment_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to add experiment {experiment_id}: {e}")
            return False

    def remove_experiment(self, experiment_id: str) -> bool:
        """
        Remove an experiment.

        Args:
            experiment_id (str): The experiment ID to remove.

        Returns:
            bool: True if removed successfully.
        """
        if experiment_id in self.experiments:
            experiment = self.experiments[experiment_id]

            # Remove from custom experiments file if it exists
            if experiment.get("source") == "custom" and "file_path" in experiment:
                try:
                    os.remove(experiment["file_path"])
                except OSError:
                    pass  # File might not exist

            # Remove from memory
            del self.experiments[experiment_id]

            # Reorganize
            self._organize_experiments()

            self.logger.info(f"Removed experiment: {experiment_id}")
            return True

        return False

    def run_experiment(
        self, experiment_id: str, custom_params: Optional[Dict[str, Any]] = None
    ) -> Optional[Any]:
        """
        Run an experiment.

        Args:
            experiment_id (str): The experiment ID to run.
            custom_params (Dict[str, Any], optional): Custom parameters to override.

        Returns:
            Optional[Any]: Experiment results or None if failed.
        """
        experiment = self.get_experiment(experiment_id)
        if not experiment:
            self.logger.error(f"Experiment not found: {experiment_id}")
            return None

        try:
            # Get experiment parameters
            params = experiment.get("config", {}).copy()

            # Override with custom parameters
            if custom_params:
                params.update(custom_params)

            # Filter out non-experiment parameters
            valid_params = {
                "num_qubits",
                "state_type",
                "noise_type",
                "noise_enabled",
                "shots",
                "sim_mode",
                "error_rate",
                "z_prob",
                "i_prob",
                "t1",
                "t2",
                "rng_seed",
            }
            experiment_params = {k: v for k, v in params.items() if k in valid_params}

            # Handle custom_params separately
            if "custom_params" in params:
                experiment_params["custom_params"] = params["custom_params"]

            # Run the experiment
            self.logger.info(f"Running experiment with params: {experiment_params}")
            runner = ExperimentRunner(experiment_id)
            circuit, result = runner.run_experiment(**experiment_params)

            # Check if research-grade analysis is enabled
            enable_research = params.get("enable_research_metrics", False)
            research_type = experiment.get("research_type", None)

            if enable_research or research_type:
                # Import research handler
                from ..core.research_handler import ResearchExperimentHandler

                # Create research analysis
                research_handler = ResearchExperimentHandler()
                full_config = experiment.get("config", {}).copy()
                full_config.update(params)

                research_analysis = research_handler.process_experiment_result(
                    circuit=circuit,
                    result=result,
                    experiment_config=full_config,
                    experiment_id=experiment_id,
                )

                # Save research results
                result_file = research_handler.save_research_result(research_analysis)
                self.logger.info(f"Research analysis saved to: {result_file}")

                # Return both standard result and research analysis
                return {
                    "circuit": circuit,
                    "result": result,
                    "research_analysis": research_analysis,
                    "research_file": result_file,
                }
            else:
                # Standard return format for backward compatibility
                self.logger.info(f"Successfully ran experiment: {experiment_id}")
                return (circuit, result)

        except Exception as e:
            self.logger.error(f"Failed to run experiment {experiment_id}: {e}")
            return None

    def export_experiment(self, experiment_id: str, file_path: str) -> bool:
        """
        Export an experiment to a file.

        Args:
            experiment_id (str): The experiment ID to export.
            file_path (str): Path to save the experiment.

        Returns:
            bool: True if exported successfully.
        """
        experiment = self.get_experiment(experiment_id)
        if not experiment:
            return False

        try:
            with open(file_path, "w") as f:
                json.dump(experiment, f, indent=2)

            self.logger.info(f"Exported experiment {experiment_id} to {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to export experiment {experiment_id}: {e}")
            return False

    def import_experiment(self, file_path: str) -> Optional[str]:
        """
        Import an experiment from a file.

        Args:
            file_path (str): Path to the experiment file.

        Returns:
            Optional[str]: Experiment ID if imported successfully.
        """
        try:
            with open(file_path, "r") as f:
                experiment_config = json.load(f)

            experiment_id = experiment_config.get("id", Path(file_path).stem)

            if self.add_experiment(experiment_id, experiment_config):
                return experiment_id

            return None

        except Exception as e:
            self.logger.error(f"Failed to import experiment from {file_path}: {e}")
            return None


def get_experiment_manager() -> ExperimentManager:
    """
    Get a fresh experiment manager instance.

    Returns:
        ExperimentManager: A new experiment manager instance.
    """
    return ExperimentManager()
