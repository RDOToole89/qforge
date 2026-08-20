"""Scaling Ladder — how do distribution metrics change with system size?

Runs the same entangled state at increasing qubit counts and tracks how
the Structure Score and related metrics of the measured distribution
change: do they increase, decrease, or stay constant?

Compares GHZ (ideal support on 2 outcomes regardless of N) against W
(ideal support on N single-excitation outcomes), which give the ladder
two different shapes to follow.

Usage:
    from qforge.experiments.decoherence import scaling_ladder

    # GHZ scaling
    results = scaling_ladder.run_ghz_ladder()

    # W scaling
    results = scaling_ladder.run_w_ladder()

    # Compare both
    ghz, w = scaling_ladder.run_comparison()
"""

from __future__ import annotations

from typing import Any

from qforge.engine.models import ExperimentConfig, ExperimentResult
from qforge.experiments.base import BaseExperiment


class ScalingLadder(BaseExperiment):
    """Test how decoherence structure scales with qubit count.

    Runs the same state at 2, 3, 4, 5, 6 qubits (and optionally 8)
    to observe how Structure Score and Total Correlation evolve.
    """

    name = "scaling_ladder"
    description = "Test decoherence structure scaling from 2 to 6+ qubits"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        return ExperimentConfig(
            num_qubits=6,
            state_type="GHZ",
            noise_enabled=True,
            noise_type="amplitude_damping",
            error_rate=0.1,
            shots=8192,
            metrics=[
                "structure_score",
                "entanglement_error_correlation",
                "concentration_index",
                "total_correlation",
            ],
            experiment_type="decoherence",
            visualization_type="all",
        )

    def run_ghz_ladder(
        self,
        qubit_range: list[int] | None = None,
        **overrides: Any,
    ) -> list[ExperimentResult]:
        """Run GHZ scaling ladder."""
        qubits = qubit_range or [2, 3, 4, 5, 6]
        return self.sweep(
            parameter_ranges={"num_qubits": qubits},
            state_type="GHZ",
            **overrides,
        )

    def run_w_ladder(
        self,
        qubit_range: list[int] | None = None,
        **overrides: Any,
    ) -> list[ExperimentResult]:
        """Run W state scaling ladder."""
        qubits = qubit_range or [2, 3, 4, 5, 6]
        return self.sweep(
            parameter_ranges={"num_qubits": qubits},
            state_type="W",
            **overrides,
        )

    def run_comparison(
        self,
        qubit_range: list[int] | None = None,
        **overrides: Any,
    ) -> tuple[list[ExperimentResult], list[ExperimentResult]]:
        """Run both GHZ and W ladders for direct comparison."""
        ghz = self.run_ghz_ladder(qubit_range, **overrides)
        w = self.run_w_ladder(qubit_range, **overrides)
        return ghz, w


scaling_ladder = ScalingLadder()
