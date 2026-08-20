"""CLI surface: run, sweep, artifact paths, results-dir."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from qforge import cli
from qforge.cli import _coerce_scalar, _parse_overrides, _parse_ranges, app

runner = CliRunner()


@pytest.fixture(autouse=True)
def _reset_cli_state() -> None:
    cli.app_state.clear()
    yield
    cli.app_state.clear()


def test_coerce_and_parse_helpers() -> None:
    assert _coerce_scalar("true") is True
    assert _coerce_scalar("3") == 3
    assert _coerce_scalar("0.05") == 0.05
    assert _coerce_scalar("GHZ") == "GHZ"
    assert _parse_overrides(["num_qubits=3", "noise_enabled=true"]) == {
        "num_qubits": 3,
        "noise_enabled": True,
    }
    assert _parse_ranges(["error_rate=0.01,0.05,0.1"]) == {"error_rate": [0.01, 0.05, 0.1]}
    assert _parse_ranges(["num_qubits=[2,3,4]"]) == {"num_qubits": [2, 3, 4]}


def test_run_prints_saved_histogram(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "--results-dir",
            str(tmp_path),
            "run",
            "01_superposition",
            "-s",
            "shots=64",
            "-s",
            "rng_seed=0",
        ],
        catch_exceptions=False,
    )
    assert result.exit_code == 0, result.stdout
    assert "Saved" in result.stdout
    assert "histogram" in result.stdout
    assert "analysis" in result.stdout
    pngs = list(tmp_path.rglob("histogram.png"))
    assert len(pngs) == 1


def test_sweep_error_rate_table(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "--results-dir",
            str(tmp_path),
            "sweep",
            "06_ghz_states",
            "-p",
            "error_rate=0.0,0.05",
            "-s",
            "shots=32",
            "-s",
            "noise_enabled=true",
            "-s",
            "noise_type=depolarizing",
            "-s",
            "metrics=quick",
            "-s",
            "visualization_type=none",
            "-s",
            "rng_seed=0",
        ],
        catch_exceptions=False,
    )
    assert result.exit_code == 0, result.stdout
    assert "2 run(s)" in result.stdout
    assert "error_rate" in result.stdout
    assert "structure_score" in result.stdout
    jsons = list(tmp_path.rglob("analysis.json"))
    assert len(jsons) == 2


def test_sweep_requires_param() -> None:
    result = runner.invoke(app, ["sweep", "01_superposition"])
    assert result.exit_code == 1
    assert "Sweep needs a range" in result.stdout


def test_unknown_experiment() -> None:
    result = runner.invoke(app, ["run", "not_a_real_experiment"])
    assert result.exit_code == 1
    assert "Unknown experiment" in result.stdout


def test_sweep_config_json(tmp_path: Path) -> None:
    manifest = {
        "base_config": {
            "num_qubits": 2,
            "state_type": "GHZ",
            "shots": 32,
            "noise_enabled": False,
            "rng_seed": 0,
            "visualization_type": "none",
        },
        "parameter_ranges": {"num_qubits": [2, 3]},
    }
    path = tmp_path / "sweep.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    out_dir = tmp_path / "out"
    result = runner.invoke(
        app,
        ["--results-dir", str(out_dir), "sweep-config", str(path)],
        catch_exceptions=False,
    )
    assert result.exit_code == 0, result.stdout
    assert "2 run(s)" in result.stdout
    assert len(list(out_dir.rglob("analysis.json"))) == 2
