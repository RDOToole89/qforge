"""
Tests for multi-backend simulation support (qasm, statevector, density_matrix).
"""

import numpy as np
import pytest

from src.engine.api import run
from src.engine.models import ExperimentConfig


# ---------------------------------------------------------------------------
# Config validation
# ---------------------------------------------------------------------------


class TestConfigValidation:
    """Test sim_mode config validation and cross-field checks."""

    def test_qasm_mode_accepted(self):
        cfg = ExperimentConfig(num_qubits=2, state_type="GHZ", sim_mode="qasm")
        assert cfg.sim_mode == "qasm"

    def test_statevector_mode_accepted(self):
        cfg = ExperimentConfig(num_qubits=2, state_type="GHZ", sim_mode="statevector")
        assert cfg.sim_mode == "statevector"

    def test_density_matrix_mode_accepted(self):
        cfg = ExperimentConfig(num_qubits=2, state_type="GHZ", sim_mode="density_matrix")
        assert cfg.sim_mode == "density_matrix"

    def test_invalid_mode_rejected(self):
        with pytest.raises(Exception):
            ExperimentConfig(num_qubits=2, state_type="GHZ", sim_mode="invalid")

    def test_statevector_plus_noise_rejected(self):
        with pytest.raises(Exception, match="statevector.*incompatible.*noise"):
            ExperimentConfig(
                num_qubits=2,
                state_type="GHZ",
                sim_mode="statevector",
                noise_enabled=True,
                noise_type="depolarizing",
                error_rate=0.1,
            )

    def test_density_matrix_plus_noise_accepted(self):
        cfg = ExperimentConfig(
            num_qubits=2,
            state_type="GHZ",
            sim_mode="density_matrix",
            noise_enabled=True,
            noise_type="depolarizing",
            error_rate=0.1,
        )
        assert cfg.sim_mode == "density_matrix"
        assert cfg.noise_enabled is True


# ---------------------------------------------------------------------------
# QASM mode (baseline — should be unchanged)
# ---------------------------------------------------------------------------


class TestQasmMode:
    """Test that QASM mode continues to work as before."""

    def test_qasm_basic(self):
        result = run(ExperimentConfig(
            num_qubits=2, state_type="GHZ", sim_mode="qasm",
            shots=500, rng_seed=42,
        ))
        meas = result.analysis.measurement_results
        assert meas.total_shots == 500
        assert meas.statevector is None
        assert meas.density_matrix is None
        assert meas.fidelity is None

    def test_qasm_with_noise(self):
        result = run(ExperimentConfig(
            num_qubits=3, state_type="GHZ", sim_mode="qasm",
            noise_enabled=True, noise_type="depolarizing", error_rate=0.05,
            shots=500, rng_seed=42,
        ))
        meas = result.analysis.measurement_results
        assert meas.total_shots == 500
        # Noisy GHZ should have more than just 000/111
        assert meas.unique_outcomes >= 2


# ---------------------------------------------------------------------------
# Statevector mode
# ---------------------------------------------------------------------------


class TestStatevectorMode:
    """Test exact statevector simulation."""

    def test_statevector_ghz(self):
        result = run(ExperimentConfig(
            num_qubits=3, state_type="GHZ", sim_mode="statevector",
            shots=1000, rng_seed=42,
        ))
        meas = result.analysis.measurement_results

        # Should have statevector
        assert meas.statevector is not None
        assert len(meas.statevector) == 8  # 2^3

        # Each element is [real, imag]
        assert len(meas.statevector[0]) == 2

        # GHZ: only |000> and |111> should have amplitude
        sv_complex = [complex(ri[0], ri[1]) for ri in meas.statevector]
        probs = [abs(c) ** 2 for c in sv_complex]
        assert probs[0] > 0.4  # |000>
        assert probs[7] > 0.4  # |111>

        # Fidelity should be ~1.0 (exact noiseless state)
        assert meas.fidelity is not None
        assert meas.fidelity > 0.999

        # Should NOT have density matrix
        assert meas.density_matrix is None

        # Counts should be synthesized
        assert meas.total_shots == 1000
        assert set(meas.raw_counts.keys()) <= {"000", "111"}

    def test_statevector_bell(self):
        result = run(ExperimentConfig(
            num_qubits=2, state_type="BELL", sim_mode="statevector",
            shots=500, rng_seed=123,
        ))
        meas = result.analysis.measurement_results
        assert meas.statevector is not None
        assert len(meas.statevector) == 4  # 2^2
        assert meas.fidelity is not None
        assert meas.fidelity > 0.999

    def test_statevector_superposition(self):
        result = run(ExperimentConfig(
            num_qubits=2, state_type="SUPERPOSITION", sim_mode="statevector",
            shots=500, rng_seed=99,
        ))
        meas = result.analysis.measurement_results
        assert meas.statevector is not None
        assert meas.fidelity is not None
        # All 4 outcomes should be roughly equal
        assert meas.unique_outcomes >= 3

    def test_statevector_deterministic(self):
        """Same seed should give identical counts."""
        results = []
        for _ in range(2):
            r = run(ExperimentConfig(
                num_qubits=3, state_type="GHZ", sim_mode="statevector",
                shots=1000, rng_seed=42,
            ))
            results.append(r.analysis.measurement_results.raw_counts)
        assert results[0] == results[1]


# ---------------------------------------------------------------------------
# Density matrix mode
# ---------------------------------------------------------------------------


class TestDensityMatrixMode:
    """Test full density matrix simulation."""

    def test_density_matrix_noiseless(self):
        result = run(ExperimentConfig(
            num_qubits=2, state_type="GHZ", sim_mode="density_matrix",
            shots=500, rng_seed=42,
        ))
        meas = result.analysis.measurement_results

        # Should have density matrix
        assert meas.density_matrix is not None
        dim = 2 ** 2  # 2 qubits
        assert len(meas.density_matrix) == dim
        assert len(meas.density_matrix[0]) == dim
        # Each element is [real, imag]
        assert len(meas.density_matrix[0][0]) == 2

        # Fidelity should be high (noiseless)
        assert meas.fidelity is not None
        assert meas.fidelity > 0.95

        # Should NOT have statevector
        assert meas.statevector is None

    def test_density_matrix_with_noise(self):
        result = run(ExperimentConfig(
            num_qubits=3, state_type="GHZ", sim_mode="density_matrix",
            noise_enabled=True, noise_type="depolarizing", error_rate=0.1,
            shots=500, rng_seed=42,
        ))
        meas = result.analysis.measurement_results

        assert meas.density_matrix is not None
        assert len(meas.density_matrix) == 8  # 2^3

        # Fidelity should be < 1 (noise degrades state)
        assert meas.fidelity is not None
        assert meas.fidelity < 0.95

        # Counts should still work
        assert meas.total_shots == 500

    def test_density_matrix_trace_one(self):
        """Trace of density matrix should be ~1."""
        result = run(ExperimentConfig(
            num_qubits=2, state_type="BELL", sim_mode="density_matrix",
            shots=100, rng_seed=42,
        ))
        dm = result.analysis.measurement_results.density_matrix
        assert dm is not None

        # Reconstruct complex matrix and check trace
        dm_complex = np.array([[complex(e[0], e[1]) for e in row] for row in dm])
        trace = np.real(np.trace(dm_complex))
        assert abs(trace - 1.0) < 1e-6


# ---------------------------------------------------------------------------
# Cross-mode: metrics pipeline compatibility
# ---------------------------------------------------------------------------


class TestMetricsCompatibility:
    """Test that all simulation modes produce data compatible with the metrics pipeline."""

    @pytest.mark.parametrize("sim_mode,noise", [
        ("qasm", True),
        ("statevector", False),
        ("density_matrix", True),
    ])
    def test_metrics_work_with_mode(self, sim_mode, noise):
        cfg = dict(
            num_qubits=3, state_type="GHZ", sim_mode=sim_mode,
            shots=500, metrics="quick", rng_seed=42,
        )
        if noise:
            cfg.update(noise_enabled=True, noise_type="depolarizing", error_rate=0.05)
        result = run(ExperimentConfig(**cfg))

        assert result.metrics_bundle is not None
        ss = result.metrics_bundle.value("structure_score")
        assert ss is not None
        assert 0.0 <= ss <= 1.0
