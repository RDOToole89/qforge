"""Generate golden quantum-math fixtures from the verified Python backend.

This is the anti-drift guarantee for the client's consolidated quantum math
(``apps/client/src/lib/quantum``). For a fixed set of states it computes, using
``src/engine/bloch_math.py`` (the verified backend), the per-qubit Bloch
vectors, per-qubit purity Tr(rho^2), and two-qubit Pauli correlators, then
writes them to JSON. The frontend golden test loads these and asserts the TS
module reproduces the same numbers to ~1e-6, proving FE math == BE math.

Basis convention
----------------
The frontend uses qubit 0 = MSB = leftmost bitstring character. Statevectors
prepared by Qiskit are little-endian (qubit 0 = LSB); they are converted to the
frontend convention via ``reverse_qargs()`` before being fed to the backend
math (identical to ``scripts/gen_frontend_constants.py``).

The backend ``partial_trace_single_qubit(rho, q, n)`` reshapes a (2^n, 2^n)
density matrix to ``[2] * 2n`` axes where axis 0 is the most-significant index,
i.e. qubit 0 = MSB — the *same* convention as the frontend. Therefore, when the
input statevector is in frontend convention, backend "qubit q" lines up exactly
with frontend "qubit q". This alignment is exercised directly by the
``asym_product3`` fixture (an asymmetric product state whose three qubits have
distinct Bloch vectors), so an index mismatch would fail the golden test rather
than pass silently.

Run:
    uv run python scripts/gen_quantum_golden.py
    (or: .venv/Scripts/python.exe scripts/gen_quantum_golden.py)
"""

from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray
from qiskit.quantum_info import Statevector

from src.core.state_preparation.state_factory import prepare_state
from src.engine.bloch_math import (
    density_matrix_to_bloch,
    partial_trace_single_qubit,
    partial_trace_two_qubit,
    statevector_to_density_matrix,
    two_qubit_correlators,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = (
    REPO_ROOT
    / "apps"
    / "client"
    / "src"
    / "lib"
    / "quantum"
    / "__tests__"
    / "golden"
    / "bloch_golden.json"
)

SCHEMA_VERSION = "1.0"
_ZERO_TOL = 1e-12
_ROUND = 12

# Single-qubit kets in the {|0>, |1>} basis (column vectors).
_KET0 = np.array([1.0, 0.0], dtype=np.complex128)
_KET_PLUS = np.array([1.0, 1.0], dtype=np.complex128) / np.sqrt(2)
_KET_PLUS_I = np.array([1.0, 1.0j], dtype=np.complex128) / np.sqrt(2)


def _canonical_global_phase(vec: NDArray[np.complex128]) -> NDArray[np.complex128]:
    """Multiply by a global phase so the first nonzero amplitude is real > 0."""
    for amp in vec:
        if abs(amp) > _ZERO_TOL:
            return vec * (abs(amp) / amp)
    return vec


def _prepared_statevector(state_type: str, n: int, params: dict | None) -> NDArray[np.complex128]:
    """Frontend-convention statevector (qubit 0 = MSB) from a backend circuit."""
    qc = prepare_state(state_type, n, custom_params=params)
    sv = np.asarray(Statevector(qc).reverse_qargs().data)  # -> qubit 0 = MSB
    return _canonical_global_phase(sv)


def _product_statevector(*kets: NDArray[np.complex128]) -> NDArray[np.complex128]:
    """Tensor product of single-qubit kets in MSB order (first arg = qubit 0)."""
    out = kets[0]
    for k in kets[1:]:
        out = np.kron(out, k)
    return _canonical_global_phase(np.asarray(out, dtype=np.complex128))


def _sv_to_json(sv: NDArray[np.complex128]) -> list[list[float]]:
    """[real, imag] pairs with float-dust cleaned and -0.0 normalised."""
    out: list[list[float]] = []
    for amp in sv:
        re = round(float(amp.real), _ROUND)
        im = round(float(amp.imag), _ROUND)
        out.append([re + 0.0, im + 0.0])
    return out


def _compute_state(sv: NDArray[np.complex128], n: int) -> dict[str, Any]:
    """Compute per-qubit Bloch/purity and per-pair correlators via the backend."""
    rho = statevector_to_density_matrix(_sv_to_json(sv))

    qubits = []
    for q in range(n):
        rho_q = partial_trace_single_qubit(rho, q, n)
        bloch = density_matrix_to_bloch(rho_q)
        purity = float(np.real(np.trace(rho_q @ rho_q)))
        qubits.append(
            {
                "qubit_index": q,
                "bloch": {k: round(v, _ROUND) for k, v in bloch.items()},
                "purity": round(purity, _ROUND),
            }
        )

    pairs = []
    for qi, qj in combinations(range(n), 2):
        rho_2q = partial_trace_two_qubit(rho, qi, qj, n)
        corr = two_qubit_correlators(rho_2q)
        pairs.append(
            {
                "qubit_i": qi,
                "qubit_j": qj,
                "correlators": {k: round(v, _ROUND) for k, v in corr.items()},
            }
        )

    return {"qubits": qubits, "pairs": pairs}


# State id -> ("prepared", state_type, n, params) | ("product", [kets...], n)
_STATES: list[dict[str, Any]] = [
    {"id": "bell_phi_plus", "n": 2, "kind": "prepared",
     "state_type": "BELL", "params": {"variant": "phi_plus"},
     "desc": "Bell |Phi+> = (|00>+|11>)/sqrt2"},
    {"id": "ghz2", "n": 2, "kind": "prepared",
     "state_type": "GHZ", "params": None,
     "desc": "GHZ(2) (identical to Bell |Phi+>)"},
    {"id": "ghz3", "n": 3, "kind": "prepared",
     "state_type": "GHZ", "params": None,
     "desc": "GHZ(3) = (|000>+|111>)/sqrt2"},
    {"id": "w3", "n": 3, "kind": "prepared",
     "state_type": "W", "params": None,
     "desc": "W(3) = (|001>+|010>+|100>)/sqrt3"},
    {"id": "cluster3", "n": 3, "kind": "prepared",
     "state_type": "CLUSTER", "params": None,
     "desc": "Linear cluster state on 3 qubits"},
    {"id": "asym_product3", "n": 3, "kind": "product",
     "kets": [_KET0, _KET_PLUS, _KET_PLUS_I],
     "desc": "Asymmetric product |0> (x) |+> (x) |+i> "
             "(verifies per-qubit index alignment BE<->FE)"},
]


def main() -> None:
    states_out: list[dict[str, Any]] = []
    for spec in _STATES:
        n = spec["n"]
        if spec["kind"] == "prepared":
            sv = _prepared_statevector(spec["state_type"], n, spec["params"])
        else:
            sv = _product_statevector(*spec["kets"])

        computed = _compute_state(sv, n)
        states_out.append(
            {
                "id": spec["id"],
                "description": spec["desc"],
                "num_qubits": n,
                "statevector": _sv_to_json(sv),
                "qubits": computed["qubits"],
                "pairs": computed["pairs"],
            }
        )

    doc = {
        "schema_version": SCHEMA_VERSION,
        "generated_by": "scripts/gen_quantum_golden.py",
        "source": "src/engine/bloch_math.py",
        "convention": (
            "qubit 0 = MSB = leftmost bitstring char; statevector amplitudes are "
            "[real, imag] pairs of length 2^n. Backend partial_trace_single_qubit "
            "uses the same MSB ordering, so qubit index q matches FE qubit index q."
        ),
        "states": states_out,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(states_out)} states to {OUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
