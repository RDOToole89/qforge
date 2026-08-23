"""User-registered experiment programs without editing the in-repo registry."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from qforge.cli import app, app_state
from qforge.engine.models import ExperimentConfig
from qforge.experiments import (
    get_experiment,
    list_experiments,
    register_experiment,
    unregister_experiment,
)
from qforge.experiments.base import BaseExperiment

TOY_NAME = "toy_plugin_experiment"

runner = CliRunner()


class ToyPluginExperiment(BaseExperiment):
    """Defined in tests/, not in src/qforge/experiments/."""

    name = TOY_NAME
    description = "Out-of-tree plugin experiment for registry tests"
    metrics_hint = "Asymmetry Index near 0: fair coin."

    def default_config(self) -> ExperimentConfig:
        """Return a cheap 1-qubit config."""
        return ExperimentConfig(
            num_qubits=1,
            state_type="SUPERPOSITION",
            shots=64,
            rng_seed=0,
            visualization_type="none",
            metrics=["asymmetry_index"],
        )


@pytest.fixture
def toy_experiment() -> ToyPluginExperiment:
    exp = ToyPluginExperiment()
    register_experiment(exp)
    try:
        yield exp
    finally:
        unregister_experiment(TOY_NAME)


@pytest.fixture
def _reset_cli_state() -> None:
    app_state.clear()
    yield
    app_state.clear()


def test_register_experiment_appears_in_list_and_run(
    toy_experiment: ToyPluginExperiment,
) -> None:
    names = [name for name, _description in list_experiments()]
    assert TOY_NAME in names
    got = get_experiment(TOY_NAME)
    assert got is toy_experiment
    result = got.run()
    assert result.status == "completed"
    assert result.metrics_bundle is not None
    assert "asymmetry_index" in result.metrics_bundle.metrics


def test_unregister_removes_plugin() -> None:
    register_experiment(ToyPluginExperiment())
    unregister_experiment(TOY_NAME)
    names = [name for name, _description in list_experiments()]
    assert TOY_NAME not in names
    with pytest.raises(KeyError, match=TOY_NAME):
        get_experiment(TOY_NAME)


def test_register_refuses_builtin_overwrite() -> None:
    with pytest.raises(KeyError, match="01_superposition"):
        register_experiment(ToyPluginExperiment(), name="01_superposition")


def test_register_replace_overwrites_plugin() -> None:
    first = ToyPluginExperiment()
    second = ToyPluginExperiment()
    register_experiment(first)
    try:
        register_experiment(second, replace=True)
        assert get_experiment(TOY_NAME) is second
    finally:
        unregister_experiment(TOY_NAME)


def test_register_rejects_non_program() -> None:
    with pytest.raises(TypeError, match="ExperimentProgram"):
        register_experiment(object())  # type: ignore[arg-type]


def test_register_rejects_empty_name() -> None:
    exp = ToyPluginExperiment()
    with pytest.raises(ValueError, match="non-empty"):
        register_experiment(exp, name="  ")


def test_cli_run_user_experiment(
    toy_experiment: ToyPluginExperiment,
    tmp_path: Path,
    _reset_cli_state: None,
) -> None:
    del toy_experiment
    result = runner.invoke(
        app,
        ["--results-dir", str(tmp_path), "run", TOY_NAME],
        catch_exceptions=False,
    )
    assert result.exit_code == 0, result.stdout
    assert "asymmetry_index" in result.stdout
    assert "fair coin" in result.stdout
