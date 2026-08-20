"""Pauli-string observables over measurement counts and exact states.

Pauli labels use the same MSB-left convention as canonical bitstrings:
the leftmost character is logical index 0 (``bitstring[0]``).
"""

from __future__ import annotations

import math

import numpy as np
from numpy.typing import NDArray

from qforge.core.math.indexing import bit_for_qubit
from qforge.core.math.pauli import PAULIS

_PAULI_CHARS = frozenset("IXYZ")


def parse_pauli_string(label: str, n_qubits: int) -> str:
    """Validate and normalize a Pauli string.

    Args:
        label: String of I/X/Y/Z, length ``n_qubits``.
        n_qubits: Expected number of qubits.

    Returns:
        Uppercase Pauli string.

    Raises:
        ValueError: If the label is the wrong length or contains non-Pauli characters.
    """
    pauli = label.strip().upper()
    if len(pauli) != n_qubits:
        raise ValueError(f"Pauli string {label!r} has length {len(pauli)}, expected {n_qubits}")
    bad = set(pauli) - _PAULI_CHARS
    if bad:
        raise ValueError(f"Pauli string {label!r} contains non-Pauli characters: {sorted(bad)}")
    return pauli


def is_z_basis_pauli(pauli: str) -> bool:
    """Return True if ``pauli`` is measurable in the computational (Z) basis."""
    return set(pauli) <= {"I", "Z"}


def measurement_basis(pauli: str) -> tuple[str, ...]:
    """Per-qubit measure basis: I is treated as Z (no rotation)."""
    return tuple("Z" if char == "I" else char for char in pauli)


def pauli_matrix(pauli: str) -> NDArray[np.complex128]:
    """Kronecker product of single-qubit Paulis in MSB-left / logical order."""
    mats = [PAULIS[char] for char in pauli]
    out = mats[0]
    for mat in mats[1:]:
        out = np.kron(out, mat)
    return out


def pauli_expectation_from_counts(counts: dict[str, int], pauli: str) -> tuple[float, float]:
    """Estimate ⟨P⟩ from Z-basis (or already-rotated) shot counts.

    Non-I positions contribute to parity: odd number of 1s → eigenvalue −1.
    After an X or Y basis rotation, pass the original Pauli string — the
    rotated measurement has already mapped those axes onto Z.

    Args:
        counts: Canonical MSB-left bitstring counts.
        pauli: Normalized Pauli string.

    Returns:
        ``(value, stderr)`` where stderr is the shot-noise estimate
        ``sqrt((1 − ⟨P⟩²) / N)``.
    """
    n_plus = 0
    n_minus = 0
    for bitstring, count in counts.items():
        parity = 0
        for index, char in enumerate(pauli):
            if char == "I":
                continue
            if bit_for_qubit(bitstring, index) == "1":
                parity ^= 1
        if parity:
            n_minus += count
        else:
            n_plus += count
    total = n_plus + n_minus
    if total <= 0:
        return 0.0, 0.0
    value = (n_plus - n_minus) / total
    variance = max(0.0, 1.0 - value * value)
    stderr = math.sqrt(variance / total)
    return float(value), float(stderr)


def pauli_expectation_from_statevector(statevector: NDArray[np.complex128], pauli: str) -> float:
    """Exact ⟨ψ|P|ψ⟩. ``statevector`` uses the same index convention as Qiskit data."""
    psi = np.asarray(statevector, dtype=complex).reshape(-1)
    matrix = pauli_matrix(pauli)
    value = np.vdot(psi, matrix @ psi)
    return float(np.real(value))


def pauli_expectation_from_density_matrix(
    density_matrix: NDArray[np.complex128],
    pauli: str,
) -> float:
    """Exact Tr(ρ P)."""
    rho = np.asarray(density_matrix, dtype=complex)
    matrix = pauli_matrix(pauli)
    value = np.trace(rho @ matrix)
    return float(np.real(value))
