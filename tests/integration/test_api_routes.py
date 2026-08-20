"""API tests for the core FastAPI routes (apps/api/routes/).

Covers experiments, results, bloch, and health/CORS. Hardware routes are
tested separately in test_hardware_api.py and are not duplicated here.

All tests use fastapi.testclient.TestClient against apps.api.main.app with
small, fast inputs (low qubit counts and shots). No hardware or IBM
credentials are required.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from apps.api.main import app
from qforge.engine.api import run as engine_run
from qforge.engine.models import ExperimentConfig

client = TestClient(app)


# ── Config builders ───────────────────────────────────────────────────


def _tiny_run_config(**overrides: object) -> dict[str, object]:
    """A fast, deterministic 2-qubit GHZ qasm config (no noise)."""
    cfg: dict[str, object] = {
        "num_qubits": 2,
        "state_type": "GHZ",
        "sim_mode": "qasm",
        "shots": 64,
        "rng_seed": 1,
        "visualization_type": "none",
    }
    cfg.update(overrides)
    return cfg


# ── GET /api/health ───────────────────────────────────────────────────


def test_health_ok() -> None:
    """Health check returns 200 with status ok."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_cors_headers_present() -> None:
    """CORS middleware echoes an allowed origin on a cross-origin request."""
    resp = client.get(
        "/api/health",
        headers={"Origin": "http://localhost:8081"},
    )
    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:8081"


# ── GET /api/experiments ──────────────────────────────────────────────


def test_list_experiments() -> None:
    """Registry listing returns name/description dicts including known entries."""
    resp = client.get("/api/experiments")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert body, "registry should not be empty"
    for entry in body:
        assert set(entry.keys()) == {"name", "description"}
        assert isinstance(entry["name"], str)
        assert isinstance(entry["description"], str)
    names = {e["name"] for e in body}
    assert "bell_state" in names
    assert "06_ghz_states" in names


# ── GET /api/experiments/config-schema ────────────────────────────────


def test_config_schema() -> None:
    """Config schema is a JSON schema dict exposing core ExperimentConfig fields."""
    resp = client.get("/api/experiments/config-schema")
    assert resp.status_code == 200
    schema = resp.json()
    assert isinstance(schema, dict)
    assert "properties" in schema
    props = schema["properties"]
    assert "num_qubits" in props
    assert "state_type" in props
    assert "shots" in props


# ── GET /api/experiments/{name}/config ────────────────────────────────


def test_default_config_known_experiment() -> None:
    """A registered experiment returns a valid default ExperimentConfig dict."""
    resp = client.get("/api/experiments/bell_state/config")
    assert resp.status_code == 200
    cfg = resp.json()
    assert isinstance(cfg, dict)
    # exclude_none is applied, but core fields are always present
    assert "num_qubits" in cfg
    assert "state_type" in cfg
    # The returned config round-trips back through the model
    ExperimentConfig(**cfg)


def test_default_config_unknown_experiment_404() -> None:
    """An unknown experiment name returns 404 with a detail message."""
    resp = client.get("/api/experiments/no_such_experiment_xyz/config")
    assert resp.status_code == 404
    assert "detail" in resp.json()


# ── POST /api/experiments/preview ─────────────────────────────────────


def test_preview_circuit() -> None:
    """Preview returns structured circuit, ASCII diagram, and stats."""
    resp = client.post(
        "/api/experiments/preview",
        json={"num_qubits": 2, "state_type": "GHZ"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert set(body.keys()) == {"circuit", "diagram", "stats"}

    circuit = body["circuit"]
    assert circuit["numQubits"] == 2
    assert isinstance(circuit["moments"], list)

    stats = body["stats"]
    assert stats["num_qubits"] == 2
    assert stats["num_gates"] >= 1
    assert stats["depth"] >= 1

    assert isinstance(body["diagram"], str) and body["diagram"]


# ── POST /api/experiments/run ─────────────────────────────────────────


def test_run_experiment() -> None:
    """A tiny qasm run returns a full, internally consistent result dict."""
    resp = client.post("/api/experiments/run", json=_tiny_run_config())
    assert resp.status_code == 200
    body = resp.json()

    assert body["status"] == "completed"
    assert isinstance(body.get("config_hash"), str) and body["config_hash"]
    assert "provenance" in body

    meas = body["analysis"]["measurement_results"]
    assert meas["total_shots"] == 64
    assert sum(meas["raw_counts"].values()) == 64
    # canonical bitstrings are width-2
    assert all(len(bs) == 2 for bs in meas["raw_counts"])


def test_run_experiment_with_metrics_profile() -> None:
    """Requesting a metrics profile populates the metrics bundle."""
    resp = client.post(
        "/api/experiments/run",
        json=_tiny_run_config(metrics="decoherence"),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["metrics_bundle"] is not None
    assert body["metrics_bundle"]["metrics"]


# ── POST /api/experiments/sweep ───────────────────────────────────────


def test_run_sweep() -> None:
    """A tiny 2-point sweep returns one result dict per combination."""
    manifest = {
        "base_config": _tiny_run_config(),
        "parameter_ranges": {"num_qubits": [2, 3]},
    }
    resp = client.post("/api/experiments/sweep", json=manifest)
    assert resp.status_code == 200
    results = resp.json()
    assert isinstance(results, list)
    assert len(results) == 2
    qubit_counts = sorted(r["analysis"]["measurement_results"]["total_shots"] for r in results)
    # both ran with shots=64
    assert qubit_counts == [64, 64]
    for r in results:
        assert r["status"] == "completed"


# ── GET /api/results ──────────────────────────────────────────────────


def test_list_results_returns_list() -> None:
    """Result listing always returns a list (possibly empty)."""
    resp = client.get("/api/results")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_result_missing_404() -> None:
    """Requesting a non-existent result file returns 404."""
    resp = client.get("/api/results/definitely_missing_result.json")
    assert resp.status_code == 404
    assert "detail" in resp.json()


def test_results_roundtrip(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """A stored result file is listed and retrievable by filename."""
    import apps.api.routes.results as results_route

    result_dict = engine_run(ExperimentConfig(**_tiny_run_config())).model_dump()
    fname = "roundtrip.json"
    (tmp_path / fname).write_text(json.dumps(result_dict))
    monkeypatch.setattr(results_route, "RESULTS_DIR", tmp_path)

    listing = client.get("/api/results")
    assert listing.status_code == 200
    assert any(e["filename"] == fname for e in listing.json())

    fetched = client.get(f"/api/results/{fname}")
    assert fetched.status_code == 200
    assert fetched.json()["status"] == "completed"


# ── GET /api/bloch/{filename} ─────────────────────────────────────────


def test_get_bloch_missing_404() -> None:
    """Requesting Bloch data for a non-existent file returns 404."""
    resp = client.get("/api/bloch/definitely_missing_result.json")
    assert resp.status_code == 404
    assert "detail" in resp.json()


def test_get_bloch_from_stored_result(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """A stored density-matrix result yields Bloch visualization data."""
    import apps.api.routes.bloch as bloch_route

    cfg = _tiny_run_config(
        sim_mode="density_matrix",
        noise_enabled=True,
        noise_type="depolarizing",
        error_rate=0.1,
    )
    result_dict = engine_run(ExperimentConfig(**cfg)).model_dump()
    fname = "bloch_src.json"
    (tmp_path / fname).write_text(json.dumps(result_dict))
    monkeypatch.setattr(bloch_route, "RESULTS_DIR", tmp_path)

    resp = client.get(f"/api/bloch/{fname}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["num_qubits"] == 2
    assert len(body["qubits"]) == 2
    assert "mi_matrix" in body


# ── POST /api/bloch/sweep ─────────────────────────────────────────────


def test_bloch_sweep() -> None:
    """A tiny error-rate sweep returns one Bloch snapshot per rate."""
    req = {
        "state_type": "GHZ",
        "num_qubits": 2,
        "noise_type": "depolarizing",
        "error_rates": [0.0, 0.1],
        "sim_mode": "density_matrix",
        "shots": 128,
        "rng_seed": 1,
    }
    resp = client.post("/api/bloch/sweep", json=req)
    assert resp.status_code == 200
    body = resp.json()
    assert body["state_type"] == "GHZ"
    assert body["num_qubits"] == 2
    assert body["error_rates"] == [0.0, 0.1]

    snapshots = body["snapshots"]
    assert len(snapshots) == 2
    assert [s["error_rate"] for s in snapshots] == [0.0, 0.1]
    for snap in snapshots:
        # density_matrix mode yields full Bloch info (not an error snapshot)
        assert "error" not in snap
        assert snap["num_qubits"] == 2
        assert len(snap["qubits"]) == 2


# ── Validation (Pydantic -> 422) ──────────────────────────────────────


def test_run_invalid_num_qubits_422() -> None:
    """num_qubits=0 violates the ge=1 constraint -> 422."""
    resp = client.post(
        "/api/experiments/run",
        json={"num_qubits": 0, "state_type": "GHZ"},
    )
    assert resp.status_code == 422


def test_preview_invalid_state_type_422() -> None:
    """An unknown state_type fails Literal validation -> 422."""
    resp = client.post(
        "/api/experiments/preview",
        json={"num_qubits": 2, "state_type": "NOT_A_STATE"},
    )
    assert resp.status_code == 422


def test_run_extra_field_rejected_422() -> None:
    """ExperimentConfig forbids extra fields -> 422 on unknown keys."""
    resp = client.post(
        "/api/experiments/run",
        json=_tiny_run_config(bogus_field="x"),
    )
    assert resp.status_code == 422


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__, "-v"])
