"""Deep Dive: GHZ Structure Metrics — quantifying distribution shape.

What you'll learn:
  - How GHZ states generalize Bell states to N qubits
  - What a concentrated error distribution looks like in measurement data
  - How Structure Score quantifies deviation from independent qubits

A GHZ state is (|000...0⟩ + |111...1⟩) / √2 — all qubits are
perfectly correlated. Its ideal distribution has just two peaks, and
under moderate noise the measured counts stay concentrated around them.

Try it:
    from src.experiments.basics.ghz_exploration import ghz_exploration

    # Run at different qubit counts to see how the metrics change
    for n in [2, 3, 4, 5, 6]:
        result = ghz_exploration.run({"num_qubits": n})
        ss = result.metrics_bundle.metrics["structure_score"].value
        print(f"{n} qubits: Structure Score = {ss:.3f}")

    # Compare with and without noise
    clean = ghz_exploration.run({"noise_enabled": False})
    noisy = ghz_exploration.run({"noise_enabled": True, "error_rate": 0.1})

CIRCUIT (GHZ-4):
  q0: ─H──●──●──●── M
  q1: ────X──┼──┼── M
  q2: ───────X──┼── M
  q3: ──────────X── M

  Runs with metrics="decoherence" to compute
  Structure Score, Total Correlation, and Concentration Index.

WHAT YOU'LL EXPLORE:
  - Structure Score: how far the error distribution is from independent qubits
  - Total Correlation: how much knowing one qubit tells you about the others
  - Concentration Index: how concentrated probability is in a few outcomes
  - How these metrics grow with qubit count

TRY IT:
    from src.experiments.basics.deep_dives.dd_ghz_structure_metrics import ghz_exploration

    # Single run with metrics
    result = ghz_exploration.run()

    # Scaling: 2 to 6 qubits
    results = ghz_exploration.run_scaling()
"""

from __future__ import annotations

from typing import Any

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


class GHZExploration(BaseExperiment):
    """Explore GHZ states and distribution-structure metrics.

    Start here to understand what Structure Score, Total Correlation,
    and Concentration Index measure.
    """

    name = "ghz_exploration"
    description = "Explore multi-qubit GHZ states and decoherence structure metrics"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        return ExperimentConfig(
            num_qubits=4,
            state_type="GHZ",
            noise_enabled=True,
            noise_type="depolarizing",
            error_rate=0.05,
            shots=4096,
            metrics="decoherence",
            visualization_type=["histogram", "metrics_summary"],
        )

    def run_scaling(
        self,
        qubit_range: list[int] | None = None,
        **overrides: Any,
    ) -> list[ExperimentResult]:
        """Run at multiple qubit counts to see how structure scales."""
        if qubit_range is None:
            qubit_range = [2, 3, 4, 5, 6]
        return self.sweep(parameter_ranges={"num_qubits": qubit_range}, **overrides)


ghz_exploration = GHZExploration()
