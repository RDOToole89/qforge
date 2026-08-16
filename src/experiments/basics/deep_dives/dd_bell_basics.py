"""Deep Dive: Bell State with Noise — Watch correlations decay.

What you'll learn:
  - What a Bell state looks like in measurement data
  - Why entangled qubits produce correlated outcomes
  - How noise degrades quantum correlations

A Bell state is the simplest entangled state: two qubits that are
perfectly correlated. When you measure, you always get 00 or 11
(never 01 or 10) — unless noise intervenes.

Try it:
    from src.experiments.basics.bell_state import bell_experiment

    # Run with no noise — see perfect correlations
    result = bell_experiment.run({"noise_enabled": False})

    # Run with noise — see how correlations degrade
    result = bell_experiment.run({"noise_enabled": True, "error_rate": 0.05})

    # Sweep noise to watch correlations decay
    results = bell_experiment.sweep(
        parameter_ranges={"error_rate": [0.0, 0.01, 0.05, 0.1, 0.2]}
    )

CIRCUIT:
  q0: ─H──●── M
  q1: ────X── M

  2-qubit GHZ = Bell state Φ+.
  With noise sweep: watch correlations decay as error rate increases.

WHAT YOU'LL EXPLORE:
  - How noise degrades quantum correlations in a Bell state
  - The relationship between error rate and correlation strength
  - What "decoherence" looks like for the simplest entangled state

TRY IT:
    from src.experiments.basics.deep_dives.dd_bell_basics import bell_experiment

    # Single run with default noise
    result = bell_experiment.run()

    # Sweep noise from 0% to 30%
    results = bell_experiment.run_noise_sweep()
"""

from __future__ import annotations

from typing import Any

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


class BellExperiment(BaseExperiment):
    """Create and measure a Bell state (2-qubit GHZ).

    The simplest entangled system. Perfect for learning how
    entanglement shows up in measurement data.
    """

    name = "bell_state"
    description = "Two-qubit Bell state — see quantum correlations in action"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        return ExperimentConfig(
            num_qubits=2,
            state_type="GHZ",
            noise_enabled=True,
            noise_type="depolarizing",
            error_rate=0.02,
            shots=4096,
            metrics="decoherence",
        )

    def run_noise_sweep(
        self,
        steps: int = 10,
        max_error: float = 0.3,
        **overrides: Any,
    ) -> list[ExperimentResult]:
        """Watch correlations decay as noise increases."""
        import numpy as np

        rates = np.linspace(0.0, max_error, steps).tolist()
        return self.sweep(parameter_ranges={"error_rate": rates}, **overrides)


bell_experiment = BellExperiment()
