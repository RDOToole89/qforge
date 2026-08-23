"""Setuptools entry-point discovery for out-of-tree experiments."""

from __future__ import annotations

import pytest

from qforge.engine.models import ExperimentConfig
from qforge.experiments import (
    EXPERIMENT_ENTRY_POINT_GROUP,
    get_experiment,
    load_experiment_entry_points,
    register_experiment,
    unregister_experiment,
)
from qforge.experiments.base import BaseExperiment

INSTANCE_NAME = "ep_toy_instance"
CALLABLE_NAME = "ep_toy_callable"


class _Toy(BaseExperiment):
    """Minimal program used as an entry-point payload."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.description = "entry-point test experiment"

    def default_config(self) -> ExperimentConfig:
        return ExperimentConfig(
            num_qubits=1,
            state_type="SUPERPOSITION",
            shots=8,
            rng_seed=0,
            visualization_type="none",
        )


class _FakeEP:
    def __init__(self, name: str, obj: object) -> None:
        self.name = name
        self._obj = obj

    def load(self) -> object:
        return self._obj


class _FakeEntryPoints:
    def __init__(self, items: list[_FakeEP]) -> None:
        self._items = items

    def select(self, group: str) -> list[_FakeEP]:
        assert group == EXPERIMENT_ENTRY_POINT_GROUP
        return self._items


@pytest.fixture(autouse=True)
def _cleanup_registry() -> None:
    yield
    unregister_experiment(INSTANCE_NAME)
    unregister_experiment(CALLABLE_NAME)


def _patch_entries(monkeypatch: pytest.MonkeyPatch, items: list[_FakeEP]) -> None:
    monkeypatch.setattr(
        "qforge.experiments.entry_points",
        lambda: _FakeEntryPoints(items),
    )


def test_loads_instance(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_entries(monkeypatch, [_FakeEP("inst", _Toy(INSTANCE_NAME))])
    loaded = load_experiment_entry_points(force=True)
    assert loaded == 1
    assert get_experiment(INSTANCE_NAME).name == INSTANCE_NAME
    assert load_experiment_entry_points(force=False) == 0


def test_loads_callable(monkeypatch: pytest.MonkeyPatch) -> None:
    def _register() -> None:
        register_experiment(_Toy(CALLABLE_NAME))

    _patch_entries(monkeypatch, [_FakeEP("fn", _register)])
    assert load_experiment_entry_points(force=True) == 1
    assert get_experiment(CALLABLE_NAME).name == CALLABLE_NAME


def test_skips_bad_entry(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_entries(monkeypatch, [_FakeEP("bad", object())])
    assert load_experiment_entry_points(force=True) == 0


def test_skips_already_registered(monkeypatch: pytest.MonkeyPatch) -> None:
    original = _Toy(INSTANCE_NAME)
    register_experiment(original)
    replacement = _Toy(INSTANCE_NAME)
    _patch_entries(monkeypatch, [_FakeEP("dup", replacement)])
    assert load_experiment_entry_points(force=True) == 0
    assert get_experiment(INSTANCE_NAME) is original
