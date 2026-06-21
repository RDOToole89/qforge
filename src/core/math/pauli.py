"""Single-qubit Pauli matrices (the one definition used across the codebase).

Constants are read-only (``write=False``) to prevent accidental in-place mutation
by callers that share the module-level arrays.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def _frozen(matrix: list[list[complex]]) -> NDArray[np.complex128]:
    arr = np.array(matrix, dtype=complex)
    arr.setflags(write=False)
    return arr


PAULI_I: NDArray[np.complex128] = _frozen([[1, 0], [0, 1]])
PAULI_X: NDArray[np.complex128] = _frozen([[0, 1], [1, 0]])
PAULI_Y: NDArray[np.complex128] = _frozen([[0, -1j], [1j, 0]])
PAULI_Z: NDArray[np.complex128] = _frozen([[1, 0], [0, -1]])

PAULIS: dict[str, NDArray[np.complex128]] = {
    "I": PAULI_I,
    "X": PAULI_X,
    "Y": PAULI_Y,
    "Z": PAULI_Z,
}


def pauli(label: str) -> NDArray[np.complex128]:
    """Return a fresh (writable) copy of the Pauli matrix for ``label`` (I/X/Y/Z).

    Args:
        label: One of "I", "X", "Y", "Z" (case-insensitive).

    Returns:
        A new 2x2 complex array (safe to mutate).

    Raises:
        KeyError: If ``label`` is not a Pauli label.
    """
    return PAULIS[label.upper()].copy()
