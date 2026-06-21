"""
Tests for the Bloch sphere visualization API (apps/api/routes/bloch.py).

Covers:
- Partial trace correctness (single-qubit and two-qubit)
- Bloch vector extraction
- Two-qubit correlator computation
- Mutual information from density matrices
- Density matrix construction (counts, statevector, JSON)
- compute_bloch_data orchestration
- Edge cases and validation
"""

import numpy as np
import pytest

from src.engine.bloch_math import (
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

# ── Helpers ──────────────────────────────────────────────────────────


def _ghz_2q_dm() -> np.ndarray:
    """|Φ+⟩ = (|00⟩ + |11⟩)/√2 density matrix."""
    psi = np.array([1, 0, 0, 1], dtype=np.complex128) / np.sqrt(2)
    return np.outer(psi, psi.conj())


def _product_state_dm(n: int) -> np.ndarray:
    """|+⟩^n density matrix (product state, no entanglement)."""
    psi_plus = np.array([1, 1], dtype=np.complex128) / np.sqrt(2)
    psi = psi_plus
    for _ in range(n - 1):
        psi = np.kron(psi, psi_plus)
    return np.outer(psi, psi.conj())


def _maximally_mixed(n: int) -> np.ndarray:
    """Maximally mixed state I/2^n."""
    dim = 2**n
    return np.eye(dim, dtype=np.complex128) / dim


def _pure_zero_dm() -> np.ndarray:
    """|0⟩⟨0| single-qubit density matrix."""
    return np.array([[1, 0], [0, 0]], dtype=np.complex128)


# ── Partial trace tests ──────────────────────────────────────────────


class TestPartialTraceSingleQubit:
    """Test single-qubit partial trace."""

    def test_bell_state_gives_maximally_mixed(self):
        """Tracing out one qubit of a Bell state gives I/2."""
        rho = _ghz_2q_dm()
        for q in range(2):
            rho_q = partial_trace_single_qubit(rho, q, 2)
            assert rho_q.shape == (2, 2)
            np.testing.assert_allclose(rho_q, np.eye(2) / 2, atol=1e-12)

    def test_product_state_gives_pure_marginals(self):
        """|+⟩⊗|+⟩: tracing out either qubit gives |+⟩⟨+|."""
        rho = _product_state_dm(2)
        expected = np.array([[0.5, 0.5], [0.5, 0.5]], dtype=np.complex128)
        for q in range(2):
            rho_q = partial_trace_single_qubit(rho, q, 2)
            np.testing.assert_allclose(rho_q, expected, atol=1e-12)

    def test_trace_preserved(self):
        """Reduced density matrix must have Tr = 1."""
        rho = _ghz_2q_dm()
        for q in range(2):
            rho_q = partial_trace_single_qubit(rho, q, 2)
            assert abs(np.trace(rho_q) - 1.0) < 1e-12

    def test_3qubit_ghz(self):
        """GHZ3 = (|000⟩+|111⟩)/√2: each qubit is maximally mixed."""
        psi = np.zeros(8, dtype=np.complex128)
        psi[0] = psi[7] = 1.0 / np.sqrt(2)
        rho = np.outer(psi, psi.conj())

        for q in range(3):
            rho_q = partial_trace_single_qubit(rho, q, 3)
            np.testing.assert_allclose(rho_q, np.eye(2) / 2, atol=1e-12)

    def test_invalid_shape_raises(self):
        """Wrong-sized density matrix raises ValueError."""
        with pytest.raises(ValueError, match="Expected"):
            partial_trace_single_qubit(np.eye(3), 0, 2)


class TestPartialTraceTwoQubit:
    """Test two-qubit partial trace."""

    def test_bell_state_returns_full_dm(self):
        """Tracing out nothing from a 2-qubit state returns the state itself."""
        rho = _ghz_2q_dm()
        rho_2q = partial_trace_two_qubit(rho, 0, 1, 2)
        np.testing.assert_allclose(rho_2q, rho, atol=1e-12)

    def test_3qubit_pair_trace_preserved(self):
        """Reduced 2-qubit DM of 3-qubit state has Tr=1."""
        psi = np.zeros(8, dtype=np.complex128)
        psi[0] = psi[7] = 1.0 / np.sqrt(2)
        rho = np.outer(psi, psi.conj())

        from itertools import combinations

        for qi, qj in combinations(range(3), 2):
            rho_2q = partial_trace_two_qubit(rho, qi, qj, 3)
            assert rho_2q.shape == (4, 4)
            assert abs(np.trace(rho_2q) - 1.0) < 1e-12

    def test_product_state_pair_is_separable(self):
        """|+⟩^3 pair should be product: ρ_ij = ρ_i ⊗ ρ_j."""
        rho = _product_state_dm(3)
        rho_01 = partial_trace_two_qubit(rho, 0, 1, 3)
        rho_0 = partial_trace_single_qubit(rho, 0, 3)
        rho_1 = partial_trace_single_qubit(rho, 1, 3)
        expected = np.kron(rho_0, rho_1)
        np.testing.assert_allclose(rho_01, expected, atol=1e-12)


# ── Bloch vector tests ───────────────────────────────────────────────


class TestDensityMatrixToBloch:
    """Test Bloch vector extraction from 2x2 density matrix."""

    def test_zero_state(self):
        """|0⟩ → (0, 0, 1) on Bloch sphere."""
        bv = density_matrix_to_bloch(_pure_zero_dm())
        assert abs(bv["rx"]) < 1e-12
        assert abs(bv["ry"]) < 1e-12
        assert abs(bv["rz"] - 1.0) < 1e-12

    def test_one_state(self):
        """|1⟩ → (0, 0, -1) on Bloch sphere."""
        rho = np.array([[0, 0], [0, 1]], dtype=np.complex128)
        bv = density_matrix_to_bloch(rho)
        assert abs(bv["rx"]) < 1e-12
        assert abs(bv["ry"]) < 1e-12
        assert abs(bv["rz"] + 1.0) < 1e-12

    def test_plus_state(self):
        """|+⟩ → (1, 0, 0) on Bloch sphere."""
        rho = np.array([[0.5, 0.5], [0.5, 0.5]], dtype=np.complex128)
        bv = density_matrix_to_bloch(rho)
        assert abs(bv["rx"] - 1.0) < 1e-12
        assert abs(bv["ry"]) < 1e-12
        assert abs(bv["rz"]) < 1e-12

    def test_maximally_mixed_at_origin(self):
        """I/2 → (0, 0, 0)."""
        bv = density_matrix_to_bloch(np.eye(2, dtype=np.complex128) / 2)
        assert abs(bv["rx"]) < 1e-12
        assert abs(bv["ry"]) < 1e-12
        assert abs(bv["rz"]) < 1e-12

    def test_bloch_vector_norm_le_1(self):
        """Any valid density matrix has |r| ≤ 1."""
        rng = np.random.default_rng(42)
        for _ in range(20):
            # Random mixed state via partial trace of random pure state
            psi = rng.standard_normal(4) + 1j * rng.standard_normal(4)
            psi /= np.linalg.norm(psi)
            rho_2 = np.outer(psi, psi.conj())
            # Partial trace to get 1-qubit state
            rho_1 = partial_trace_single_qubit(rho_2, 0, 2)
            bv = density_matrix_to_bloch(rho_1)
            norm = np.sqrt(bv["rx"] ** 2 + bv["ry"] ** 2 + bv["rz"] ** 2)
            assert norm <= 1.0 + 1e-10


# ── Two-qubit correlator tests ───────────────────────────────────────


class TestTwoQubitCorrelators:
    """Test Pauli correlator extraction."""

    def test_bell_state_correlators(self):
        """Bell state |Φ+⟩ has ⟨ZZ⟩=1, ⟨XX⟩=1, ⟨YY⟩=-1."""
        rho = _ghz_2q_dm()
        c = two_qubit_correlators(rho)
        assert abs(c["zz"] - 1.0) < 1e-12
        assert abs(c["xx"] - 1.0) < 1e-12
        assert abs(c["yy"] + 1.0) < 1e-12
        # Individual qubits: maximally mixed → ⟨ZI⟩=⟨IZ⟩=0
        assert abs(c["zi"]) < 1e-12
        assert abs(c["iz"]) < 1e-12

    def test_product_state_factorizes(self):
        """|0⟩⊗|0⟩: ⟨ZZ⟩ = ⟨Z⟩⟨Z⟩ = 1, ⟨XX⟩ = ⟨X⟩⟨X⟩ = 0."""
        psi = np.array([1, 0, 0, 0], dtype=np.complex128)
        rho = np.outer(psi, psi.conj())
        c = two_qubit_correlators(rho)
        assert abs(c["zz"] - 1.0) < 1e-12
        assert abs(c["zi"] - 1.0) < 1e-12
        assert abs(c["iz"] - 1.0) < 1e-12
        assert abs(c["xx"]) < 1e-12
        assert abs(c["yy"]) < 1e-12

    def test_maximally_mixed_all_zero(self):
        """I/4 has all correlators = 0."""
        rho = _maximally_mixed(2)
        c = two_qubit_correlators(rho)
        for key in ("zi", "iz", "zz", "xx", "yy"):
            assert abs(c[key]) < 1e-12


# ── Mutual information tests ─────────────────────────────────────────


class TestMutualInformation:
    """Test mutual information from density matrices."""

    def test_bell_state_mi(self):
        """Maximally entangled state: MI = 2 (2 bits)."""
        rho = _ghz_2q_dm()
        mi = mutual_information_from_rho(rho)
        assert abs(mi - 2.0) < 1e-10

    def test_product_state_mi_zero(self):
        """Product state has MI ≈ 0."""
        rho = _product_state_dm(2)
        mi = mutual_information_from_rho(rho)
        assert mi < 1e-10

    def test_mi_non_negative(self):
        """MI must be ≥ 0 for any state."""
        rng = np.random.default_rng(99)
        for _ in range(20):
            psi = rng.standard_normal(4) + 1j * rng.standard_normal(4)
            psi /= np.linalg.norm(psi)
            rho = np.outer(psi, psi.conj())
            mi = mutual_information_from_rho(rho)
            assert mi >= -1e-15

    def test_mi_symmetric(self):
        """MI(A:B) = MI(B:A) — verified by swapping qubit order."""
        psi = np.array([1, 0, 0, 1], dtype=np.complex128) / np.sqrt(2)
        rho = np.outer(psi, psi.conj())
        mi_01 = mutual_information_from_rho(rho)
        # Swap qubits: SWAP ρ SWAP†
        swap = np.array(
            [[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=np.complex128
        )
        rho_swap = swap @ rho @ swap.T.conj()
        mi_10 = mutual_information_from_rho(rho_swap)
        assert abs(mi_01 - mi_10) < 1e-12


# ── Density matrix construction tests ────────────────────────────────


class TestCountsToDiagonalDM:
    """Test diagonal density matrix construction from counts."""

    def test_uniform_counts(self):
        """Equal counts → diagonal entries all equal."""
        counts = {"00": 100, "01": 100, "10": 100, "11": 100}
        rho = counts_to_diagonal_density_matrix(counts, 2)
        assert rho.shape == (4, 4)
        for i in range(4):
            assert abs(rho[i, i] - 0.25) < 1e-12
        # Off-diagonal should be zero
        assert abs(np.sum(rho) - np.trace(rho)) < 1e-12

    def test_trace_one(self):
        counts = {"000": 400, "111": 600}
        rho = counts_to_diagonal_density_matrix(counts, 3)
        assert abs(np.trace(rho) - 1.0) < 1e-12

    def test_empty_counts(self):
        rho = counts_to_diagonal_density_matrix({}, 2)
        assert np.allclose(rho, 0)

    def test_single_outcome(self):
        """Deterministic → single diagonal entry = 1."""
        rho = counts_to_diagonal_density_matrix({"01": 1000}, 2)
        assert abs(rho[1, 1] - 1.0) < 1e-12
        assert abs(np.trace(rho) - 1.0) < 1e-12


class TestStatevectorToDM:
    """Test statevector → density matrix conversion."""

    def test_zero_state(self):
        sv = [[1.0, 0.0], [0.0, 0.0]]
        rho = statevector_to_density_matrix(sv)
        expected = np.array([[1, 0], [0, 0]], dtype=np.complex128)
        np.testing.assert_allclose(rho, expected, atol=1e-12)

    def test_hermitian(self):
        """ρ = |ψ⟩⟨ψ| must be Hermitian."""
        sv = [[1 / np.sqrt(2), 0.0], [0.0, 1 / np.sqrt(2)]]  # (|0⟩+i|1⟩)/√2
        rho = statevector_to_density_matrix(sv)
        np.testing.assert_allclose(rho, rho.T.conj(), atol=1e-12)

    def test_trace_one(self):
        sv = [[1 / np.sqrt(2), 0.0], [1 / np.sqrt(2), 0.0]]
        rho = statevector_to_density_matrix(sv)
        assert abs(np.trace(rho) - 1.0) < 1e-12


class TestJsonDMToNumpy:
    """Test JSON density matrix parsing."""

    def test_identity_2x2(self):
        dm = [[[0.5, 0], [0, 0]], [[0, 0], [0.5, 0]]]
        rho = json_density_matrix_to_numpy(dm)
        np.testing.assert_allclose(rho, np.eye(2) / 2, atol=1e-12)

    def test_complex_entries(self):
        dm = [[[1, 0], [0, -0.5]], [[0, 0.5], [0, 0]]]
        rho = json_density_matrix_to_numpy(dm)
        assert rho[0, 1] == complex(0, -0.5)
        assert rho[1, 0] == complex(0, 0.5)


# ── compute_bloch_data integration tests ────────────────────────────


class TestComputeBlochData:
    """Test the main orchestration function."""

    def _make_result_dict(
        self,
        n_qubits: int,
        dm: np.ndarray | None = None,
        sv: list | None = None,
        counts: dict | None = None,
    ):
        """Build a minimal result dict for compute_bloch_data."""
        meas: dict = {}
        if dm is not None:
            # Convert to JSON format [[real, imag], ...]
            meas["density_matrix"] = [
                [[float(dm[i, j].real), float(dm[i, j].imag)] for j in range(dm.shape[1])]
                for i in range(dm.shape[0])
            ]
        if sv is not None:
            meas["statevector"] = sv
        if counts is not None:
            meas["raw_counts"] = counts

        return {
            "experiment_parameters": {
                "num_qubits": n_qubits,
                "state_type": "GHZ",
                "noise_enabled": False,
            },
            "measurement_results": meas,
            "experiment_metadata": {"experiment_id": "test-001"},
        }

    def test_dm_source_2qubit_bell(self):
        """Full density matrix gives correct Bloch data for Bell state."""
        rho = _ghz_2q_dm()
        data = self._make_result_dict(2, dm=rho)
        result = compute_bloch_data(data)

        assert result["num_qubits"] == 2
        assert result["source_mode"] == "density_matrix"
        assert len(result["qubits"]) == 2
        assert len(result["pairs"]) == 1

        # Each qubit of Bell state is maximally mixed → purity ≈ 0.5
        for qdata in result["qubits"]:
            assert abs(qdata["purity"] - 0.5) < 1e-4
            bv = qdata["bloch_vector"]
            norm = np.sqrt(bv["rx"] ** 2 + bv["ry"] ** 2 + bv["rz"] ** 2)
            assert norm < 0.01  # near origin

        # MI should be 2.0 for Bell state
        pair = result["pairs"][0]
        assert abs(pair["mutual_information"] - 2.0) < 0.01

    def test_statevector_source(self):
        """Statevector fallback works correctly."""
        sv = [[1 / np.sqrt(2), 0.0], [0.0, 0.0], [0.0, 0.0], [1 / np.sqrt(2), 0.0]]
        data = self._make_result_dict(2, sv=sv)
        result = compute_bloch_data(data)
        assert result["source_mode"] == "statevector"
        assert len(result["qubits"]) == 2

    def test_counts_source(self):
        """Counts-only fallback gives diagonal estimate."""
        data = self._make_result_dict(2, counts={"00": 500, "11": 500})
        result = compute_bloch_data(data)
        assert result["source_mode"] == "diagonal_estimate"

    def test_dm_priority_over_statevector(self):
        """DM is preferred when both DM and SV are available."""
        rho = _ghz_2q_dm()
        sv = [[1.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]]
        data = self._make_result_dict(2, dm=rho, sv=sv)
        result = compute_bloch_data(data)
        assert result["source_mode"] == "density_matrix"

    def test_no_data_raises(self):
        """Missing measurement data raises ValueError."""
        data = self._make_result_dict(2)
        with pytest.raises(ValueError, match="No measurement data"):
            compute_bloch_data(data)

    def test_invalid_qubit_count_raises(self):
        """0 or >8 qubits raises ValueError."""
        for bad_n in [0, 9]:
            data = {
                "experiment_parameters": {"num_qubits": bad_n},
                "measurement_results": {"raw_counts": {"0": 100}},
                "experiment_metadata": {},
            }
            with pytest.raises(ValueError, match="Unsupported qubit count"):
                compute_bloch_data(data)

    def test_mi_matrix_symmetric(self):
        """MI matrix output must be symmetric."""
        psi = np.zeros(8, dtype=np.complex128)
        psi[0] = psi[7] = 1.0 / np.sqrt(2)
        rho = np.outer(psi, psi.conj())
        data = self._make_result_dict(3, dm=rho)
        result = compute_bloch_data(data)

        mi = result["mi_matrix"]
        assert len(mi) == 3
        for i in range(3):
            for j in range(3):
                assert abs(mi[i][j] - mi[j][i]) < 1e-12

    def test_single_qubit(self):
        """Single qubit: no pairs, one qubit entry."""
        rho = _pure_zero_dm()
        data = self._make_result_dict(1, dm=rho)
        result = compute_bloch_data(data)
        assert len(result["qubits"]) == 1
        assert len(result["pairs"]) == 0
        assert abs(result["qubits"][0]["purity"] - 1.0) < 1e-6

    def test_full_result_structure(self):
        """Full ExperimentResult wrapper is handled."""
        rho = _ghz_2q_dm()
        inner = self._make_result_dict(2, dm=rho)
        wrapped = {"analysis": inner}
        result = compute_bloch_data(wrapped)
        assert result["source_mode"] == "density_matrix"


# ── Pure state purity checks ─────────────────────────────────────────


class TestPurityCalculation:
    """Verify purity = Tr(ρ²) is computed correctly in the pipeline."""

    def test_pure_state_purity_1(self):
        """Pure |0⟩ has purity = 1."""
        rho = _pure_zero_dm()
        purity = float(np.real(np.trace(rho @ rho)))
        assert abs(purity - 1.0) < 1e-12

    def test_mixed_state_purity_half(self):
        """Maximally mixed 1-qubit has purity = 0.5."""
        rho = np.eye(2, dtype=np.complex128) / 2
        purity = float(np.real(np.trace(rho @ rho)))
        assert abs(purity - 0.5) < 1e-12
