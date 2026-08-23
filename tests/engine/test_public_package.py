"""Public package surface: ``from qforge import run`` and the CLI registry."""

from __future__ import annotations

import pytest

import qforge
from qforge import ExperimentConfig, get_experiment, list_experiments, run, sweep


def test_documented_imports_resolve() -> None:
    """The documented import ``from qforge import run`` resolves."""
    assert callable(run)
    assert callable(sweep)
    assert qforge.run is run


def test_statevector_bell_fidelity_is_one() -> None:
    result = run(
        ExperimentConfig(
            num_qubits=2,
            state_type="BELL",
            sim_mode="statevector",
            shots=256,
            rng_seed=0,
            noise_enabled=False,
        )
    )
    assert result.status == "completed"
    meas = result.analysis.measurement_results
    assert meas is not None
    assert meas.fidelity is not None
    assert abs(meas.fidelity - 1.0) < 1e-10


def test_lazy_experiment_registry() -> None:
    """get_experiment / list_experiments are public and include the teaching path."""
    names = [name for name, _description in list_experiments()]
    assert "01_superposition" in names
    assert "05_bell_states" in names
    exp = get_experiment("01_superposition")
    assert exp.name == "01_superposition"


def test_register_experiment_is_public() -> None:
    from qforge import register_experiment, unregister_experiment

    assert callable(register_experiment)
    assert callable(unregister_experiment)


def test_unknown_root_export_raises() -> None:
    with pytest.raises(AttributeError):
        qforge.__getattr__("not_a_public_export")


def test_package_version_is_nonempty() -> None:
    assert isinstance(qforge.__version__, str)
    assert len(qforge.__version__) > 0
