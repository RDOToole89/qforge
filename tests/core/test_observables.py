"""Verified Pauli-string expectation math (MSB-left / bitstring order)."""

from __future__ import annotations

import numpy as np
import pytest

from qforge.core.math.observables import (
    is_z_basis_pauli,
    measurement_basis,
    parse_pauli_string,
    pauli_expectation_from_counts,
    pauli_expectation_from_density_matrix,
    pauli_expectation_from_statevector,
    pauli_matrix,
)


def test_parse_normalizes_and_rejects() -> None:
    assert parse_pauli_string(" zz ", 2) == "ZZ"
    with pytest.raises(ValueError, match="length"):
        parse_pauli_string("ZZZ", 2)
    with pytest.raises(ValueError, match="non-Pauli"):
        parse_pauli_string("ZA", 2)


def test_z_basis_and_measurement_basis() -> None:
    assert is_z_basis_pauli("IZ")
    assert not is_z_basis_pauli("XI")
    assert measurement_basis("XI") == ("X", "Z")
    assert measurement_basis("IY") == ("Z", "Y")


def test_parity_from_synthetic_counts() -> None:
    assert pauli_expectation_from_counts({"00": 50, "11": 50}, "ZZ") == (1.0, 0.0)
    value, stderr = pauli_expectation_from_counts({"10": 100}, "ZI")
    assert value == pytest.approx(-1.0)
    assert stderr == pytest.approx(0.0)
    value_iz, _ = pauli_expectation_from_counts({"10": 100}, "IZ")
    assert value_iz == pytest.approx(1.0)
    mixed, mixed_err = pauli_expectation_from_counts({"00": 75, "01": 25}, "ZZ")
    assert mixed == pytest.approx(0.5)
    assert mixed_err == pytest.approx(np.sqrt((1.0 - 0.25) / 100))


def test_empty_counts() -> None:
    assert pauli_expectation_from_counts({}, "Z") == (0.0, 0.0)


def test_bell_phi_plus_exact_paulis() -> None:
    """|Φ+⟩ = (|00⟩+|11⟩)/√2 → ⟨ZZ⟩=1, ⟨XX⟩=1, ⟨YY⟩=−1."""
    psi = np.array([1 / np.sqrt(2), 0.0, 0.0, 1 / np.sqrt(2)], dtype=complex)
    rho = np.outer(psi, psi.conj())
    assert pauli_expectation_from_statevector(psi, "ZZ") == pytest.approx(1.0)
    assert pauli_expectation_from_statevector(psi, "XX") == pytest.approx(1.0)
    assert pauli_expectation_from_statevector(psi, "YY") == pytest.approx(-1.0)
    assert pauli_expectation_from_statevector(psi, "ZI") == pytest.approx(0.0)
    assert pauli_expectation_from_density_matrix(rho, "ZZ") == pytest.approx(1.0)
    assert pauli_expectation_from_density_matrix(rho, "YY") == pytest.approx(-1.0)


def test_pauli_matrix_endianness_zi_iz() -> None:
    """Logical leftmost is index 0: ZI ≠ IZ."""
    zi = pauli_matrix("ZI")
    iz = pauli_matrix("IZ")
    assert not np.allclose(zi, iz)
    ket10 = np.array([0, 0, 1, 0], dtype=complex)
    assert pauli_expectation_from_statevector(ket10, "ZI") == pytest.approx(-1.0)
    assert pauli_expectation_from_statevector(ket10, "IZ") == pytest.approx(1.0)
