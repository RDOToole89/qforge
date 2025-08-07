"""
Experiment Validator for the Quantum Experiment Framework.

This module provides comprehensive validation for experiment configurations,
ensuring experiments are properly formatted and contain valid parameters.
"""

import logging
from typing import Dict, Any, List, Optional
from src.config.constants import VALID_STATE_TYPES, VALID_NOISE_TYPES, VALID_SIM_MODES


class ExperimentValidator:
    """
    Validates experiment configurations.

    This class provides comprehensive validation for experiment configurations,
    ensuring they are properly formatted and contain valid parameters.
    """

    def __init__(self):
        """Initialize the experiment validator."""
        self.logger = logging.getLogger("QuantumExperiment.ExperimentValidator")

    def validate_experiment(self, experiment_config: Dict[str, Any]) -> bool:
        """
        Validate a complete experiment configuration.

        Args:
            experiment_config (Dict[str, Any]): The experiment configuration.

        Returns:
            bool: True if the experiment is valid.
        """
        try:
            # Check required fields
            if not self._validate_required_fields(experiment_config):
                return False

            # Validate metadata
            if not self._validate_metadata(experiment_config):
                return False

            # Validate configuration
            if not self._validate_config(experiment_config.get('config', {})):
                return False

            self.logger.info("Experiment validation passed")
            return True

        except Exception as e:
            self.logger.error(f"Experiment validation failed: {e}")
            return False

    def _validate_required_fields(self, experiment_config: Dict[str, Any]) -> bool:
        """
        Validate that all required fields are present.

        Args:
            experiment_config (Dict[str, Any]): The experiment configuration.

        Returns:
            bool: True if all required fields are present.
        """
        required_fields = ['name', 'description', 'category', 'difficulty', 'config']
        missing_fields = [field for field in required_fields if field not in experiment_config]

        if missing_fields:
            self.logger.error(f"Missing required fields: {missing_fields}")
            return False

        return True

    def _validate_metadata(self, experiment_config: Dict[str, Any]) -> bool:
        """
        Validate experiment metadata.

        Args:
            experiment_config (Dict[str, Any]): The experiment configuration.

        Returns:
            bool: True if metadata is valid.
        """
        # Validate name
        name = experiment_config.get('name', '')
        if not name or not isinstance(name, str):
            self.logger.error("Experiment name must be a non-empty string")
            return False

        # Validate description
        description = experiment_config.get('description', '')
        if not description or not isinstance(description, str):
            self.logger.error("Experiment description must be a non-empty string")
            return False

        # Validate category
        category = experiment_config.get('category', '')
        if not category or not isinstance(category, str):
            self.logger.error("Experiment category must be a non-empty string")
            return False

        # Validate difficulty
        difficulty = experiment_config.get('difficulty', '')
        valid_difficulties = ['beginner', 'intermediate', 'advanced', 'research']
        if difficulty not in valid_difficulties:
            self.logger.error(f"Difficulty must be one of: {valid_difficulties}")
            return False

        return True

    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate experiment configuration parameters.

        Args:
            config (Dict[str, Any]): The experiment configuration parameters.

        Returns:
            bool: True if configuration is valid.
        """
        # Validate num_qubits
        num_qubits = config.get('num_qubits')
        if num_qubits is None or not isinstance(num_qubits, int) or num_qubits < 1:
            self.logger.error("num_qubits must be a positive integer")
            return False

        # Validate state_type
        state_type = config.get('state_type', '').upper()
        if state_type not in VALID_STATE_TYPES:
            self.logger.error(f"state_type must be one of: {VALID_STATE_TYPES}")
            return False

        # Validate noise_type
        noise_type = config.get('noise_type', '').upper()
        if noise_type not in VALID_NOISE_TYPES:
            self.logger.error(f"noise_type must be one of: {VALID_NOISE_TYPES}")
            return False

        # Validate noise_enabled
        noise_enabled = config.get('noise_enabled')
        if not isinstance(noise_enabled, bool):
            self.logger.error("noise_enabled must be a boolean")
            return False

        # Validate shots
        shots = config.get('shots')
        if shots is None or not isinstance(shots, int) or shots < 1:
            self.logger.error("shots must be a positive integer")
            return False

        # Validate sim_mode
        sim_mode = config.get('sim_mode', '').lower()
        if sim_mode not in VALID_SIM_MODES:
            self.logger.error(f"sim_mode must be one of: {VALID_SIM_MODES}")
            return False

        # Validate optional parameters
        if not self._validate_optional_parameters(config):
            return False

        return True

    def _validate_optional_parameters(self, config: Dict[str, Any]) -> bool:
        """
        Validate optional experiment parameters.

        Args:
            config (Dict[str, Any]): The experiment configuration parameters.

        Returns:
            bool: True if optional parameters are valid.
        """
        # Validate error_rate
        error_rate = config.get('error_rate')
        if error_rate is not None:
            if not isinstance(error_rate, (int, float)) or not 0 <= error_rate <= 1:
                self.logger.error("error_rate must be a number between 0 and 1")
                return False

        # Validate z_prob and i_prob for PHASE_FLIP
        if config.get('noise_type', '').upper() == 'PHASE_FLIP':
            z_prob = config.get('z_prob')
            i_prob = config.get('i_prob')

            if z_prob is not None:
                if not isinstance(z_prob, (int, float)) or not 0 <= z_prob <= 1:
                    self.logger.error("z_prob must be a number between 0 and 1")
                    return False

            if i_prob is not None:
                if not isinstance(i_prob, (int, float)) or not 0 <= i_prob <= 1:
                    self.logger.error("i_prob must be a number between 0 and 1")
                    return False

            if z_prob is not None and i_prob is not None:
                if abs(z_prob + i_prob - 1) > 1e-10:
                    self.logger.error("z_prob and i_prob must sum to 1")
                    return False

        # Validate t1 and t2 for THERMAL_RELAXATION
        if config.get('noise_type', '').upper() == 'THERMAL_RELAXATION':
            t1 = config.get('t1')
            t2 = config.get('t2')

            if t1 is not None:
                if not isinstance(t1, (int, float)) or t1 <= 0:
                    self.logger.error("t1 must be a positive number")
                    return False

            if t2 is not None:
                if not isinstance(t2, (int, float)) or t2 <= 0:
                    self.logger.error("t2 must be a positive number")
                    return False

            if t1 is not None and t2 is not None:
                if t2 > t1:
                    self.logger.error("t2 must be less than or equal to t1")
                    return False

        return True

    def validate_experiment_list(self, experiments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate a list of experiments and return valid ones.

        Args:
            experiments (List[Dict[str, Any]]): List of experiment configurations.

        Returns:
            List[Dict[str, Any]]: List of valid experiments.
        """
        valid_experiments = []

        for experiment in experiments:
            if self.validate_experiment(experiment):
                valid_experiments.append(experiment)

        return valid_experiments

    def get_validation_errors(self, experiment_config: Dict[str, Any]) -> List[str]:
        """
        Get detailed validation errors for an experiment.

        Args:
            experiment_config (Dict[str, Any]): The experiment configuration.

        Returns:
            List[str]: List of validation error messages.
        """
        errors = []

        # Check required fields
        required_fields = ['name', 'description', 'category', 'difficulty', 'config']
        missing_fields = [field for field in required_fields if field not in experiment_config]
        if missing_fields:
            errors.append(f"Missing required fields: {missing_fields}")

        # Check metadata
        if 'name' in experiment_config:
            name = experiment_config['name']
            if not name or not isinstance(name, str):
                errors.append("Experiment name must be a non-empty string")

        if 'description' in experiment_config:
            description = experiment_config['description']
            if not description or not isinstance(description, str):
                errors.append("Experiment description must be a non-empty string")

        if 'category' in experiment_config:
            category = experiment_config['category']
            if not category or not isinstance(category, str):
                errors.append("Experiment category must be a non-empty string")

        if 'difficulty' in experiment_config:
            difficulty = experiment_config['difficulty']
            valid_difficulties = ['beginner', 'intermediate', 'advanced', 'research']
            if difficulty not in valid_difficulties:
                errors.append(f"Difficulty must be one of: {valid_difficulties}")

        # Check configuration
        if 'config' in experiment_config:
            config_errors = self._get_config_validation_errors(experiment_config['config'])
            errors.extend(config_errors)

        return errors

    def _get_config_validation_errors(self, config: Dict[str, Any]) -> List[str]:
        """
        Get validation errors for experiment configuration.

        Args:
            config (Dict[str, Any]): The experiment configuration parameters.

        Returns:
            List[str]: List of configuration validation error messages.
        """
        errors = []

        # Check num_qubits
        num_qubits = config.get('num_qubits')
        if num_qubits is None or not isinstance(num_qubits, int) or num_qubits < 1:
            errors.append("num_qubits must be a positive integer")

        # Check state_type
        state_type = config.get('state_type', '').upper()
        if state_type not in VALID_STATE_TYPES:
            errors.append(f"state_type must be one of: {VALID_STATE_TYPES}")

        # Check noise_type
        noise_type = config.get('noise_type', '').upper()
        if noise_type not in VALID_NOISE_TYPES:
            errors.append(f"noise_type must be one of: {VALID_NOISE_TYPES}")

        # Check noise_enabled
        noise_enabled = config.get('noise_enabled')
        if not isinstance(noise_enabled, bool):
            errors.append("noise_enabled must be a boolean")

        # Check shots
        shots = config.get('shots')
        if shots is None or not isinstance(shots, int) or shots < 1:
            errors.append("shots must be a positive integer")

        # Check sim_mode
        sim_mode = config.get('sim_mode', '').lower()
        if sim_mode not in VALID_SIM_MODES:
            errors.append(f"sim_mode must be one of: {VALID_SIM_MODES}")

        return errors
