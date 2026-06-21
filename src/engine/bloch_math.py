"""Bloch sphere computation: partial traces, Bloch vectors, correlators, MI.

Pure quantum math functions operating on density matrices. No web framework
dependencies — used by the Bloch API routes and directly testable.
"""

from __future__ import annotations

from itertools import combinations
from typing import Any, cast

import numpy as np
from numpy.typing import NDArray

# Pauli matrices
_I = np.eye(2, dtype=np.complex128)
_X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
_Y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
_Z = np.array([[1, 0], [0, -1]], dtype=np.complex128)


# ── Partial traces ──────────────────────────────────────────────────


def partial_trace_single_qubit(
    rho: NDArray[np.complex128], qubit_index: int, n_qubits: int
) -> NDArray[np.complex128]:
    """Trace out all qubits except one. Returns 2x2 reduced density matrix.

    Reshapes (2^n, 2^n) -> (2,2,...,2) with 2n axes, then contracts all
    index pairs except the target qubit via einsum.
    """
    dim = 2**n_qubits
    if rho.shape != (dim, dim):
        raise ValueError(f"Expected ({dim},{dim}) density matrix, got {rho.shape}")

    tensor = rho.reshape([2] * (2 * n_qubits))

    row_indices = list(range(n_qubits))
    col_indices = list(range(n_qubits, 2 * n_qubits))

    # For non-target qubits, set col index = row index (trace)
    for i in range(n_qubits):
        if i != qubit_index:
            col_indices[i] = row_indices[i]

    out_indices = [row_indices[qubit_index], col_indices[qubit_index]]
    # numpy stubs lack the einsum "sublist" overload signature used here.
    return cast(
        "NDArray[np.complex128]",
        np.einsum(tensor, row_indices + col_indices, out_indices),  # type: ignore[arg-type]
    )


def partial_trace_two_qubit(
    rho: NDArray[np.complex128], qubit_i: int, qubit_j: int, n_qubits: int
) -> NDArray[np.complex128]:
    """Trace out all qubits except two. Returns 4x4 reduced density matrix."""
    dim = 2**n_qubits
    if rho.shape != (dim, dim):
        raise ValueError(f"Expected ({dim},{dim}) density matrix, got {rho.shape}")

    tensor = rho.reshape([2] * (2 * n_qubits))

    row_indices = list(range(n_qubits))
    col_indices = list(range(n_qubits, 2 * n_qubits))

    keep = {qubit_i, qubit_j}
    for i in range(n_qubits):
        if i not in keep:
            col_indices[i] = row_indices[i]

    out_indices = [
        row_indices[qubit_i],
        row_indices[qubit_j],
        col_indices[qubit_i],
        col_indices[qubit_j],
    ]

    # numpy stubs lack the einsum "sublist" overload signature used here.
    reduced = cast(
        "NDArray[np.complex128]",
        np.einsum(tensor, row_indices + col_indices, out_indices),  # type: ignore[arg-type]
    )
    return reduced.reshape(4, 4)


# ── Bloch vectors and correlators ───────────────────────────────────


def density_matrix_to_bloch(rho_1q: NDArray[np.complex128]) -> dict[str, float]:
    """Extract Bloch vector from 2x2 density matrix.

    rho = (I + rx*X + ry*Y + rz*Z) / 2
    => rx = Tr(rho*X), ry = Tr(rho*Y), rz = Tr(rho*Z)
    """
    rx = float(np.real(np.trace(rho_1q @ _X)))
    ry = float(np.real(np.trace(rho_1q @ _Y)))
    rz = float(np.real(np.trace(rho_1q @ _Z)))
    return {"rx": rx, "ry": ry, "rz": rz}


def two_qubit_correlators(rho_2q: NDArray[np.complex128]) -> dict[str, float]:
    """Compute two-qubit Pauli expectation values from 4x4 density matrix.

    Each correlator is Tr(rho * (Pa x Pb)).
    """
    result = {}
    ops = {"z": _Z, "i": _I, "x": _X, "y": _Y}

    for label, (a, b) in [
        ("zi", ("z", "i")),
        ("iz", ("i", "z")),
        ("zz", ("z", "z")),
        ("xx", ("x", "x")),
        ("yy", ("y", "y")),
    ]:
        op = np.kron(ops[a], ops[b])
        result[label] = float(np.real(np.trace(rho_2q @ op)))

    return result


def mutual_information_from_rho(
    rho_2q: NDArray[np.complex128],
) -> float:
    """Compute mutual information I(A:B) = S(A) + S(B) - S(AB) from 4x4 density matrix."""

    def von_neumann_entropy(rho: NDArray[np.complex128]) -> float:
        eigenvalues = np.real(np.linalg.eigvalsh(rho))
        eigenvalues = eigenvalues[eigenvalues > 1e-15]
        return float(-np.sum(eigenvalues * np.log2(eigenvalues)))

    rho_a = partial_trace_single_qubit(rho_2q, 0, 2)
    rho_b = partial_trace_single_qubit(rho_2q, 1, 2)

    s_a = von_neumann_entropy(rho_a)
    s_b = von_neumann_entropy(rho_b)
    s_ab = von_neumann_entropy(rho_2q)

    return max(0.0, s_a + s_b - s_ab)


# ── Density matrix construction ─────────────────────────────────────


def counts_to_diagonal_density_matrix(
    counts: dict[str, int], n_qubits: int
) -> NDArray[np.complex128]:
    """Build diagonal density matrix from measurement counts.

    rho = sum_x p(x)|x><x| — gives correct Z-basis info only.
    """
    dim = 2**n_qubits
    rho = np.zeros((dim, dim), dtype=np.complex128)
    total = sum(counts.values())
    if total == 0:
        return rho

    for bitstring, count in counts.items():
        bits = bitstring.replace(" ", "")
        if len(bits) != n_qubits:
            continue
        idx = int(bits, 2)
        if 0 <= idx < dim:
            rho[idx, idx] = count / total

    return rho


def statevector_to_density_matrix(
    sv: list[list[float]],
) -> NDArray[np.complex128]:
    """Convert [real, imag] statevector to density matrix."""
    psi = np.array([complex(r, i) for r, i in sv], dtype=np.complex128)
    return np.outer(psi, psi.conj())


def json_density_matrix_to_numpy(
    dm: list[list[list[float]]],
) -> NDArray[np.complex128]:
    """Convert JSON density matrix (NxN of [real, imag]) to numpy."""
    n = len(dm)
    rho = np.zeros((n, n), dtype=np.complex128)
    for i in range(n):
        for j in range(n):
            r, im = dm[i][j]
            rho[i, j] = complex(r, im)
    return rho


# ── High-level computation ──────────────────────────────────────────


def compute_bloch_data(data: dict[str, Any]) -> dict[str, Any]:
    """Compute Bloch visualization data from an experiment result dict.

    Works with both stored JSON and in-memory engine results.
    Raises ValueError on invalid data.
    """
    # Navigate result structure: full ExperimentResult or raw analysis
    if "analysis" in data:
        analysis = data["analysis"]
        params = analysis.get("experiment_parameters", {})
        meas = analysis.get("measurement_results", {})
        meta = analysis.get("experiment_metadata", {})
        metrics_bundle = data.get("metrics_bundle")
    else:
        params = data.get("experiment_parameters", {})
        meas = data.get("measurement_results", {})
        meta = data.get("experiment_metadata", {})
        metrics_bundle = data.get("metrics_bundle")

    n_qubits = int(params.get("num_qubits", 0))
    if n_qubits < 1 or n_qubits > 8:
        raise ValueError(f"Unsupported qubit count: {n_qubits} (must be 1-8)")

    # Build density matrix from best available source
    source_mode: str
    rho: NDArray[np.complex128]

    dm_raw = meas.get("density_matrix")
    sv_raw = meas.get("statevector")
    counts = meas.get("raw_counts", {})

    if dm_raw is not None:
        rho = json_density_matrix_to_numpy(dm_raw)
        source_mode = "density_matrix"
    elif sv_raw is not None:
        rho = statevector_to_density_matrix(sv_raw)
        source_mode = "statevector"
    elif counts:
        rho = counts_to_diagonal_density_matrix(counts, n_qubits)
        source_mode = "diagonal_estimate"
    else:
        raise ValueError("No measurement data found")

    # Per-qubit Bloch vectors and purity
    qubits = []
    for q in range(n_qubits):
        rho_q = partial_trace_single_qubit(rho, q, n_qubits)
        bv = density_matrix_to_bloch(rho_q)
        purity = float(np.real(np.trace(rho_q @ rho_q)))
        qubits.append(
            {
                "qubit_index": q,
                "bloch_vector": bv,
                "purity": round(purity, 6),
            }
        )

    # Qubit pairs: correlators and mutual information
    pairs = []
    mi_matrix = [[0.0] * n_qubits for _ in range(n_qubits)]

    for qi, qj in combinations(range(n_qubits), 2):
        rho_2q = partial_trace_two_qubit(rho, qi, qj, n_qubits)
        corrs = two_qubit_correlators(rho_2q)
        mi = mutual_information_from_rho(rho_2q)

        pairs.append(
            {
                "qubit_i": qi,
                "qubit_j": qj,
                "correlators": corrs,
                "mutual_information": round(mi, 6),
            }
        )

        mi_matrix[qi][qj] = round(mi, 6)
        mi_matrix[qj][qi] = round(mi, 6)

    # Metrics
    metrics = None
    if metrics_bundle and isinstance(metrics_bundle, dict):
        raw_metrics = metrics_bundle.get("metrics", {})
        if raw_metrics:
            metrics = {}
            for name, entry in raw_metrics.items():
                if isinstance(entry, dict):
                    metrics[name] = {
                        "value": entry.get("value"),
                        "ci95": entry.get("ci95"),
                    }

    return {
        "experiment_id": meta.get("experiment_id", ""),
        "state_type": params.get("state_type", ""),
        "num_qubits": n_qubits,
        "noise_type": params.get("noise_type") if params.get("noise_enabled") else None,
        "error_rate": params.get("error_rate") if params.get("noise_enabled") else None,
        "fidelity": meas.get("fidelity"),
        "source_mode": source_mode,
        "qubits": qubits,
        "pairs": pairs,
        "mi_matrix": mi_matrix,
        "metrics": metrics,
    }
