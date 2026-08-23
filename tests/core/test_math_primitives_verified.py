"""Exact-value tests for the shared math primitives in ``src/qforge/core/math``.

These are the single source of truth for Pauli matrices, relaxation probability,
total variation distance, Gini, and the qubit/bit indexing convention. Every
consumer across the codebase imports from here, so they are tested once.
"""

from __future__ import annotations

import numpy as np
import pytest

from qforge.core.math import (
    PAULI_I,
    PAULI_X,
    PAULI_Y,
    PAULI_Z,
    bit_for_qubit,
    gini_coefficient,
    pauli,
    physical_qubit_of_index,
    relaxation_probability,
    total_variation_distance,
)


# --- Pauli matrices --------------------------------------------------------
def test_pauli_values() -> None:
    assert np.array_equal(PAULI_I, [[1, 0], [0, 1]])
    assert np.array_equal(PAULI_X, [[0, 1], [1, 0]])
    assert np.array_equal(PAULI_Y, [[0, -1j], [1j, 0]])
    assert np.array_equal(PAULI_Z, [[1, 0], [0, -1]])


def test_pauli_algebra() -> None:
    # X^2 = Y^2 = Z^2 = I ; XY = iZ
    for p in (PAULI_X, PAULI_Y, PAULI_Z):
        assert np.allclose(p @ p, PAULI_I)
    assert np.allclose(PAULI_X @ PAULI_Y, 1j * PAULI_Z)


def test_pauli_constants_are_readonly() -> None:
    with pytest.raises(ValueError):
        PAULI_X[0, 0] = 5.0


def test_pauli_factory_returns_writable_copy() -> None:
    x = pauli("x")
    assert np.array_equal(x, PAULI_X)
    x[0, 0] = 9.0  # must not raise and must not affect the constant
    assert PAULI_X[0, 0] == 0
    with pytest.raises(KeyError):
        pauli("Q")


# --- relaxation probability ------------------------------------------------
def test_relaxation_probability_closed_form() -> None:
    assert relaxation_probability(20e-9, 100e-6) == pytest.approx(1.9998000133325533e-4)
    assert relaxation_probability(20e-9, 80e-6) == pytest.approx(2.4996875260396845e-4)
    assert relaxation_probability(0.0, 100e-6) == 0.0


@pytest.mark.parametrize("bad", [(1.0, 0.0), (1.0, -1.0), (-1.0, 1.0)])
def test_relaxation_probability_invalid(bad: tuple[float, float]) -> None:
    with pytest.raises(ValueError):
        relaxation_probability(*bad)


# --- total variation distance ----------------------------------------------
def test_tvd_values() -> None:
    assert total_variation_distance([0.5, 0.5], [0.5, 0.5]) == 0.0
    assert total_variation_distance([1.0, 0.0], [0.0, 1.0]) == 1.0
    assert total_variation_distance([0.75, 0.25], [0.25, 0.75]) == pytest.approx(0.5)


def test_tvd_shape_mismatch() -> None:
    with pytest.raises(ValueError):
        total_variation_distance([0.5, 0.5], [1.0])


# --- Gini ------------------------------------------------------------------
def test_gini_values() -> None:
    assert gini_coefficient([1, 3]) == pytest.approx(0.25)
    assert gini_coefficient([5, 5, 5, 5]) == 0.0
    assert gini_coefficient([0, 0, 0]) == 0.0  # zero total
    assert gini_coefficient([42]) == 0.0  # single value
    # order independence
    assert gini_coefficient([3, 1]) == pytest.approx(0.25)


# --- indexing convention ---------------------------------------------------
def test_bit_for_qubit() -> None:
    assert bit_for_qubit("011", 0) == "0"
    assert bit_for_qubit("011", 2) == "1"


def test_physical_qubit_mapping() -> None:
    # leftmost logical index 0 -> physical qubit n-1 (Qiskit rightmost = qubit 0)
    assert physical_qubit_of_index(0, 3) == 2
    assert physical_qubit_of_index(2, 3) == 0
