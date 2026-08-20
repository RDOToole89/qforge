"""Exact-value verification tests for quantum math in the engine layer.

Covers ``src/qforge/engine/fidelity.py`` and ``src/qforge/engine/bloch_math.py``.

Every assertion below is checked against the closed-form definition of the
quantity, not against whatever the implementation happens to return. The goal
is to lock in *correct* values so a future regression (including an endianness
flip) is caught.

Conventions verified here:
- State fidelity (pure/pure):    F = |<psi|phi>|^2
- State fidelity (pure target):  F = <psi|rho|psi>
- Counts ("classical") fidelity: F = (sum_x sqrt(p_ideal(x) p_obs(x)))^2  (Bhattacharyya)
- Bloch vector:                  r = (Tr(rho X), Tr(rho Y), Tr(rho Z))
- Purity:                        Tr(rho^2)
- partial_trace_single_qubit qubit_index ordering: np.kron / big-endian,
  i.e. qubit_index 0 is the *leftmost* tensor factor (MSB of the basis index).
"""

from __future__ import annotations

import numpy as np
import pytest

from qforge.core.state_preparation import create_state_instance
from qforge.engine.bloch_math import (
    compute_bloch_data,
    counts_to_diagonal_density_matrix,
    density_matrix_to_bloch,
    json_density_matrix_to_numpy,
    mutual_information_from_rho,
    partial_trace_single_qubit,
    partial_trace_two_qubit,
    statevector_to_density_matrix,
    two_qubit_correlators,
)
from qforge.engine.fidelity import (
    _compute_fidelity_density_matrix,
    _compute_fidelity_from_counts,
    _compute_fidelity_statevector,
    extract_simulation_data,
)
from tests._qhelpers import density_matrix_from_statevector as _dm

# ── single-qubit kets / density matrices ────────────────────────────────────
KET0 = np.array([1, 0], dtype=complex)
KET1 = np.array([0, 1], dtype=complex)
KETP = np.array([1, 1], dtype=complex) / np.sqrt(2)  # |+>
KETM = np.array([1, -1], dtype=complex) / np.sqrt(2)  # |->
KETi = np.array([1, 1j], dtype=complex) / np.sqrt(2)  # |i> = (|0>+i|1>)/sqrt2


class _DataObj:
    """Minimal stand-in for a Qiskit Statevector/DensityMatrix result object."""

    def __init__(self, data: np.ndarray) -> None:
        self.data = data


# ════════════════════════════════════════════════════════════════════════════
# fidelity.py  —  pure statevector fidelity  F = |<ideal|sv>|^2
# ════════════════════════════════════════════════════════════════════════════


def test_sv_fidelity_identical_is_one():
    # GHZ(1) ideal == |0>.  F(|0>,|0>) = 1
    assert _compute_fidelity_statevector(KET0, "GHZ", 1) == pytest.approx(1.0)


def test_sv_fidelity_orthogonal_is_zero():
    # F(|0>,|1>) = 0
    assert _compute_fidelity_statevector(KET1, "GHZ", 1) == pytest.approx(0.0)


def test_sv_fidelity_zero_vs_plus_is_half():
    # F(|0>,|+>) = |<0|+>|^2 = 1/2
    assert _compute_fidelity_statevector(KETP, "GHZ", 1) == pytest.approx(0.5)


def test_sv_fidelity_ghz_vs_ghz_is_one():
    ideal = create_state_instance("GHZ", 3).get_theoretical_state_vector()
    assert _compute_fidelity_statevector(ideal, "GHZ", 3) == pytest.approx(1.0)


def test_sv_fidelity_ghz_orthogonal_is_zero():
    # |GHZ-> = (|000> - |111>)/sqrt2 is orthogonal to |GHZ+>
    ghz_minus = np.zeros(8, dtype=complex)
    ghz_minus[0] = 1 / np.sqrt(2)
    ghz_minus[-1] = -1 / np.sqrt(2)
    assert _compute_fidelity_statevector(ghz_minus, "GHZ", 3) == pytest.approx(0.0)


def test_sv_fidelity_bad_state_type_returns_none():
    assert _compute_fidelity_statevector(KET0, "NOT_A_STATE", 1) is None


# ════════════════════════════════════════════════════════════════════════════
# fidelity.py  —  density-matrix fidelity  F = <ideal|rho|ideal>
# ════════════════════════════════════════════════════════════════════════════


def test_dm_fidelity_pure_match_is_one():
    assert _compute_fidelity_density_matrix(_dm(KET0), "GHZ", 1) == pytest.approx(1.0)


def test_dm_fidelity_pure_orthogonal_is_zero():
    assert _compute_fidelity_density_matrix(_dm(KET1), "GHZ", 1) == pytest.approx(0.0)


def test_dm_fidelity_vs_5050_mixture_is_half():
    # rho = 1/2 |0><0| + 1/2 |1><1| = I/2.  <0|rho|0> = 1/2
    rho = 0.5 * _dm(KET0) + 0.5 * _dm(KET1)
    assert _compute_fidelity_density_matrix(rho, "GHZ", 1) == pytest.approx(0.5)


def test_dm_fidelity_ghz_vs_5050_mixture_with_orthogonal():
    # rho = 1/2 |GHZ+><GHZ+| + 1/2 |GHZ-><GHZ-|.  F = <GHZ+|rho|GHZ+> = 1/2
    ideal = create_state_instance("GHZ", 2).get_theoretical_state_vector()
    ghz_minus = np.array([1, 0, 0, -1], dtype=complex) / np.sqrt(2)
    rho = 0.5 * _dm(ideal) + 0.5 * _dm(ghz_minus)
    assert _compute_fidelity_density_matrix(rho, "GHZ", 2) == pytest.approx(0.5)


def test_dm_fidelity_bad_state_type_returns_none():
    assert _compute_fidelity_density_matrix(_dm(KET0), "NOPE", 1) is None


# ════════════════════════════════════════════════════════════════════════════
# fidelity.py  —  counts fidelity  F = (sum sqrt(p_ideal p_obs))^2
# ════════════════════════════════════════════════════════════════════════════


def test_counts_fidelity_perfect_single_qubit():
    # ideal GHZ(1) = |0>; all counts in '0'
    assert _compute_fidelity_from_counts({"0": 1000}, "GHZ", 1) == pytest.approx(1.0)


def test_counts_fidelity_orthogonal_single_qubit():
    assert _compute_fidelity_from_counts({"1": 1000}, "GHZ", 1) == pytest.approx(0.0)


def test_counts_fidelity_5050_against_pure_is_half():
    # ideal probs [1,0]; obs [0.5,0.5]; bc = sqrt(0.5); bc^2 = 0.5
    f = _compute_fidelity_from_counts({"0": 500, "1": 500}, "GHZ", 1)
    assert f == pytest.approx(0.5)


def test_counts_fidelity_perfect_ghz2():
    # ideal probs index0=index3=0.5; matching 50/50 counts -> F=1
    f = _compute_fidelity_from_counts({"00": 500, "11": 500}, "GHZ", 2)
    assert f == pytest.approx(1.0)


def test_counts_fidelity_ghz2_partial_overlap():
    # ideal probs {0:0.5, 3:0.5}; obs all in '00' -> bc=sqrt(0.5*1)=sqrt(0.5); F=0.5
    f = _compute_fidelity_from_counts({"00": 1000}, "GHZ", 2)
    assert f == pytest.approx(0.5)


def test_counts_fidelity_zero_shots_returns_none():
    assert _compute_fidelity_from_counts({"0": 0, "1": 0}, "GHZ", 1) is None


def test_counts_fidelity_out_of_range_bitstring_ignored():
    # '11' -> idx 3, out of range for a 1-qubit (len-2) prob vector; skipped.
    # observed stays all-zero -> bc = 0 -> F = 0 (does not raise).
    assert _compute_fidelity_from_counts({"11": 5}, "GHZ", 1) == pytest.approx(0.0)


def test_counts_fidelity_bad_state_type_returns_none():
    assert _compute_fidelity_from_counts({"0": 10}, "NOPE", 1) is None


# ════════════════════════════════════════════════════════════════════════════
# fidelity.py  —  extract_simulation_data dispatch
# ════════════════════════════════════════════════════════════════════════════


def test_extract_qasm_returns_all_none():
    assert extract_simulation_data({}, "qasm", "GHZ", 1) == (None, None, None)


def test_extract_hardware_with_counts():
    dm, sv, fid = extract_simulation_data({"counts": {"0": 1000}}, "hardware", "GHZ", 1)
    assert dm is None and sv is None
    assert fid == pytest.approx(1.0)


def test_extract_hardware_without_counts():
    assert extract_simulation_data({}, "hardware", "GHZ", 1) == (None, None, None)


def test_extract_statevector_serializes_and_scores():
    raw = {"statevector": _DataObj(KET0.copy())}
    dm, sv, fid = extract_simulation_data(raw, "statevector", "GHZ", 1)
    assert dm is None
    assert sv == [[1.0, 0.0], [0.0, 0.0]]
    assert fid == pytest.approx(1.0)


def test_extract_statevector_missing_object():
    assert extract_simulation_data({"statevector": None}, "statevector", "GHZ", 1) == (
        None,
        None,
        None,
    )


def test_extract_density_matrix_serializes_and_scores():
    rho = _dm(KET0)
    raw = {"density_matrix": _DataObj(rho)}
    dm, sv, fid = extract_simulation_data(raw, "density_matrix", "GHZ", 1)
    assert sv is None
    assert dm == [[[1.0, 0.0], [0.0, 0.0]], [[0.0, 0.0], [0.0, 0.0]]]
    assert fid == pytest.approx(1.0)


def test_extract_density_matrix_missing_object():
    assert extract_simulation_data({"density_matrix": None}, "density_matrix", "GHZ", 1) == (
        None,
        None,
        None,
    )


def test_extract_statevector_exception_path_returns_none():
    # object() has no .data -> AttributeError is caught, returns all-None.
    assert extract_simulation_data({"statevector": object()}, "statevector", "GHZ", 1) == (
        None,
        None,
        None,
    )


def test_extract_unknown_mode_returns_none():
    assert extract_simulation_data({}, "totally_unknown", "GHZ", 1) == (None, None, None)


# ════════════════════════════════════════════════════════════════════════════
# bloch_math.py  —  density_matrix_to_bloch  r = (Tr rho X, Tr rho Y, Tr rho Z)
# ════════════════════════════════════════════════════════════════════════════


@pytest.mark.parametrize(
    ("psi", "expected"),
    [
        (KET0, (0.0, 0.0, 1.0)),
        (KET1, (0.0, 0.0, -1.0)),
        (KETP, (1.0, 0.0, 0.0)),
        (KETM, (-1.0, 0.0, 0.0)),
        (KETi, (0.0, 1.0, 0.0)),
    ],
)
def test_bloch_vectors_pure_states(psi, expected):
    bv = density_matrix_to_bloch(_dm(psi))
    assert (bv["rx"], bv["ry"], bv["rz"]) == pytest.approx(expected)


def test_bloch_maximally_mixed_is_origin():
    rho = np.eye(2, dtype=complex) / 2
    bv = density_matrix_to_bloch(rho)
    assert (bv["rx"], bv["ry"], bv["rz"]) == pytest.approx((0.0, 0.0, 0.0))


def test_purity_pure_vs_mixed():
    assert np.real(np.trace(_dm(KET0) @ _dm(KET0))) == pytest.approx(1.0)
    rho_mixed = np.eye(2, dtype=complex) / 2
    assert np.real(np.trace(rho_mixed @ rho_mixed)) == pytest.approx(0.5)


# ════════════════════════════════════════════════════════════════════════════
# bloch_math.py  —  partial_trace_single_qubit (ordering + reductions)
# ════════════════════════════════════════════════════════════════════════════


def test_partial_trace_endianness_product_0_tensor_1():
    # |0> (x) |1>: kron/big-endian -> qubit_index 0 is the leftmost factor.
    psi = np.kron(KET0, KET1)
    rho = _dm(psi)
    bv0 = density_matrix_to_bloch(partial_trace_single_qubit(rho, 0, 2))
    bv1 = density_matrix_to_bloch(partial_trace_single_qubit(rho, 1, 2))
    assert (bv0["rx"], bv0["ry"], bv0["rz"]) == pytest.approx((0.0, 0.0, 1.0))
    assert (bv1["rx"], bv1["ry"], bv1["rz"]) == pytest.approx((0.0, 0.0, -1.0))


def test_partial_trace_endianness_product_1_tensor_0():
    # Swapped order must give swapped Bloch vectors (catches endianness flips).
    psi = np.kron(KET1, KET0)
    rho = _dm(psi)
    bv0 = density_matrix_to_bloch(partial_trace_single_qubit(rho, 0, 2))
    bv1 = density_matrix_to_bloch(partial_trace_single_qubit(rho, 1, 2))
    assert (bv0["rx"], bv0["ry"], bv0["rz"]) == pytest.approx((0.0, 0.0, -1.0))
    assert (bv1["rx"], bv1["ry"], bv1["rz"]) == pytest.approx((0.0, 0.0, 1.0))


def test_partial_trace_product_0_tensor_plus():
    # |0> (x) |+>: qubit0 -> (0,0,1), qubit1 -> (1,0,0)
    psi = np.kron(KET0, KETP)
    rho = _dm(psi)
    bv0 = density_matrix_to_bloch(partial_trace_single_qubit(rho, 0, 2))
    bv1 = density_matrix_to_bloch(partial_trace_single_qubit(rho, 1, 2))
    assert (bv0["rx"], bv0["ry"], bv0["rz"]) == pytest.approx((0.0, 0.0, 1.0))
    assert (bv1["rx"], bv1["ry"], bv1["rz"]) == pytest.approx((1.0, 0.0, 0.0))


def test_partial_trace_bell_each_qubit_maximally_mixed():
    ideal = create_state_instance("BELL", 2).get_theoretical_state_vector()
    rho = _dm(ideal)
    for q in (0, 1):
        rho_q = partial_trace_single_qubit(rho, q, 2)
        bv = density_matrix_to_bloch(rho_q)
        assert (bv["rx"], bv["ry"], bv["rz"]) == pytest.approx((0.0, 0.0, 0.0))
        assert np.real(np.trace(rho_q @ rho_q)) == pytest.approx(0.5)


@pytest.mark.parametrize("n", [2, 3])
def test_partial_trace_ghz_each_qubit_maximally_mixed(n):
    ideal = create_state_instance("GHZ", n).get_theoretical_state_vector()
    rho = _dm(ideal)
    for q in range(n):
        rho_q = partial_trace_single_qubit(rho, q, n)
        bv = density_matrix_to_bloch(rho_q)
        assert (bv["rx"], bv["ry"], bv["rz"]) == pytest.approx((0.0, 0.0, 0.0))
        assert np.real(np.trace(rho_q @ rho_q)) == pytest.approx(0.5)


def test_partial_trace_single_wrong_shape_raises():
    with pytest.raises(ValueError):
        partial_trace_single_qubit(np.eye(2, dtype=complex), 0, 2)


# ════════════════════════════════════════════════════════════════════════════
# bloch_math.py  —  partial_trace_two_qubit / correlators / mutual information
# ════════════════════════════════════════════════════════════════════════════


def test_two_qubit_correlators_bell_phi_plus():
    ideal = create_state_instance("BELL", 2).get_theoretical_state_vector()
    rho = _dm(ideal)
    corr = two_qubit_correlators(rho)
    assert corr["zz"] == pytest.approx(1.0)
    assert corr["xx"] == pytest.approx(1.0)
    assert corr["yy"] == pytest.approx(-1.0)
    assert corr["zi"] == pytest.approx(0.0)
    assert corr["iz"] == pytest.approx(0.0)


def test_mutual_information_bell_is_two_bits():
    ideal = create_state_instance("BELL", 2).get_theoretical_state_vector()
    assert mutual_information_from_rho(_dm(ideal)) == pytest.approx(2.0)


def test_mutual_information_product_state_is_zero():
    psi = np.kron(KETP, KETP)
    assert mutual_information_from_rho(_dm(psi)) == pytest.approx(0.0, abs=1e-9)


def test_partial_trace_two_qubit_ghz3_classical_correlation():
    # Reduced 2-qubit state of GHZ(3) is 1/2(|00><00| + |11><11|): MI = 1 bit.
    ideal = create_state_instance("GHZ", 3).get_theoretical_state_vector()
    rho = _dm(ideal)
    rho_2q = partial_trace_two_qubit(rho, 0, 1, 3)
    assert rho_2q.shape == (4, 4)
    assert mutual_information_from_rho(rho_2q) == pytest.approx(1.0)


def test_partial_trace_two_wrong_shape_raises():
    with pytest.raises(ValueError):
        partial_trace_two_qubit(np.eye(4, dtype=complex), 0, 1, 3)


# ════════════════════════════════════════════════════════════════════════════
# bloch_math.py  —  density matrix construction helpers
# ════════════════════════════════════════════════════════════════════════════


def test_counts_to_diagonal_density_matrix_basic():
    rho = counts_to_diagonal_density_matrix({"00": 750, "11": 250}, 2)
    assert rho[0, 0] == pytest.approx(0.75)
    assert rho[3, 3] == pytest.approx(0.25)
    assert np.real(np.trace(rho)) == pytest.approx(1.0)


def test_counts_to_diagonal_handles_spaces_and_bad_length():
    # space stripped -> "01"; bad-length "111" skipped as an entry BUT its
    # count still contributes to the normalization total (10 + 5 = 15).
    rho = counts_to_diagonal_density_matrix({"0 1": 10, "111": 5}, 2)
    assert rho[1, 1] == pytest.approx(10 / 15)
    assert np.real(np.trace(rho)) == pytest.approx(10 / 15)


def test_counts_to_diagonal_zero_total_is_zero_matrix():
    rho = counts_to_diagonal_density_matrix({}, 2)
    assert np.allclose(rho, 0)


def test_statevector_to_density_matrix_roundtrip():
    rho = statevector_to_density_matrix([[1.0, 0.0], [0.0, 0.0]])
    assert np.allclose(rho, _dm(KET0))


def test_json_density_matrix_to_numpy_roundtrip():
    rho = json_density_matrix_to_numpy([[[0.5, 0.0], [0.0, -0.5]], [[0.0, 0.5], [0.5, 0.0]]])
    assert rho[0, 1] == complex(0.0, -0.5)
    assert rho[1, 0] == complex(0.0, 0.5)


# ════════════════════════════════════════════════════════════════════════════
# bloch_math.py  —  compute_bloch_data orchestration
# ════════════════════════════════════════════════════════════════════════════


def _bell_sv_json() -> list[list[float]]:
    a = 1 / np.sqrt(2)
    return [[a, 0.0], [0.0, 0.0], [0.0, 0.0], [a, 0.0]]


def test_compute_bloch_data_statevector_source():
    data = {
        "experiment_parameters": {
            "num_qubits": 2,
            "state_type": "BELL",
            "noise_enabled": False,
        },
        "measurement_results": {"statevector": _bell_sv_json(), "fidelity": 0.99},
        "experiment_metadata": {"experiment_id": "exp-1"},
    }
    out = compute_bloch_data(data)
    assert out["source_mode"] == "statevector"
    assert out["num_qubits"] == 2
    assert out["experiment_id"] == "exp-1"
    assert out["noise_type"] is None
    for q in out["qubits"]:
        bv = q["bloch_vector"]
        assert (bv["rx"], bv["ry"], bv["rz"]) == pytest.approx((0.0, 0.0, 0.0))
        assert q["purity"] == pytest.approx(0.5)
    assert out["mi_matrix"][0][1] == pytest.approx(2.0)


def test_compute_bloch_data_density_matrix_source_and_metrics():
    rho = _dm(np.array(_bell_sv_json())[:, 0])  # real Bell vector
    dm_json = [[[float(c.real), float(c.imag)] for c in row] for row in rho]
    data = {
        "analysis": {
            "experiment_parameters": {
                "num_qubits": 2,
                "state_type": "BELL",
                "noise_enabled": True,
                "noise_type": "depolarizing",
                "error_rate": 0.1,
            },
            "measurement_results": {"density_matrix": dm_json, "fidelity": 0.8},
            "experiment_metadata": {"experiment_id": "exp-2"},
        },
        "metrics_bundle": {"metrics": {"asymmetry_index": {"value": 0.42, "ci95": [0.3, 0.5]}}},
    }
    out = compute_bloch_data(data)
    assert out["source_mode"] == "density_matrix"
    assert out["noise_type"] == "depolarizing"
    assert out["error_rate"] == 0.1
    assert out["fidelity"] == 0.8
    assert out["metrics"]["asymmetry_index"]["value"] == 0.42


def test_compute_bloch_data_counts_source():
    data = {
        "experiment_parameters": {"num_qubits": 1, "state_type": "GHZ"},
        "measurement_results": {"raw_counts": {"0": 500, "1": 500}},
        "experiment_metadata": {},
    }
    out = compute_bloch_data(data)
    assert out["source_mode"] == "diagonal_estimate"
    bv = out["qubits"][0]["bloch_vector"]
    # Diagonal (Z-basis only) estimate of a 50/50 mix -> origin.
    assert (bv["rx"], bv["ry"], bv["rz"]) == pytest.approx((0.0, 0.0, 0.0))


def test_compute_bloch_data_invalid_qubit_count():
    with pytest.raises(ValueError):
        compute_bloch_data({"experiment_parameters": {"num_qubits": 0}})
    with pytest.raises(ValueError):
        compute_bloch_data({"experiment_parameters": {"num_qubits": 9}})


def test_compute_bloch_data_no_measurement_data():
    data = {
        "experiment_parameters": {"num_qubits": 2},
        "measurement_results": {},
        "experiment_metadata": {},
    }
    with pytest.raises(ValueError):
        compute_bloch_data(data)
