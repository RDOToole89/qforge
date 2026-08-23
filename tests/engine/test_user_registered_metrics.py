"""User-registered metrics and profiles without editing core specs."""

from __future__ import annotations

import pytest

from qforge import ExperimentConfig, run
from qforge.core.analysis.metrics import (
    MetricResult,
    register,
    register_profile,
    unregister,
    unregister_profile,
)

TOY_METRIC = "toy_constant_metric"
TOY_PROFILE = "toy_profile"


def test_experiment_type_is_a_free_label() -> None:
    cfg = ExperimentConfig(
        num_qubits=2,
        state_type="BELL",
        experiment_type="decoherence",
    )
    assert cfg.experiment_type == "decoherence"
    custom = ExperimentConfig(
        num_qubits=2,
        state_type="BELL",
        experiment_type="my_research_track",
    )
    assert custom.experiment_type == "my_research_track"


def test_user_metric_and_profile_via_run() -> None:
    """A metric defined outside core is selectable via metrics=profile."""

    @register(TOY_METRIC)
    def _toy_constant(**_kwargs: object) -> MetricResult:
        return MetricResult(
            value=0.42,
            ci95=(0.42, 0.42),
            status="validated",
            extras={"source": "user"},
        )

    register_profile(TOY_PROFILE, [TOY_METRIC])
    try:
        result = run(
            ExperimentConfig(
                num_qubits=2,
                state_type="BELL",
                shots=128,
                rng_seed=1,
                metrics=TOY_PROFILE,
                visualization_type="none",
            )
        )
        assert result.metrics_bundle is not None
        assert result.metrics_bundle.profile == TOY_PROFILE
        entry = result.metrics_bundle.metrics[TOY_METRIC]
        assert entry.value == pytest.approx(0.42)
        assert entry.status == "validated"
    finally:
        unregister(TOY_METRIC)
        unregister_profile(TOY_PROFILE)
