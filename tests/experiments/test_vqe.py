"""VQE energy is a linear combination of engine Pauli estimates, not a core metric."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from qiskit.quantum_info import Statevector
from typer.testing import CliRunner

from qforge.cli import app, app_state
from qforge.core.math.observables import pauli_expectation_from_statevector
from qforge.engine.execution.context import AppContext
from qforge.engine.models.measurement import ObservableEstimate
from qforge.experiments.advanced.deep_dives.dd_vqe import (
    H2_FCI_0_735,
    H2_PARITY_STO3G_0_735,
    _build_vqe_ansatz,
    energy_from_estimates,
    fci_energy,
    h2_pauli_coeffs,
    vqe_experiment,
)

runner = CliRunner()


def _ansatz_energy(theta: float) -> float:
    circuit = _build_vqe_ansatz(n_qubits=2, depth=1, theta=theta)
    circuit.remove_final_measurements()
    psi = np.asarray(Statevector.from_instruction(circuit).data, dtype=complex)
    energy = H2_PARITY_STO3G_0_735["II"]
    for label, coeff in H2_PARITY_STO3G_0_735.items():
        if set(label) <= {"I"}:
            continue
        energy += coeff * pauli_expectation_from_statevector(psi, label)
    return float(energy)


def test_fci_matches_published_operator() -> None:
    assert fci_energy(H2_PARITY_STO3G_0_735) == pytest.approx(H2_FCI_0_735, abs=1e-8)


def test_other_bond_distance_requires_override() -> None:
    with pytest.raises(ValueError, match="0.735"):
        h2_pauli_coeffs(1.0)


def test_energy_from_estimates_identity_plus_weighted_paulis() -> None:
    estimates = {
        "ZZ": ObservableEstimate(pauli="ZZ", value=1.0, stderr=0.0, shots=100),
        "XX": ObservableEstimate(pauli="XX", value=-1.0, stderr=0.0, shots=100),
        "ZI": ObservableEstimate(pauli="ZI", value=0.0, stderr=0.0, shots=100),
        "IZ": ObservableEstimate(pauli="IZ", value=0.0, stderr=0.0, shots=100),
    }
    coeffs = {"II": -1.0, "ZZ": 0.5, "XX": 0.25, "ZI": 0.0, "IZ": 0.0}
    value, stderr = energy_from_estimates(estimates, coeffs)
    assert value == pytest.approx(-1.0 + 0.5 - 0.25)
    assert stderr == pytest.approx(0.0)


def test_statevector_energy_matches_closed_form(tmp_path: Path) -> None:
    theta = 0.5
    expected = _ansatz_energy(theta)
    result = vqe_experiment.run(
        {
            "sim_mode": "statevector",
            "shots": 64,
            "rng_seed": 0,
            "visualization_type": "none",
            "custom_params": {"theta": theta},
        },
        ctx=AppContext(base_results_dir=str(tmp_path)),
    )
    assert result.h2_energy == pytest.approx(expected, abs=1e-8)
    assert result.h2_energy_stderr is None
    assert result.h2_fci == pytest.approx(H2_FCI_0_735, abs=1e-8)
    assert result.h2_bond_distance == pytest.approx(0.735)
    observables = result.analysis.measurement_results.observables
    assert observables is not None
    assert set(observables) == {"ZI", "IZ", "ZZ", "XX"}


def test_cli_run_vqe_prints_energy(tmp_path: Path) -> None:
    app_state.clear()
    try:
        result = runner.invoke(
            app,
            [
                "--results-dir",
                str(tmp_path),
                "run",
                "vqe",
                "-s",
                "sim_mode=statevector",
                "-s",
                "shots=32",
                "-s",
                "rng_seed=0",
                "-s",
                "visualization_type=none",
            ],
            catch_exceptions=False,
        )
    finally:
        app_state.clear()
    assert result.exit_code == 0, result.stdout
    assert "h2_energy" in result.stdout
    assert "h2_fci" in result.stdout
    assert "ZI" in result.stdout
    assert "XX" in result.stdout
