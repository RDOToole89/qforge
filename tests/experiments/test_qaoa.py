"""QAOA MaxCut cost is a linear combination of engine ⟨ZZ⟩ estimates, not a core metric."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from typer.testing import CliRunner

from qforge.cli import app, app_state
from qforge.core.math.observables import pauli_expectation_from_statevector
from qforge.engine.execution.context import AppContext
from qforge.engine.models.measurement import ObservableEstimate
from qforge.experiments.advanced.deep_dives.dd_qaoa import (
    DEFAULT_EDGES,
    DEFAULT_N_QUBITS,
    _build_qaoa_circuit,
    maxcut_from_estimates,
    maxcut_optimal,
    qaoa_experiment,
    zz_pauli,
)

runner = CliRunner()


def _circuit_cost(
    circuit: QuantumCircuit, n_qubits: int, edges: tuple[tuple[int, int], ...]
) -> float:
    stripped = circuit.copy()
    stripped.remove_final_measurements()
    psi = np.asarray(Statevector.from_instruction(stripped).data, dtype=complex)
    cost = 0.0
    for left, right in edges:
        cost += 0.5 * (
            1.0 - pauli_expectation_from_statevector(psi, zz_pauli(n_qubits, left, right))
        )
    return float(cost)


def test_zz_pauli_uses_physical_to_msb_left() -> None:
    assert zz_pauli(3, 0, 1) == "IZZ"
    assert zz_pauli(4, 0, 1) == "IIZZ"
    assert zz_pauli(4, 0, 3) == "ZIIZ"


def test_square_graph_maxcut_is_all_edges() -> None:
    assert maxcut_optimal(DEFAULT_N_QUBITS, DEFAULT_EDGES) == 4


def test_maxcut_from_estimates_half_minus_half_zz() -> None:
    estimates = {
        "IZZ": ObservableEstimate(pauli="IZZ", value=-1.0, stderr=0.0, shots=100),
    }
    cost, stderr = maxcut_from_estimates(estimates, 3, ((0, 1),))
    assert cost == pytest.approx(1.0)
    assert stderr == pytest.approx(0.0)


def test_one_edge_cut_on_physical_q0_q1() -> None:
    """|q0=1, q1=0⟩ cuts edge (0,1). Wrong MSB-left mapping would give ⟨ZZ⟩=+1."""
    psi = np.zeros(8, dtype=complex)
    psi[1] = 1.0  # Qiskit |001⟩: physical qubit 0 is 1
    zz = pauli_expectation_from_statevector(psi, zz_pauli(3, 0, 1))
    assert zz == pytest.approx(-1.0)
    assert 0.5 * (1.0 - zz) == pytest.approx(1.0)


def test_p0_uniform_expected_cut_is_half_the_edges(tmp_path: Path) -> None:
    result = qaoa_experiment.run(
        {
            "sim_mode": "statevector",
            "shots": 32,
            "rng_seed": 0,
            "visualization_type": "none",
            "custom_params": {"p": 0},
        },
        ctx=AppContext(base_results_dir=str(tmp_path)),
    )
    assert result.maxcut_cost == pytest.approx(2.0, abs=1e-8)
    assert result.maxcut_optimal == 4
    assert result.maxcut_approximation_ratio == pytest.approx(0.5, abs=1e-8)
    assert result.qaoa_p == 0
    assert result.maxcut_cost_stderr is None
    observables = result.analysis.measurement_results.observables
    assert observables is not None
    assert set(observables) == {"IIZZ", "IZZI", "ZZII", "ZIIZ"}


def test_statevector_cost_matches_closed_form(tmp_path: Path) -> None:
    p, gamma, beta = 1, 0.5, 0.5
    circuit = _build_qaoa_circuit(DEFAULT_N_QUBITS, DEFAULT_EDGES, p=p, gamma=gamma, beta=beta)
    expected = _circuit_cost(circuit, DEFAULT_N_QUBITS, DEFAULT_EDGES)
    result = qaoa_experiment.run(
        {
            "sim_mode": "statevector",
            "shots": 64,
            "rng_seed": 0,
            "visualization_type": "none",
            "custom_params": {"p": p, "gamma": gamma, "beta": beta},
        },
        ctx=AppContext(base_results_dir=str(tmp_path)),
    )
    assert result.maxcut_cost == pytest.approx(expected, abs=1e-8)
    assert result.maxcut_optimal == 4
    assert result.qaoa_p == 1


def test_cli_run_qaoa_prints_cost(tmp_path: Path) -> None:
    app_state.clear()
    try:
        result = runner.invoke(
            app,
            [
                "--results-dir",
                str(tmp_path),
                "run",
                "qaoa",
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
    assert "maxcut_cost" in result.stdout
    assert "maxcut_optimal" in result.stdout
    assert "IIZZ" in result.stdout
