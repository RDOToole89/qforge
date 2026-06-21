"""Canonical qubit <-> bitstring-position convention (single source of truth).

The framework canonicalizes measurement counts in Qiskit's display order: a
length-n bitstring is written MSB-left, so the RIGHTMOST character is physical
qubit 0 and the LEFTMOST character is physical qubit n-1.

Analysis code, however, has historically indexed bitstrings positionally from the
LEFT (``bitstring[i]`` for "qubit i"). To keep this consistent and explicit -- so
a topology builder and the mutual-information matrix it is correlated against use
the SAME qubit identity -- route all qubit/bit lookups through these helpers
rather than indexing bitstrings ad hoc.

Convention used by the analysis layer (logical index == bitstring position):
    logical index i  ->  bitstring[i]        (leftmost = index 0)
    physical qubit   ->  n - 1 - i           (Qiskit: rightmost = qubit 0)
"""

from __future__ import annotations


def bit_for_qubit(bitstring: str, index: int) -> str:
    """Return the bit character at logical ``index`` (leftmost = 0) of ``bitstring``.

    This is the single accessor the analysis metrics use to read a qubit's bit,
    so the indexing convention lives in exactly one place.

    Args:
        bitstring: A canonical MSB-left bitstring (no spaces).
        index: Logical qubit index in [0, len(bitstring)).

    Returns:
        The single-character bit ("0" or "1").

    Raises:
        IndexError: If ``index`` is out of range.
    """
    return bitstring[index]


def physical_qubit_of_index(index: int, n_qubits: int) -> int:
    """Map a logical analysis index to the physical (Qiskit) qubit number.

    Under the canonical convention the leftmost bitstring position (logical index
    0) corresponds to physical qubit ``n-1`` (Qiskit numbers qubit 0 as the
    rightmost / least-significant bit).

    Args:
        index: Logical index (bitstring position), 0-based from the left.
        n_qubits: Total number of qubits.

    Returns:
        The physical qubit number (0-based, Qiskit convention).
    """
    return n_qubits - 1 - index
