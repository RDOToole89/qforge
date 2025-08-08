import json
import os
from pathlib import Path


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

    from main import run_sweep_from_manifest

    # Should not raise
    run_sweep_from_manifest(str(m))
