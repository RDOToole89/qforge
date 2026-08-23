"""Short educational blurbs for gates that appear on a circuit.

The diagram itself is Qiskit's ``circuit.draw``. This module only labels
the unique instruction names on that circuit.
"""

from __future__ import annotations

from typing import Any

# Qiskit instruction name → (diagram label, one-line explainer).
_GATE_EXPLAINERS: dict[str, tuple[str, str]] = {
    "h": ("H", "Hadamard — superposition (|0⟩+|1⟩)/√2"),
    "x": ("X", "Pauli X — bit flip |0⟩↔|1⟩"),
    "y": ("Y", "Pauli Y — bit and phase flip"),
    "z": ("Z", "Pauli Z — phase flip on |1⟩"),
    "s": ("S", "S — √Z phase gate"),
    "sdg": ("Sdg", "S† — inverse of S"),
    "t": ("T", "T — π/8 phase gate"),
    "tdg": ("Tdg", "T† — inverse of T"),
    "sx": ("SX", "√X — square-root of NOT"),
    "id": ("I", "Identity — do nothing"),
    "p": ("P", "P(λ) — phase gate"),
    "u": ("U", "U(θ,φ,λ) — general single-qubit rotation"),
    "rx": ("Rx", "Rx(θ) — rotate around X"),
    "ry": ("Ry", "Ry(θ) — rotate around Y"),
    "rz": ("Rz", "Rz(θ) — rotate around Z (phase)"),
    "cx": ("CX", "CNOT — flip the target if the control is |1⟩"),
    "cy": ("CY", "Controlled-Y"),
    "cz": ("CZ", "Controlled-Z — phase on |11⟩"),
    "swap": ("SWAP", "Exchange two qubits"),
    "ccx": ("CCX", "Toffoli — flip the target if both controls are |1⟩"),
    "rzz": ("RZZ", "Rzz(θ) — ZZ-coupling rotation"),
    "measure": ("Measure", "Measure — collapse onto a classical bit"),
    "barrier": ("Barrier", "Barrier — visual grouping only, no physics"),
    "reset": ("Reset", "Reset — return the qubit to |0⟩"),
}


def explain_circuit_gates(circuit: Any) -> list[dict[str, str]]:
    """Return unique gates on ``circuit`` in first-seen order, with explainers.

    Args:
        circuit: A Qiskit ``QuantumCircuit`` (or anything with ``.data``).

    Returns:
        List of ``{"name", "label", "explainer"}`` dicts. Unknown instructions
        get a generic fallback so the legend still lists them.
    """
    seen: set[str] = set()
    rows: list[dict[str, str]] = []
    for instruction in getattr(circuit, "data", ()):
        operation = getattr(instruction, "operation", None)
        raw = getattr(operation, "name", None) or getattr(instruction, "name", None)
        if not raw:
            continue
        name = str(raw).lower()
        if name in seen:
            continue
        seen.add(name)
        label, text = _GATE_EXPLAINERS.get(
            name,
            (name.upper(), f"{name} — Qiskit gate on this circuit"),
        )
        rows.append({"name": name, "label": label, "explainer": text})
    return rows
