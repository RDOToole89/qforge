"""
Validation components for experiment parameters and configurations.

Provides robust validation for experiment parameters, component configurations,
and experiment pipelines to ensure correctness and prevent runtime errors.
"""

from typing import Dict, Any, List, Optional, Union, Type
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger("QuantumExperiment.Components.Validators")


class ValidationError(Exception):
    """Exception raised when validation fails."""
    pass


class ParameterValidator:
    """
    Validates individual experiment parameters.
    
    Provides type checking, range validation, and constraint validation
    for experiment parameters.
    """
    
    @staticmethod
    def validate_num_qubits(num_qubits: Any) -> int:
        """
        Validate number of qubits parameter.
        
        Args:
            num_qubits: Value to validate
            
        Returns:
            Validated integer value
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(num_qubits, int):
            try:
                num_qubits = int(num_qubits)
            except (ValueError, TypeError):
                raise ValidationError(f"num_qubits must be an integer, got {type(num_qubits)}")
        
        if num_qubits < 1:
            raise ValidationError(f"num_qubits must be >= 1, got {num_qubits}")
        
        if num_qubits > 20:  # Reasonable upper limit for simulators
            logger.warning(f"Large number of qubits ({num_qubits}) may cause performance issues")
        
        return num_qubits
    
    @staticmethod
    def validate_shots(shots: Any) -> int:
        """
        Validate number of shots parameter.
        
        Args:
            shots: Value to validate
            
        Returns:
            Validated integer value
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(shots, int):
            try:
                shots = int(shots)
            except (ValueError, TypeError):
                raise ValidationError(f"shots must be an integer, got {type(shots)}")
        
        if shots < 1:
            raise ValidationError(f"shots must be >= 1, got {shots}")
        
        if shots > 100000:
            logger.warning(f"Large number of shots ({shots}) may cause long execution times")
        
        return shots
    
    @staticmethod
    def validate_error_rate(error_rate: Any) -> float:
        """
        Validate error rate parameter.
        
        Args:
            error_rate: Value to validate
            
        Returns:
            Validated float value
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(error_rate, (int, float)):
            try:
                error_rate = float(error_rate)
            except (ValueError, TypeError):
                raise ValidationError(f"error_rate must be a number, got {type(error_rate)}")
        
        if error_rate < 0.0:
            raise ValidationError(f"error_rate must be >= 0.0, got {error_rate}")
        
        if error_rate > 1.0:
            raise ValidationError(f"error_rate must be <= 1.0, got {error_rate}")
        
        return float(error_rate)
    
    @staticmethod
    def validate_state_type(state_type: Any) -> str:
        """
        Validate quantum state type parameter.
        
        Args:
            state_type: Value to validate
            
        Returns:
            Validated string value
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(state_type, str):
            raise ValidationError(f"state_type must be a string, got {type(state_type)}")
        
        valid_states = ["BELL", "GHZ", "W", "RANDOM", "CUSTOM"]
        state_type = state_type.upper()
        
        if state_type not in valid_states:
            raise ValidationError(f"state_type must be one of {valid_states}, got {state_type}")
        
        return state_type
    
    @staticmethod
    def validate_noise_type(noise_type: Any) -> str:
        """
        Validate noise type parameter.
        
        Args:
            noise_type: Value to validate
            
        Returns:
            Validated string value
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(noise_type, str):
            raise ValidationError(f"noise_type must be a string, got {type(noise_type)}")
        
        valid_noises = ["DEPOLARIZING", "PHASE_DAMPING", "AMPLITUDE_DAMPING", "PAULI", "THERMAL"]
        noise_type = noise_type.upper()
        
        if noise_type not in valid_noises:
            raise ValidationError(f"noise_type must be one of {valid_noises}, got {noise_type}")
        
        return noise_type


class ConfigurationValidator:
    """
    Validates complete experiment configurations.
    
    Provides validation for entire experiment configurations including
    cross-parameter validation and logical consistency checks.
    """
    
    def __init__(self):
        self.param_validator = ParameterValidator()
    
    def validate_basic_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate basic experiment configuration.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            Validated and normalized configuration
            
        Raises:
            ValidationError: If validation fails
        """
        validated_config = {}
        
        # Required parameters
        if "num_qubits" not in config:
            raise ValidationError("Missing required parameter: num_qubits")
        
        if "shots" not in config:
            config["shots"] = 4096  # Default value
            logger.info("Using default shots: 4096")
        
        # Validate individual parameters
        validated_config["num_qubits"] = self.param_validator.validate_num_qubits(config["num_qubits"])
        validated_config["shots"] = self.param_validator.validate_shots(config["shots"])
        
        # Optional parameters with defaults
        validated_config["state_type"] = self.param_validator.validate_state_type(
            config.get("state_type", "GHZ")
        )
        
        validated_config["sim_mode"] = config.get("sim_mode", "qasm")
        if validated_config["sim_mode"] not in ["qasm", "statevector"]:
            raise ValidationError(f"sim_mode must be 'qasm' or 'statevector', got {validated_config['sim_mode']}")
        
        return validated_config
    
    def validate_noise_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate noise configuration.
        
        Args:
            config: Configuration dictionary with noise parameters
            
        Returns:
            Validated noise configuration
            
        Raises:
            ValidationError: If validation fails
        """
        validated_config = {}
        
        validated_config["noise_enabled"] = config.get("noise_enabled", False)
        
        if validated_config["noise_enabled"]:
            if "noise_type" not in config:
                raise ValidationError("noise_enabled=True but noise_type not specified")
            
            validated_config["noise_type"] = self.param_validator.validate_noise_type(config["noise_type"])
            validated_config["error_rate"] = self.param_validator.validate_error_rate(
                config.get("error_rate", 0.01)
            )
        
        return validated_config
    
    def validate_research_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate research configuration.
        
        Args:
            config: Configuration dictionary with research parameters
            
        Returns:
            Validated research configuration
            
        Raises:
            ValidationError: If validation fails
        """
        validated_config = {}
        
        validated_config["enable_research_metrics"] = config.get("enable_research_metrics", False)
        
        if validated_config["enable_research_metrics"]:
            research_type = config.get("research_type")
            if research_type:
                valid_research_types = ["structured_decoherence", "entanglement_study", "quantum_experiment"]
                if research_type not in valid_research_types:
                    raise ValidationError(f"research_type must be one of {valid_research_types}, got {research_type}")
                validated_config["research_type"] = research_type
        
        return validated_config
    
    def validate_full_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate complete experiment configuration.
        
        Args:
            config: Complete configuration dictionary
            
        Returns:
            Fully validated and normalized configuration
            
        Raises:
            ValidationError: If validation fails
        """
        logger.info("Validating experiment configuration...")
        
        # Validate basic configuration
        validated = self.validate_basic_config(config)
        
        # Validate noise configuration
        noise_config = self.validate_noise_config(config)
        validated.update(noise_config)
        
        # Validate research configuration
        research_config = self.validate_research_config(config)
        validated.update(research_config)
        
        # Cross-parameter validation
        self._validate_cross_parameters(validated)
        
        logger.info("Configuration validation completed successfully")
        return validated
    
    def _validate_cross_parameters(self, config: Dict[str, Any]) -> None:
        """
        Validate relationships between parameters.
        
        Args:
            config: Configuration to validate
            
        Raises:
            ValidationError: If cross-parameter validation fails
        """
        # Example: High precision research should use sufficient shots
        if config.get("enable_research_metrics", False):
            if config["shots"] < 1024:
                logger.warning(f"Low shot count ({config['shots']}) for research-grade experiment")
        
        # Example: Statevector mode with too many qubits
        if config.get("sim_mode") == "statevector" and config["num_qubits"] > 10:
            logger.warning(f"Statevector simulation with {config['num_qubits']} qubits may use excessive memory")
        
        # Example: Noise with statevector mode
        if config.get("noise_enabled", False) and config.get("sim_mode") == "statevector":
            logger.warning("Noise simulation typically more accurate in qasm mode")