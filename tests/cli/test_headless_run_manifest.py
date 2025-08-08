import json
import os
from pathlib import Path
from main import run_sweep_from_manifest


def test_run_from_config(monkeypatch, tmp_path):
    cfg = {
        "preset": "ghz_structured_decoherence_ref",
        "shots": 64,
        "error_rate": 0.05,
    }
    p = tmp_path / "config.json"
    p.write_text(json.dumps(cfg))

    from main import run_from_config

    # Should not raise
    run_from_config(str(p))


def test_sweep_from_manifest(tmp_path):
    manifest = {
        "base_preset": "ghz_structured_decoherence_ref",
        "parameter_ranges": {"error_rate": [0.01, 0.05]},
        "runs_per_config": 1,
    }
    m = tmp_path / "manifest.json"
    m.write_text(json.dumps(manifest))

    # Should not raise
    run_sweep_from_manifest(str(m))


def test_engine_sweep_manifest_runs(tmp_path, monkeypatch):
    # Prepare a minimal manifest using an existing preset and small ranges
    manifest = {
        "base_preset": "ghz_basic",
        "parameter_ranges": {"error_rate": [0.01, 0.02]},
        "runs_per_config": 1,
        "rng_seed": 123,
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    # Use engine path
    monkeypatch.setenv("QEXP_USE_ENGINE_API", "1")

    # Run
    run_sweep_from_manifest(str(manifest_path))

    # Expect at least one results JSON saved under results/structured_decoherence
    results_dir = Path("results/structured_decoherence")
    assert results_dir.exists()
    assert any(results_dir.glob("*.json"))
