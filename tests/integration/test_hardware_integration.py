"""Integration tests for IBM Quantum hardware execution.

These tests require active IBM Quantum credentials and are skipped
by default. Set the IBM_QUANTUM_TOKEN environment variable to enable.

Run with:
    IBM_QUANTUM_TOKEN=1 pytest tests/integration/test_hardware_integration.py -v
"""

import os

import pytest

skip_no_hardware = pytest.mark.skipif(
    not os.environ.get("IBM_QUANTUM_TOKEN"),
    reason="IBM Quantum credentials not configured (set IBM_QUANTUM_TOKEN=1 to enable)",
)


@skip_no_hardware
class TestHardwareIntegration:
    """End-to-end tests on real IBM Quantum hardware."""

    def test_ghz_3qubit_hardware(self):
        """Run a 3-qubit GHZ experiment on real hardware."""
        from src.engine.api import run
        from src.engine.models import ExperimentConfig

        result = run(
            ExperimentConfig(
                num_qubits=3,
                state_type="GHZ",
                sim_mode="hardware",
                shots=100,
                visualization_type="none",
            )
        )

        assert result.status == "completed"
        counts = result.analysis.measurement_results.raw_counts
        assert len(counts) > 0
        assert result.analysis.measurement_results.total_shots == 100

    def test_hardware_provenance_populated(self):
        """Hardware provenance includes backend and transpilation info."""
        from src.engine.api import run
        from src.engine.models import ExperimentConfig

        result = run(
            ExperimentConfig(
                num_qubits=2,
                state_type="GHZ",
                sim_mode="hardware",
                shots=100,
                visualization_type="none",
            )
        )

        sim_info = result.provenance.simulator_info
        assert sim_info["sim_mode"] == "hardware"
        assert "backend_name" in sim_info
        assert "job_id" in sim_info

        transp = result.provenance.transpilation_summary
        assert "optimization_level" in transp
        assert "qubit_layout" in transp
        assert "swap_count" in transp

    def test_hardware_fidelity_computed(self):
        """Hardware results should have a counts-based fidelity estimate."""
        from src.engine.api import run
        from src.engine.models import ExperimentConfig

        result = run(
            ExperimentConfig(
                num_qubits=2,
                state_type="GHZ",
                sim_mode="hardware",
                shots=1000,
                visualization_type="none",
            )
        )

        fidelity = result.analysis.measurement_results.fidelity
        assert fidelity is not None
        assert 0.0 < fidelity <= 1.0
