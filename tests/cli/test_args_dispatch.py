from __future__ import annotations

from src.cli.entrypoints.args import dispatch


def test_dispatch_help(capsys):
    code = dispatch(["--help"])
    assert code == 0


def test_dispatch_list(monkeypatch, capsys):
    # Not asserting output; just that it doesn't error
    code = dispatch(["--list"])
    assert code == 0


def test_dispatch_viz_flags(tmp_path, monkeypatch):
    data = {
        "experiment_parameters": {
            "state_type": "GHZ",
            "noise_type": "DEPOLARIZING",
            "noise_enabled": True,
            "num_qubits": 3,
        },
        "measurement_results": {"raw_counts": {"000": 512, "111": 512}},
    }
    p = tmp_path / "res.json"
    import json

    p.write_text(json.dumps(data))
    code = dispatch(
        [
            "--viz",
            str(p),
            "--type",
            "histogram",
            "--backend",
            "matplotlib",
            "--outdir",
            str(tmp_path),
        ]
    )
    assert code == 0


def test_dispatch_run_preset(monkeypatch):
    # Should route to headless run by preset
    code = dispatch(["run", "--preset", "ghz_basic"])
    assert code == 0


def test_dispatch_run_config(tmp_path):
    import json

    cfg = {
        "preset": "ghz_basic",
        "shots": 8,
        "error_rate": 0.01,
    }
    p = tmp_path / "cfg.json"
    p.write_text(json.dumps(cfg))
    code = dispatch(["run", "--config", str(p)])
    assert code == 0


def test_dispatch_sweep_manifest(tmp_path):
    import json

    manifest = {
        "base_preset": "ghz_basic",
        "parameter_ranges": {"error_rate": [0.01, 0.02]},
        "runs_per_config": 1,
    }
    m = tmp_path / "manifest.json"
    m.write_text(json.dumps(manifest))
    code = dispatch(["sweep", "--manifest", str(m)])
    assert code == 0
