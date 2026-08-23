"""Estimate Pauli observables on an executed experiment.

Core math lives in ``qforge.core.math.observables``. This module only
groups extra measurement circuits and attaches results.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from qiskit import QuantumCircuit

from qforge.core.math.indexing import physical_qubit_of_index
from qforge.core.math.observables import (
    is_z_basis_pauli,
    measurement_basis,
    pauli_expectation_from_counts,
    pauli_expectation_from_density_matrix,
    pauli_expectation_from_statevector,
)
from qforge.engine.analysis.metrics import extract_counts_from_result
from qforge.engine.models.measurement import ObservableEstimate

if TYPE_CHECKING:
    from qforge.engine.execution.runner import EngineExperimentRunner


def _array_from_serialized_statevector(
    statevector: list[list[float]],
) -> np.ndarray:
    return np.array([complex(real, imag) for real, imag in statevector], dtype=complex)


def _array_from_serialized_density_matrix(
    density_matrix: list[list[list[float]]],
) -> np.ndarray:
    return np.array(
        [[complex(pair[0], pair[1]) for pair in row] for row in density_matrix],
        dtype=complex,
    )


def apply_pauli_basis(circuit: QuantumCircuit, pauli: str) -> QuantumCircuit:
    """Copy ``circuit``, map X/Y sites onto Z, and measure."""
    rotated = circuit.copy()
    rotated.remove_final_measurements()
    n_qubits = rotated.num_qubits
    for index, char in enumerate(pauli):
        physical = physical_qubit_of_index(index, n_qubits)
        if char == "X":
            rotated.h(physical)
        elif char == "Y":
            rotated.sdg(physical)
            rotated.h(physical)
    rotated.measure_all()
    return rotated


def _exact_value(
    pauli: str,
    *,
    statevector: list[list[float]] | None,
    density_matrix: list[list[list[float]]] | None,
) -> float | None:
    if statevector is not None:
        return pauli_expectation_from_statevector(
            _array_from_serialized_statevector(statevector),
            pauli,
        )
    if density_matrix is not None:
        return pauli_expectation_from_density_matrix(
            _array_from_serialized_density_matrix(density_matrix),
            pauli,
        )
    return None


def estimate_observables(
    *,
    labels: list[str],
    counts: dict[str, int],
    n_qubits: int,
    shots: int,
    sim_mode: str,
    circuit: QuantumCircuit,
    runner: EngineExperimentRunner,
    statevector: list[list[float]] | None = None,
    density_matrix: list[list[list[float]]] | None = None,
) -> dict[str, ObservableEstimate]:
    """Return Pauli estimates for ``labels``.

    Statevector / density-matrix modes are exact (stderr is None). QASM and
    hardware reuse Z-basis counts for I/Z-only strings and run extra circuits
    for X/Y, grouped by measurement basis.
    """
    if any(len(pauli) != n_qubits for pauli in labels):
        raise ValueError("Every Pauli string must have length num_qubits")
    exact_ok = sim_mode in {"statevector", "density_matrix"}
    estimates: dict[str, ObservableEstimate] = {}
    need_shots: list[str] = []

    for pauli in labels:
        if exact_ok:
            value = _exact_value(pauli, statevector=statevector, density_matrix=density_matrix)
            if value is not None:
                estimates[pauli] = ObservableEstimate(pauli=pauli, value=value)
                continue
        if is_z_basis_pauli(pauli):
            value, stderr = pauli_expectation_from_counts(counts, pauli)
            estimates[pauli] = ObservableEstimate(
                pauli=pauli, value=value, stderr=stderr, shots=shots
            )
        else:
            need_shots.append(pauli)

    if not need_shots:
        return estimates

    grouped: dict[tuple[str, ...], list[str]] = {}
    for pauli in need_shots:
        grouped.setdefault(measurement_basis(pauli), []).append(pauli)

    for basis_paulis in grouped.values():
        sample = basis_paulis[0]
        rotated = apply_pauli_basis(circuit, sample)
        raw = runner.execute_circuit(rotated)
        extra_counts = extract_counts_from_result(raw, num_qubits=circuit.num_qubits)
        extra_shots = int(sum(extra_counts.values())) or shots
        for pauli in basis_paulis:
            value, stderr = pauli_expectation_from_counts(extra_counts, pauli)
            estimates[pauli] = ObservableEstimate(
                pauli=pauli, value=value, stderr=stderr, shots=extra_shots
            )
    return estimates
