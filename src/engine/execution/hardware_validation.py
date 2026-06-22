"""Dynamic hardware-job feasibility checks.

Static config limits (shots <= 100k, qubits 1-20, etc.) live in
``ExperimentConfig``. This module covers the *dynamic* gap: validating a
concrete job against the *actual* capabilities of the chosen IBM Quantum
backend before anything is submitted.

The goal is simple: never submit an impossible job to real hardware.
A circuit that needs more qubits than the device has, more shots than the
device allows, or a non-operational backend should fail fast with a clear,
human-readable explanation — not after a remote round trip.

Everything here is defensive: Qiskit backend objects vary across versions
(``BackendV1`` vs ``BackendV2``, runtime backends, fakes), so capability
extraction tolerates missing attributes and falls back to sensible defaults.
This also makes the layer fully testable offline with mock backend objects.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# Shots below this are allowed but statistically near-useless on hardware.
_LOW_SHOTS_WARNING_THRESHOLD = 100


class HardwareFeasibilityError(RuntimeError):
    """Raised when a job cannot run on the chosen hardware backend."""


@dataclass
class HardwareFeasibility:
    """Outcome of a dynamic hardware feasibility check.

    Attributes:
        feasible: True if the job can be submitted (no hard violations).
        violations: Human-readable reasons the job is impossible. Non-empty
            implies ``feasible is False``.
        warnings: Non-fatal advisories (job still runs).
        backend_name: Name of the evaluated backend, if known.
        capabilities: The capability dict the decision was based on.
    """

    feasible: bool
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    backend_name: str | None = None
    capabilities: dict[str, Any] = field(default_factory=dict)


def _safe_call(obj: Any, *names: str) -> Any:
    """Return the first attribute/method result that resolves without error.

    Each name is tried in order. If the resolved attribute is callable it is
    called with no arguments. Any exception (missing attr, call failure) moves
    on to the next name. Returns ``None`` if nothing resolves.
    """
    for name in names:
        try:
            value = getattr(obj, name)
        except Exception:
            continue
        try:
            return value() if callable(value) else value
        except Exception:
            continue
    return None


def extract_backend_capabilities(backend: Any) -> dict[str, Any]:
    """Defensively extract capabilities from a Qiskit backend object.

    Handles ``BackendV1``/``BackendV2``, runtime backends, and mock/fake
    objects. Missing data is filled with ``None`` (unknown) or sensible
    defaults rather than raising.

    Returns:
        Dict with keys: ``name``, ``num_qubits``, ``max_shots``,
        ``basis_gates`` (list[str]), ``operational`` (bool),
        ``simulator`` (bool).
    """
    config = _safe_call(backend, "configuration")
    status = _safe_call(backend, "status")

    # ── name ──────────────────────────────────────────────────────────
    name = _safe_call(backend, "name")
    if name is None and config is not None:
        name = getattr(config, "backend_name", None)
    name = str(name) if name is not None else None

    # ── num_qubits ────────────────────────────────────────────────────
    num_qubits = _safe_call(backend, "num_qubits")
    if num_qubits is None and config is not None:
        num_qubits = getattr(config, "n_qubits", None) or getattr(config, "num_qubits", None)
    try:
        num_qubits = int(num_qubits) if num_qubits is not None else None
    except (TypeError, ValueError):
        num_qubits = None

    # ── max_shots ─────────────────────────────────────────────────────
    max_shots = _safe_call(backend, "max_shots")
    if max_shots is None and config is not None:
        max_shots = getattr(config, "max_shots", None)
    try:
        max_shots = int(max_shots) if max_shots is not None else None
    except (TypeError, ValueError):
        max_shots = None

    # ── basis gates ───────────────────────────────────────────────────
    basis_gates = _extract_basis_gates(backend, config)

    # ── operational ───────────────────────────────────────────────────
    operational = getattr(status, "operational", None) if status is not None else None
    if operational is None:
        operational = _safe_call(backend, "operational")
    operational = True if operational is None else bool(operational)

    # ── simulator ─────────────────────────────────────────────────────
    simulator = _safe_call(backend, "simulator")
    if simulator is None and config is not None:
        simulator = getattr(config, "simulator", None)
    simulator = False if simulator is None else bool(simulator)

    return {
        "name": name,
        "num_qubits": num_qubits,
        "max_shots": max_shots,
        "basis_gates": basis_gates,
        "operational": operational,
        "simulator": simulator,
    }


def _extract_basis_gates(backend: Any, config: Any) -> list[str]:
    """Pull the supported gate set from a backend, tolerating API variance."""
    # BackendV2: operation_names / target
    raw = _safe_call(backend, "operation_names")
    if raw is None:
        target = _safe_call(backend, "target")
        if target is not None:
            try:
                raw = list(target.operation_names)
            except Exception:
                raw = None
    # BackendV1: configuration().basis_gates
    if raw is None and config is not None:
        raw = getattr(config, "basis_gates", None)
    if raw is None:
        return []
    try:
        return [str(g).lower() for g in raw]
    except TypeError:
        return []


def validate_hardware_feasibility(
    num_qubits: int,
    shots: int,
    capabilities: dict[str, Any],
    gate_names: list[str] | None = None,
) -> HardwareFeasibility:
    """Validate a job against extracted backend capabilities.

    Hard violations (``feasible=False``):
        * circuit needs more qubits than the backend provides;
        * shots exceed the backend's ``max_shots`` (when known);
        * the backend is not operational.

    Soft warnings (still feasible):
        * gates not in the backend basis set (they will be transpiled);
        * very low shot count (poor statistics).

    Args:
        num_qubits: Qubits the circuit requires.
        shots: Requested measurement shots.
        capabilities: Output of :func:`extract_backend_capabilities`.
        gate_names: Optional circuit gate names to check against the basis set.

    Returns:
        A :class:`HardwareFeasibility` describing the decision.
    """
    violations: list[str] = []
    warnings: list[str] = []

    backend_name = capabilities.get("name")
    label = backend_name or "unknown backend"

    # ── HARD: qubit capacity ──────────────────────────────────────────
    backend_qubits = capabilities.get("num_qubits")
    if backend_qubits is not None and num_qubits > backend_qubits:
        violations.append(
            f"Circuit needs {num_qubits} qubits but backend '{label}' has {backend_qubits}."
        )

    # ── HARD: shot ceiling ────────────────────────────────────────────
    max_shots = capabilities.get("max_shots")
    if max_shots is not None and shots > max_shots:
        violations.append(
            f"Requested {shots} shots but backend '{label}' allows at most {max_shots}."
        )

    # ── HARD: operational status ──────────────────────────────────────
    if capabilities.get("operational") is False:
        violations.append(f"Backend '{label}' is not operational (offline or in maintenance).")

    # ── SOFT: unsupported gates (transpiler will rewrite them) ─────────
    basis_gates = capabilities.get("basis_gates") or []
    if gate_names and basis_gates:
        basis_set = {g.lower() for g in basis_gates}
        # Gates that are always handled separately by transpilation / structure.
        ignorable = {"measure", "barrier", "delay", "reset", "snapshot"}
        unsupported = sorted({g.lower() for g in gate_names} - basis_set - ignorable)
        if unsupported:
            warnings.append(
                f"Gate(s) {unsupported} are not in backend '{label}' basis set "
                f"{sorted(basis_set)}; they will be transpiled to native gates."
            )

    # ── SOFT: poor statistics ─────────────────────────────────────────
    if shots < _LOW_SHOTS_WARNING_THRESHOLD:
        warnings.append(
            f"Only {shots} shots requested; results may be statistically noisy "
            f"(< {_LOW_SHOTS_WARNING_THRESHOLD})."
        )

    feasible = len(violations) == 0
    return HardwareFeasibility(
        feasible=feasible,
        violations=violations,
        warnings=warnings,
        backend_name=backend_name,
        capabilities=capabilities,
    )


def validate_circuit_for_backend(
    circuit: Any,
    backend: Any,
    shots: int,
) -> HardwareFeasibility:
    """Convenience wrapper: extract caps + circuit info, then validate.

    Args:
        circuit: A Qiskit ``QuantumCircuit``.
        backend: A Qiskit backend object.
        shots: Requested measurement shots.

    Returns:
        A :class:`HardwareFeasibility` for ``circuit`` on ``backend``.
    """
    capabilities = extract_backend_capabilities(backend)

    try:
        num_qubits = int(circuit.num_qubits)
    except Exception:
        num_qubits = 0

    gate_names = _circuit_gate_names(circuit)

    return validate_hardware_feasibility(
        num_qubits=num_qubits,
        shots=shots,
        capabilities=capabilities,
        gate_names=gate_names,
    )


def _circuit_gate_names(circuit: Any) -> list[str]:
    """Extract operation names from a circuit, tolerating Qiskit versions."""
    try:
        return [inst.operation.name for inst in circuit.data]
    except Exception:
        pass
    try:
        return [inst[0].name for inst in circuit.data]
    except Exception:
        return []
