"""Engine wiring for ExperimentConfig.observables."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from qforge.engine.api import run
from qforge.engine.models import ExperimentConfig


def test_config_validates_pauli_length_and_chars() -> None:
    cfg = ExperimentConfig(num_qubits=2, state_type="BELL", observables=["zz"])
    assert cfg.observables == ["ZZ"]
    with pytest.raises(ValidationError, match="length"):
        ExperimentConfig(num_qubits=2, state_type="BELL", observables=["ZZZ"])
    with pytest.raises(ValidationError, match="non-Pauli"):
        ExperimentConfig(num_qubits=2, state_type="BELL", observables=["ZA"])


def test_bell_statevector_exact_correlators() -> None:
    result = run(
        ExperimentConfig(
            num_qubits=2,
            state_type="BELL",
            sim_mode="statevector",
            shots=128,
            rng_seed=0,
            observables=["ZZ", "XX", "YY"],
            visualization_type="none",
        )
    )
    estimates = result.analysis.measurement_results.observables
    assert estimates is not None
    assert estimates["ZZ"].value == pytest.approx(1.0, abs=1e-9)
    assert estimates["XX"].value == pytest.approx(1.0, abs=1e-9)
    assert estimates["YY"].value == pytest.approx(-1.0, abs=1e-9)
    assert estimates["ZZ"].stderr is None
    assert estimates["ZZ"].shots is None


def test_bell_density_matrix_exact_zz() -> None:
    result = run(
        ExperimentConfig(
            num_qubits=2,
            state_type="BELL",
            sim_mode="density_matrix",
            shots=64,
            rng_seed=0,
            observables=["ZZ"],
            visualization_type="none",
        )
    )
    estimates = result.analysis.measurement_results.observables
    assert estimates is not None
    assert estimates["ZZ"].value == pytest.approx(1.0, abs=1e-9)
    assert estimates["ZZ"].stderr is None


def test_bell_qasm_zz_reuses_shots_xx_extra_circuit() -> None:
    result = run(
        ExperimentConfig(
            num_qubits=2,
            state_type="BELL",
            sim_mode="qasm",
            shots=2048,
            rng_seed=0,
            observables=["ZZ", "XX"],
            visualization_type="none",
        )
    )
    estimates = result.analysis.measurement_results.observables
    assert estimates is not None
    assert estimates["ZZ"].value == pytest.approx(1.0, abs=0.08)
    assert estimates["XX"].value == pytest.approx(1.0, abs=0.08)
    assert estimates["ZZ"].stderr is not None
    assert estimates["XX"].shots == 2048
