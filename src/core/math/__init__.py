"""Shared, tested mathematical primitives for the quantum framework.

Single source of truth for low-level math used across physics (noise models,
state preparation), analysis (metrics), and the engine (fidelity, Bloch). Import
these instead of re-deriving the same constants/formulas in multiple modules so
each concept is implemented and tested exactly once.
"""

from src.core.math.distances import gini_coefficient, total_variation_distance
from src.core.math.indexing import bit_for_qubit, physical_qubit_of_index
from src.core.math.pauli import PAULI_I, PAULI_X, PAULI_Y, PAULI_Z, PAULIS, pauli
from src.core.math.rates import relaxation_probability

__all__ = [
    "PAULI_I",
    "PAULI_X",
    "PAULI_Y",
    "PAULI_Z",
    "PAULIS",
    "pauli",
    "relaxation_probability",
    "total_variation_distance",
    "gini_coefficient",
    "bit_for_qubit",
    "physical_qubit_of_index",
]
