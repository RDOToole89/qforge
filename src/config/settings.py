"""
Application settings for the Quantum Experiment Framework.

This module centralizes all application settings and configuration
management for the quantum experiment framework.
"""

import os
from typing import Dict, Any


class Settings:
    """
    Application settings manager for the Quantum Experiment Framework.

    This class provides centralized access to all application settings,
    with support for environment variables and configuration files.
    """

    def __init__(self):
        """Initialize the settings manager."""
        self._load_defaults()
        self._load_environment()

    def _load_defaults(self) -> None:
        """Load default application settings."""
        # === ✅ Default Experiment Parameters ===
        self.DEFAULT_NUM_QUBITS = 3
        self.DEFAULT_STATE_TYPE = "GHZ"
        self.DEFAULT_NOISE_TYPE = "DEPOLARIZING"
        self.DEFAULT_NOISE_ENABLED = True
        self.DEFAULT_SHOTS = 1024
        self.DEFAULT_SIM_MODE = "qasm"

        # === 🔧 Default Noise Parameters ===
        self.DEFAULT_ERROR_RATE = 0.1
        self.DEFAULT_T1 = 100e-6
        self.DEFAULT_T2 = 80e-6
        self.DEFAULT_Z_PROB = 0.5
        self.DEFAULT_I_PROB = 0.5

        # === 🎛 Default State Parameters ===
        self.DEFAULT_CLUSTER_LATTICE = "2D"

        # === 📂 File & Logging Configurations ===
        self.DEFAULT_RESULTS_DIR = "results"
        self.DEFAULT_LOGS_DIR = "logs"
        self.DEFAULT_LOG_LEVEL = "INFO"

        # === 🔌 Plugin and Extension Settings ===
        self.PLUGIN_DIR = "plugins"
        self.EXPERIMENT_DIR = "experiments"
        self.TEMPLATE_DIR = "templates"

    def _load_environment(self) -> None:
        """Load settings from environment variables."""
        # Override defaults with environment variables if present
        if os.getenv("QEXP_NUM_QUBITS"):
            self.DEFAULT_NUM_QUBITS = int(os.getenv("QEXP_NUM_QUBITS"))

        if os.getenv("QEXP_STATE_TYPE"):
            self.DEFAULT_STATE_TYPE = os.getenv("QEXP_STATE_TYPE")

        if os.getenv("QEXP_NOISE_TYPE"):
            self.DEFAULT_NOISE_TYPE = os.getenv("QEXP_NOISE_TYPE")

        if os.getenv("QEXP_NOISE_ENABLED"):
            self.DEFAULT_NOISE_ENABLED = (
                os.getenv("QEXP_NOISE_ENABLED").lower() == "true"
            )

        if os.getenv("QEXP_SHOTS"):
            self.DEFAULT_SHOTS = int(os.getenv("QEXP_SHOTS"))

        if os.getenv("QEXP_SIM_MODE"):
            self.DEFAULT_SIM_MODE = os.getenv("QEXP_SIM_MODE")

        if os.getenv("QEXP_ERROR_RATE"):
            self.DEFAULT_ERROR_RATE = float(os.getenv("QEXP_ERROR_RATE"))

        if os.getenv("QEXP_LOG_LEVEL"):
            self.DEFAULT_LOG_LEVEL = os.getenv("QEXP_LOG_LEVEL")

        if os.getenv("QEXP_RESULTS_DIR"):
            self.DEFAULT_RESULTS_DIR = os.getenv("QEXP_RESULTS_DIR")

        if os.getenv("QEXP_LOGS_DIR"):
            self.DEFAULT_LOGS_DIR = os.getenv("QEXP_LOGS_DIR")

    def get_experiment_defaults(self) -> Dict[str, Any]:
        """
        Get default experiment parameters.

        Returns:
            Dict[str, Any]: Default experiment parameters.
        """
        return {
            "num_qubits": self.DEFAULT_NUM_QUBITS,
            "state_type": self.DEFAULT_STATE_TYPE,
            "noise_type": self.DEFAULT_NOISE_TYPE,
            "noise_enabled": self.DEFAULT_NOISE_ENABLED,
            "shots": self.DEFAULT_SHOTS,
            "sim_mode": self.DEFAULT_SIM_MODE,
            "error_rate": self.DEFAULT_ERROR_RATE,
            "t1": self.DEFAULT_T1,
            "t2": self.DEFAULT_T2,
            "z_prob": self.DEFAULT_Z_PROB,
            "i_prob": self.DEFAULT_I_PROB,
            "cluster_lattice": self.DEFAULT_CLUSTER_LATTICE,
        }

    def get_logging_config(self) -> Dict[str, Any]:
        """
        Get logging configuration.

        Returns:
            Dict[str, Any]: Logging configuration.
        """
        return {
            "log_level": self.DEFAULT_LOG_LEVEL,
            "logs_dir": self.DEFAULT_LOGS_DIR,
            "results_dir": self.DEFAULT_RESULTS_DIR,
        }

    def get_plugin_config(self) -> Dict[str, Any]:
        """
        Get plugin configuration.

        Returns:
            Dict[str, Any]: Plugin configuration.
        """
        return {
            "plugin_dir": self.PLUGIN_DIR,
            "experiment_dir": self.EXPERIMENT_DIR,
            "template_dir": self.TEMPLATE_DIR,
        }

    def validate_settings(self) -> bool:
        """
        Validate all settings are within acceptable ranges.

        Returns:
            bool: True if settings are valid.
        """
        # Validate numeric settings
        if self.DEFAULT_NUM_QUBITS < 1:
            raise ValueError("DEFAULT_NUM_QUBITS must be >= 1")

        if self.DEFAULT_SHOTS < 1:
            raise ValueError("DEFAULT_SHOTS must be >= 1")

        if not 0 <= self.DEFAULT_ERROR_RATE <= 1:
            raise ValueError("DEFAULT_ERROR_RATE must be between 0 and 1")

        if not 0 <= self.DEFAULT_Z_PROB <= 1:
            raise ValueError("DEFAULT_Z_PROB must be between 0 and 1")

        if not 0 <= self.DEFAULT_I_PROB <= 1:
            raise ValueError("DEFAULT_I_PROB must be between 0 and 1")

        # Validate string settings
        valid_sim_modes = ["qasm", "density"]
        if self.DEFAULT_SIM_MODE not in valid_sim_modes:
            raise ValueError(f"DEFAULT_SIM_MODE must be one of {valid_sim_modes}")

        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        if self.DEFAULT_LOG_LEVEL not in valid_log_levels:
            raise ValueError(f"DEFAULT_LOG_LEVEL must be one of {valid_log_levels}")

        return True


# Global settings instance
settings = Settings()


# Convenience functions for backward compatibility
def get_defaults() -> Dict[str, Any]:
    """Get default experiment parameters."""
    return settings.get_experiment_defaults()


def get_logging_config() -> Dict[str, Any]:
    """Get logging configuration."""
    return settings.get_logging_config()


def get_plugin_config() -> Dict[str, Any]:
    """Get plugin configuration."""
    return settings.get_plugin_config()


def validate_settings() -> bool:
    """Validate all settings."""
    return settings.validate_settings()
