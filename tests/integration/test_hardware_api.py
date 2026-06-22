"""API tests for the hardware feasibility endpoints.

No IBM credentials required: the IBM service and backend resolution are
monkeypatched so the routes can be exercised fully offline.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)


class FakeStatus:
    def __init__(self, operational: bool = True) -> None:
        self.operational = operational


class FakeBackend:
    """Minimal fake backend exposing the attrs the validator reads."""

    def __init__(
        self,
        name: str = "ibm_fake",
        num_qubits: int = 27,
        max_shots: int = 100_000,
        operational: bool = True,
    ) -> None:
        self.name = name
        self.num_qubits = num_qubits
        self.max_shots = max_shots
        self.operation_names = ["cx", "id", "rz", "sx", "x", "measure"]
        self.simulator = False
        self._operational = operational

    def status(self) -> FakeStatus:
        return FakeStatus(self._operational)


# ── GET /api/hardware/backends ────────────────────────────────────────


def test_backends_no_credentials(monkeypatch):
    """Service construction failure -> graceful available:false, HTTP 200."""

    class FakeService:
        def __init__(self) -> None:
            raise RuntimeError("no credentials saved")

    import qiskit_ibm_runtime

    monkeypatch.setattr(qiskit_ibm_runtime, "QiskitRuntimeService", FakeService)

    resp = client.get("/api/hardware/backends")
    assert resp.status_code == 200
    body = resp.json()
    assert body["available"] is False
    assert body["backends"] == []
    assert "reason" in body


def test_backends_populated(monkeypatch):
    """A working service returns capability dicts for each backend."""

    class FakeService:
        def __init__(self) -> None:
            pass

        def backends(self, operational=True, simulator=False):
            return [FakeBackend(name="ibm_a", num_qubits=5), FakeBackend(name="ibm_b")]

    import qiskit_ibm_runtime

    monkeypatch.setattr(qiskit_ibm_runtime, "QiskitRuntimeService", FakeService)

    resp = client.get("/api/hardware/backends")
    assert resp.status_code == 200
    body = resp.json()
    assert body["available"] is True
    names = {b["name"] for b in body["backends"]}
    assert names == {"ibm_a", "ibm_b"}
    assert all("num_qubits" in b for b in body["backends"])


# ── POST /api/hardware/validate ───────────────────────────────────────


def _config(num_qubits: int = 3, shots: int = 1024) -> dict[str, object]:
    return {
        "num_qubits": num_qubits,
        "state_type": "GHZ",
        "sim_mode": "hardware",
        "shots": shots,
        "visualization_type": "none",
    }


def test_validate_no_credentials(monkeypatch):
    """resolve_backend failing -> graceful available:false, HTTP 200."""
    import src.engine.execution.hardware as hw

    def _boom(*args, **kwargs):
        raise RuntimeError("Failed to connect to IBM Quantum.")

    monkeypatch.setattr(hw, "resolve_backend", _boom)

    resp = client.post("/api/hardware/validate", json=_config())
    assert resp.status_code == 200
    body = resp.json()
    assert body["available"] is False
    assert "reason" in body


def test_validate_feasible(monkeypatch):
    """A fitting config on a big backend is feasible with no violations."""
    import src.engine.execution.hardware as hw

    monkeypatch.setattr(
        hw, "resolve_backend", lambda *a, **k: FakeBackend(name="ibm_big", num_qubits=27)
    )

    resp = client.post("/api/hardware/validate", json=_config(num_qubits=3))
    assert resp.status_code == 200
    body = resp.json()
    assert body["available"] is True
    assert body["feasible"] is True
    assert body["violations"] == []
    assert body["backend_name"] == "ibm_big"


def test_validate_oversized(monkeypatch):
    """A circuit larger than the backend is infeasible with a clear message."""
    import src.engine.execution.hardware as hw

    monkeypatch.setattr(
        hw, "resolve_backend", lambda *a, **k: FakeBackend(name="ibm_small", num_qubits=5)
    )

    resp = client.post("/api/hardware/validate", json=_config(num_qubits=10))
    assert resp.status_code == 200
    body = resp.json()
    assert body["available"] is True
    assert body["feasible"] is False
    assert any("ibm_small" in v for v in body["violations"])


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__, "-v"])
