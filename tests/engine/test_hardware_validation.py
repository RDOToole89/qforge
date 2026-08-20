"""Unit tests for dynamic hardware feasibility validation.

No IBM credentials required: everything runs against small fake backend
objects that mimic the bits of the Qiskit backend API we touch.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from qforge.engine.execution.hardware_validation import (
    HardwareFeasibility,
    extract_backend_capabilities,
    validate_circuit_for_backend,
    validate_hardware_feasibility,
)


class FakeStatus:
    """Mimics backend.status()."""

    def __init__(self, operational: bool = True) -> None:
        self.operational = operational


class FakeBackend:
    """Minimal BackendV2-style fake exposing the attrs we read."""

    def __init__(
        self,
        name: str = "fake_backend",
        num_qubits: int = 5,
        max_shots: int = 100_000,
        operation_names: list[str] | None = None,
        operational: bool = True,
        simulator: bool = False,
    ) -> None:
        self.name = name
        self.num_qubits = num_qubits
        self.max_shots = max_shots
        self.operation_names = operation_names or ["cx", "id", "rz", "sx", "x", "measure"]
        self.simulator = simulator
        self._operational = operational

    def status(self) -> FakeStatus:
        return FakeStatus(self._operational)


def _caps(**overrides: object) -> dict[str, object]:
    """Build a capabilities dict with sensible defaults."""
    base: dict[str, object] = {
        "name": "ibm_x",
        "num_qubits": 5,
        "max_shots": 100_000,
        "basis_gates": ["cx", "id", "rz", "sx", "x"],
        "operational": True,
        "simulator": False,
    }
    base.update(overrides)
    return base


# ── extract_backend_capabilities ──────────────────────────────────────


def test_extract_capabilities_maps_fake_backend():
    backend = FakeBackend(name="ibm_fake", num_qubits=7, max_shots=4096)
    caps = extract_backend_capabilities(backend)

    assert caps["name"] == "ibm_fake"
    assert caps["num_qubits"] == 7
    assert caps["max_shots"] == 4096
    assert caps["operational"] is True
    assert caps["simulator"] is False
    assert "cx" in caps["basis_gates"]


def test_extract_capabilities_tolerates_missing_attrs():
    # A near-empty object: nothing but a name.
    backend = SimpleNamespace(name="bare")
    caps = extract_backend_capabilities(backend)

    assert caps["name"] == "bare"
    assert caps["num_qubits"] is None
    assert caps["max_shots"] is None
    assert caps["basis_gates"] == []
    # Defaults: assume operational unless told otherwise, not a simulator.
    assert caps["operational"] is True
    assert caps["simulator"] is False


def test_extract_capabilities_backendv1_style_via_configuration():
    config = SimpleNamespace(
        backend_name="ibm_v1",
        n_qubits=27,
        max_shots=8192,
        basis_gates=["cx", "u1", "u2", "u3"],
        simulator=False,
    )
    backend = SimpleNamespace(
        configuration=lambda: config,
        status=lambda: FakeStatus(operational=True),
    )
    caps = extract_backend_capabilities(backend)

    assert caps["name"] == "ibm_v1"
    assert caps["num_qubits"] == 27
    assert caps["max_shots"] == 8192
    assert caps["basis_gates"] == ["cx", "u1", "u2", "u3"]


# ── validate_hardware_feasibility: HARD violations ────────────────────


def test_too_many_qubits_is_infeasible():
    result = validate_hardware_feasibility(
        num_qubits=7, shots=1024, capabilities=_caps(name="ibm_x", num_qubits=5)
    )
    assert result.feasible is False
    assert any("7 qubits" in v and "ibm_x" in v and "5" in v for v in result.violations)


def test_shots_over_max_is_infeasible():
    result = validate_hardware_feasibility(
        num_qubits=3, shots=200_000, capabilities=_caps(max_shots=100_000)
    )
    assert result.feasible is False
    assert any("200000" in v and "100000" in v for v in result.violations)


def test_non_operational_backend_is_infeasible():
    result = validate_hardware_feasibility(
        num_qubits=3, shots=1024, capabilities=_caps(operational=False)
    )
    assert result.feasible is False
    assert any("not operational" in v for v in result.violations)


def test_multiple_violations_accumulate():
    result = validate_hardware_feasibility(
        num_qubits=9,
        shots=999_999,
        capabilities=_caps(num_qubits=5, max_shots=100_000, operational=False),
    )
    assert result.feasible is False
    assert len(result.violations) == 3


# ── validate_hardware_feasibility: feasible / SOFT warnings ────────────


def test_fitting_job_is_feasible_with_no_violations():
    result = validate_hardware_feasibility(
        num_qubits=3, shots=1024, capabilities=_caps(num_qubits=5)
    )
    assert isinstance(result, HardwareFeasibility)
    assert result.feasible is True
    assert result.violations == []
    assert result.backend_name == "ibm_x"


def test_unknown_gate_is_warning_not_violation():
    result = validate_hardware_feasibility(
        num_qubits=3,
        shots=1024,
        capabilities=_caps(basis_gates=["cx", "rz", "sx", "x"]),
        gate_names=["h", "cx", "measure"],
    )
    assert result.feasible is True
    assert result.violations == []
    assert any("h" in w for w in result.warnings)


def test_low_shots_is_warning_not_violation():
    result = validate_hardware_feasibility(num_qubits=3, shots=10, capabilities=_caps())
    assert result.feasible is True
    assert any("noisy" in w or "statistically" in w for w in result.warnings)


def test_known_gates_produce_no_gate_warning():
    result = validate_hardware_feasibility(
        num_qubits=2,
        shots=1024,
        capabilities=_caps(basis_gates=["cx", "rz", "sx", "x"]),
        gate_names=["cx", "rz", "measure", "barrier"],
    )
    assert result.feasible is True
    assert all("basis set" not in w for w in result.warnings)


def test_unknown_max_shots_skips_shot_check():
    result = validate_hardware_feasibility(
        num_qubits=3, shots=10_000_000, capabilities=_caps(max_shots=None)
    )
    assert result.feasible is True


# ── validate_circuit_for_backend ──────────────────────────────────────


def test_validate_circuit_for_backend_oversized():
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(7)
    qc.h(0)
    qc.measure_all()
    backend = FakeBackend(name="ibm_small", num_qubits=5)

    result = validate_circuit_for_backend(qc, backend, shots=1024)
    assert result.feasible is False
    assert any("ibm_small" in v for v in result.violations)


def test_validate_circuit_for_backend_fitting():
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(3)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.measure_all()
    backend = FakeBackend(name="ibm_big", num_qubits=27)

    result = validate_circuit_for_backend(qc, backend, shots=1024)
    assert result.feasible is True
    assert result.violations == []


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__, "-v"])
