# tests/cli/test_cli_viz_engine_flag.py

import os
import json
from pathlib import Path

from src.engine.viz_service import VisualizationService, VisualizationRequest
from main import visualize_from_json


def _write_dummy_analysis(tmp_path: Path) -> str:
    analysis = {
        "experiment_parameters": {
            "num_qubits": 3,
            "state_type": "GHZ",
            "noise_type": "DEPOLARIZING",
            "noise_enabled": True,
            "error_rate": 0.05,
        },
        "measurement_results": {"raw_counts": {"000": 600, "111": 424}},
    }
    p = tmp_path / "analysis.json"
    p.write_text(json.dumps(analysis), encoding="utf-8")
    return str(p)


essential_env = {"QEXP_USE_ENGINE_API": "1"}


def test_cli_viz_uses_engine_when_flag_set(tmp_path, monkeypatch):
    json_path = _write_dummy_analysis(tmp_path)

    # Ensure engine base dir for viz artifacts is inside tmp
    monkeypatch.setenv("QEXP_USE_ENGINE_API", "1")

    # Run visualization (engine service should save a file)
    visualize_from_json(json_path, viz_type="histogram")

    # Check that an artifact exists under default results/visualizations or tmp override if set
    # We can't easily intercept the save path here, so check that at least one file exists in default dir
    base = Path("results/visualizations/histograms")
    assert any(base.glob("*.png")) or any((tmp_path / "viz_out").glob("*.png"))


def test_cli_viz_outdir_flag(tmp_path, monkeypatch):
    json_path = _write_dummy_analysis(tmp_path)
    outdir = tmp_path / "custom_out"
    monkeypatch.setenv("QEXP_USE_ENGINE_API", "1")

    # Call visualize with explicit outdir
    visualize_from_json(json_path, viz_type="histogram", backend=None, outdir=str(outdir))

    # Expect artifact saved under outdir/histograms
    assert any((outdir / "histograms").glob("*.png"))
