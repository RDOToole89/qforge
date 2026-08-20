"""Tests for hardware-related ExperimentConfig validation."""

import pytest
from pydantic import ValidationError

from qforge.engine.models import ExperimentConfig


class TestHardwareSimMode:
    """Test sim_mode='hardware' config validation."""

    def test_hardware_mode_accepted(self):
        cfg = ExperimentConfig(num_qubits=3, state_type="GHZ", sim_mode="hardware")
        assert cfg.sim_mode == "hardware"

    def test_hardware_with_backend_name(self):
        cfg = ExperimentConfig(
            num_qubits=3,
            state_type="GHZ",
            sim_mode="hardware",
            backend_name="ibm_brisbane",
        )
        assert cfg.backend_name == "ibm_brisbane"

    def test_hardware_with_noise_rejected(self):
        with pytest.raises(Exception, match="hardware.*incompatible.*noise"):
            ExperimentConfig(
                num_qubits=3,
                state_type="GHZ",
                sim_mode="hardware",
                noise_enabled=True,
                noise_type="depolarizing",
            )

    def test_hardware_with_rng_seed_rejected(self):
        with pytest.raises(Exception, match="hardware.*rng_seed"):
            ExperimentConfig(
                num_qubits=3,
                state_type="GHZ",
                sim_mode="hardware",
                rng_seed=42,
            )

    def test_backend_name_without_hardware_rejected(self):
        with pytest.raises(Exception, match="backend_name.*hardware"):
            ExperimentConfig(
                num_qubits=3,
                state_type="GHZ",
                sim_mode="qasm",
                backend_name="ibm_brisbane",
            )

    def test_hardware_shots_over_100k_rejected(self):
        with pytest.raises(Exception, match="100,000"):
            ExperimentConfig(
                num_qubits=3,
                state_type="GHZ",
                sim_mode="hardware",
                shots=200_000,
            )

    def test_hardware_shots_at_100k_accepted(self):
        cfg = ExperimentConfig(
            num_qubits=3,
            state_type="GHZ",
            sim_mode="hardware",
            shots=100_000,
        )
        assert cfg.shots == 100_000

    def test_optimization_level_bounds(self):
        for level in (0, 1, 2, 3):
            cfg = ExperimentConfig(
                num_qubits=3,
                state_type="GHZ",
                sim_mode="hardware",
                optimization_level=level,
            )
            assert cfg.optimization_level == level

    def test_optimization_level_out_of_bounds(self):
        with pytest.raises(ValidationError):
            ExperimentConfig(
                num_qubits=3,
                state_type="GHZ",
                sim_mode="hardware",
                optimization_level=4,
            )

    def test_hardware_session_flag(self):
        cfg = ExperimentConfig(
            num_qubits=3,
            state_type="GHZ",
            sim_mode="hardware",
            hardware_session=True,
        )
        assert cfg.hardware_session is True

    def test_hardware_defaults(self):
        cfg = ExperimentConfig(num_qubits=3, state_type="GHZ", sim_mode="hardware")
        assert cfg.backend_name is None
        assert cfg.optimization_level == 1
        assert cfg.hardware_session is False
        assert cfg.noise_enabled is False
