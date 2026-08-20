"""End-to-end tests for the engine ``run()`` orchestration seam.

The other integration tests exercise the analysis pipeline directly. These run a
real experiment through the full engine path -- config -> circuit build -> noise
-> execution -> counts canonicalization -> analysis -> metrics -> typed result --
and assert the whole ``ExperimentResult`` is internally consistent. This is the
seam the unit tests don't cover: if any stage silently corrupts the data (wrong
shot totals, broken probabilities, missing metrics, wrong fidelity), it shows up
here.
"""

from __future__ import annotations

import math

import pytest

from qforge.engine.api import run
from qforge.engine.models import ExperimentConfig
from qforge.engine.models.results import ExperimentResult


def _ghz_qasm(**overrides):
    cfg = dict(
        num_qubits=3,
        state_type="GHZ",
        sim_mode="qasm",
        shots=1024,
        rng_seed=42,
        noise_enabled=True,
        noise_type="depolarizing",
        error_rate=0.05,
        metrics="decoherence",
    )
    cfg.update(overrides)
    return run(ExperimentConfig(**cfg))


def test_full_result_structure_and_internal_consistency():
    """A noisy GHZ qasm run yields a complete, internally consistent result."""
    result = _ghz_qasm()
    assert isinstance(result, ExperimentResult)
    assert result.status == "completed"
    assert isinstance(result.config_hash, str) and result.config_hash
    assert result.timestamp

    # --- measurement results: counts/probabilities must be self-consistent ---
    meas = result.analysis.measurement_results
    assert meas.total_shots == 1024
    assert sum(meas.raw_counts.values()) == 1024
    assert meas.unique_outcomes == len(meas.raw_counts)
    # every canonical bitstring has the right width
    assert all(len(bs) == 3 for bs in meas.raw_counts)
    # probabilities sum to 1 and equal count/total
    assert math.isclose(sum(meas.outcome_probabilities.values()), 1.0, abs_tol=1e-9)
    for bs, count in meas.raw_counts.items():
        assert math.isclose(meas.outcome_probabilities[bs], count / 1024, abs_tol=1e-9)

    # --- circuit statistics present and sane ---
    assert result.analysis.circuit_statistics is not None

    # --- metrics bundle: every entry is a well-formed metric ---
    bundle = result.metrics_bundle
    assert bundle is not None and bundle.metrics
    assert "structure_score" in bundle.metrics
    for name, entry in bundle.metrics.items():
        assert isinstance(entry.value, float) and math.isfinite(entry.value), name
        assert isinstance(entry.status, str) and entry.status
        if entry.ci95 is not None:
            assert len(entry.ci95) == 2
            assert entry.ci95[0] <= entry.ci95[1]

    # --- provenance carries reproducibility info ---
    assert result.provenance is not None
    assert result.provenance.rng_seed == 42
    assert result.provenance.software_versions


def test_statevector_ghz_is_exact():
    """Statevector mode yields the exact GHZ state (fidelity 1) on |000>+|111>."""
    result = run(
        ExperimentConfig(
            num_qubits=3, state_type="GHZ", sim_mode="statevector", shots=512, rng_seed=7
        )
    )
    meas = result.analysis.measurement_results
    assert meas.fidelity == pytest.approx(1.0, abs=1e-6)
    assert meas.statevector is not None and len(meas.statevector) == 8
    # exact GHZ collapses only onto all-zeros / all-ones
    assert set(meas.raw_counts) <= {"000", "111"}


def test_density_matrix_noise_degrades_fidelity():
    """Density-matrix mode with noise gives a mixed state with fidelity in (0, 1)."""
    result = run(
        ExperimentConfig(
            num_qubits=3,
            state_type="GHZ",
            sim_mode="density_matrix",
            noise_enabled=True,
            noise_type="depolarizing",
            error_rate=0.1,
            shots=512,
            rng_seed=1,
        )
    )
    meas = result.analysis.measurement_results
    assert meas.fidelity is not None
    assert 0.0 < meas.fidelity < 1.0
    # density matrix is 2^n x 2^n
    assert meas.density_matrix is not None
    assert len(meas.density_matrix) == 8
    assert all(len(row) == 8 for row in meas.density_matrix)


def test_run_is_reproducible_with_seed():
    """Same config + rng_seed reproduces identical canonical counts end-to-end."""
    a = _ghz_qasm(rng_seed=123)
    b = _ghz_qasm(rng_seed=123)
    assert a.analysis.measurement_results.raw_counts == b.analysis.measurement_results.raw_counts


def test_ghz_structure_dominant_outcomes():
    """A real GHZ run concentrates probability on the all-0 and all-1 strings."""
    meas = _ghz_qasm(error_rate=0.02).analysis.measurement_results
    top_two = sorted(meas.raw_counts, key=meas.raw_counts.get, reverse=True)[:2]
    assert set(top_two) == {"000", "111"}


def test_no_metrics_bundle_when_not_requested():
    """With metrics disabled the orchestration still completes, bundle is None."""
    result = run(
        ExperimentConfig(
            num_qubits=2, state_type="GHZ", sim_mode="qasm", shots=256, rng_seed=5, metrics=None
        )
    )
    assert result.status == "completed"
    assert result.metrics_bundle is None
    assert sum(result.analysis.measurement_results.raw_counts.values()) == 256
