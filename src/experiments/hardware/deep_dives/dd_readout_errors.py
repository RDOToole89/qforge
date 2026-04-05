"""Deep Dive: Readout Errors — When measurement itself is noisy.

BEST AFTER: Step 2 (hardware vs simulation)

WHAT YOU'LL EXPLORE:
  Gate errors happen DURING the circuit. Readout errors happen DURING
  MEASUREMENT — the qubit is in state |0⟩ but the detector reports |1⟩
  (or vice versa). These are independent noise sources.

  The framework supports readout errors in simulation via the
  readout_error_rate config parameter. This deep dive compares:
  1. Gate noise only (depolarizing)
  2. Readout noise only (measurement errors)
  3. Both together (realistic scenario)
  4. Real hardware (which has both naturally)

WHAT TO LOOK FOR:
  - Gate-only: errors create off-diagonal outcomes (|01⟩, |10⟩ from Bell state)
  - Readout-only: ALSO creates |01⟩, |10⟩ but from a different mechanism
  - Both together: more total noise, but the error PATTERN changes
  - Hardware: compare with the combined simulation

CIRCUIT:
  q0: ─H──●── M     (Bell state)
  q1: ────X── M

  The circuit is the same in all cases.
  What changes is WHERE the noise enters:
  - Gate noise: between gates (during circuit execution)
  - Readout noise: at the measurement step (detector imperfection)

TRY IT:
    from src.experiments.hardware.deep_dives.dd_readout_errors import readout_errors

    results = readout_errors.run_noise_source_comparison()
"""

from __future__ import annotations

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


class ReadoutErrorsExperiment(BaseExperiment):
    """Deep Dive: Compare gate noise, readout noise, and both together."""

    name = "dd_readout_errors"
    description = "Deep dive: Readout errors — when measurement itself is noisy"

    def default_config(self) -> ExperimentConfig:
        return ExperimentConfig(
            num_qubits=2,
            state_type="GHZ",
            shots=8192,
            noise_enabled=True,
            noise_type="depolarizing",
            error_rate=0.02,
            readout_error_rate=0.05,
            rng_seed=42,
            visualization_type="histogram",
        )

    def run_noise_source_comparison(self) -> list[ExperimentResult]:
        """Compare gate-only, readout-only, and combined noise."""
        results = []

        # Gate noise only
        results.append(self.run({
            "noise_enabled": True, "noise_type": "depolarizing",
            "error_rate": 0.02, "readout_error_rate": None,
        }))

        # Readout noise only
        results.append(self.run({
            "noise_enabled": False, "noise_type": None,
            "error_rate": None, "readout_error_rate": 0.05,
        }))

        # Both
        results.append(self.run({
            "noise_enabled": True, "noise_type": "depolarizing",
            "error_rate": 0.02, "readout_error_rate": 0.05,
        }))

        return results


readout_errors = ReadoutErrorsExperiment()
