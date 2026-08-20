"""Shared, reusable test helpers for the verified physics/math test suite.

This module centralises the small quantum-mechanics primitives that were
previously copy-pasted across several verified test files: the Pauli matrices,
Kraus-channel application / completeness checks, the Choi-matrix equality check
used to cross-validate against Qiskit, and closed-form reference statevectors
(GHZ, W, Bell) written in Qiskit little-endian ordering.

It is named ``_qhelpers`` (leading underscore, not ``test_*``) so pytest does
not collect it as a test module. Import it as::

    from tests._qhelpers import apply_channel, ghz_statevector, ...
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from qiskit.quantum_info import Choi, Kraus

# Single source of truth for the Pauli matrices: the real codebase definition.
from qforge.core.math import PAULI_I, PAULI_X, PAULI_Y, PAULI_Z

# Conventional short aliases used throughout the physics tests.
I2 = PAULI_I
X = PAULI_X
Y = PAULI_Y
Z = PAULI_Z

# Common reciprocal-root-2 amplitude.
INV_SQRT2 = 1.0 / np.sqrt(2.0)


# --------------------------------------------------------------------------- #
# Kraus channels
# --------------------------------------------------------------------------- #


def apply_channel(kraus: list[np.ndarray], rho: np.ndarray) -> np.ndarray:
    """Apply a Kraus channel to a density matrix: rho -> sum_i K_i rho K_i^dagger."""
    out = np.zeros_like(rho, dtype=complex)
    for k in kraus:
        out += k @ rho @ k.conj().T
    return out


def completeness_sum(kraus: list[np.ndarray]) -> np.ndarray:
    """Return sum_i K_i^dagger K_i for a list of Kraus operators."""
    dim = kraus[0].shape[0]
    acc = np.zeros((dim, dim), dtype=complex)
    for k in kraus:
        acc += k.conj().T @ k
    return acc


def assert_kraus_complete(kraus: list[np.ndarray], dim: int, atol: float = 1e-12) -> None:
    """Assert the Kraus set is trace-preserving: sum_i K_i^dagger K_i == I_dim."""
    assert np.allclose(completeness_sum(kraus), np.eye(dim), atol=atol)


def choi_equal(kraus: list[np.ndarray], qiskit_error_or_channel, atol: float = 1e-9) -> bool:
    """Decomposition-independent channel equality via Choi matrices."""
    return bool(np.allclose(Choi(Kraus(kraus)).data, Choi(qiskit_error_or_channel).data, atol=atol))


# --------------------------------------------------------------------------- #
# Density matrices
# --------------------------------------------------------------------------- #


def density_matrix_from_statevector(psi: np.ndarray) -> np.ndarray:
    """Pure-state density matrix |psi><psi| from a statevector."""
    return np.outer(psi, psi.conj())


# --------------------------------------------------------------------------- #
# Known statevectors (Qiskit little-endian ordering)
# --------------------------------------------------------------------------- #


def ghz_statevector(n: int) -> NDArray[np.complex128]:
    """GHZ statevector (|0...0> + |1...1>)/sqrt(2) on ``n`` qubits (n >= 2)."""
    sv = np.zeros(2**n, dtype=complex)
    sv[0] = INV_SQRT2
    sv[-1] = INV_SQRT2
    return sv


def w_statevector(n: int) -> NDArray[np.complex128]:
    """W statevector: equal superposition of single-excitation states on ``n`` qubits.

    Little-endian: qubit ``i`` excited -> basis index ``1 << i``.
    """
    sv = np.zeros(2**n, dtype=complex)
    amp = 1.0 / np.sqrt(n)
    for i in range(n):
        sv[1 << i] = amp
    return sv


# Closed-form two-qubit Bell states (little-endian basis order).
PHI_PLUS: NDArray[np.complex128] = np.array([INV_SQRT2, 0, 0, INV_SQRT2], dtype=complex)
PHI_MINUS: NDArray[np.complex128] = np.array([INV_SQRT2, 0, 0, -INV_SQRT2], dtype=complex)
PSI_PLUS: NDArray[np.complex128] = np.array([0, INV_SQRT2, INV_SQRT2, 0], dtype=complex)
PSI_MINUS: NDArray[np.complex128] = np.array([0, INV_SQRT2, -INV_SQRT2, 0], dtype=complex)

BELL_STATEVECTORS: dict[str, NDArray[np.complex128]] = {
    "phi_plus": PHI_PLUS,
    "phi_minus": PHI_MINUS,
    "psi_plus": PSI_PLUS,
    "psi_minus": PSI_MINUS,
}


def bell_statevector(variant: str = "phi_plus") -> NDArray[np.complex128]:
    """Return a fresh copy of the requested Bell statevector."""
    return BELL_STATEVECTORS[variant].copy()


# --------------------------------------------------------------------------- #
# Bootstrap statistics (shared by the math core / intermediates tests)
# --------------------------------------------------------------------------- #


def fraction_ones_q0(counts: dict) -> float:
    """Fraction of shots whose qubit-0 bit is 1."""
    total = sum(counts.values())
    ones = sum(c for bs, c in counts.items() if bs[0] == "1")
    return ones / total if total else 0.0
