"""Step 4: Backend Exploration — Not all quantum computers are the same.

WHAT YOU'LL LEARN:
  IBM has multiple quantum processors, each with different:
  - Qubit count (127, 156 qubits)
  - Coherence times (T1 = how long energy lasts, T2 = how long phase lasts)
  - Calibration quality (changes daily as the hardware is recalibrated)
  - Queue times (popular backends have longer waits)

  Running the same experiment on different backends tells you whether
  your results are a property of the QUANTUM STATE or the SPECIFIC CHIP.

THE EXPERIMENT:
  Run a GHZ-4 state on all available backends and compare:
  - Fidelity (how close to ideal)
  - Structure Score (how structured the decoherence is)
  - Calibration data (T1/T2 medians)

WHAT TO LOOK FOR:
  - Fidelity varies by backend (better T1/T2 = higher fidelity)
  - Structure Score should be CONSISTENT across backends (~5% variation)
  - If SS is consistent, the structure comes from the state, not the chip
  - If SS varies wildly, the hardware is dominating

CIRCUIT:
  q0: ─H──●──●──●── M
  q1: ────X──┼──┼── M
  q2: ───────X──┼── M
  q3: ──────────X── M

  Same circuit on every backend. Only the physical hardware differs.

WHY THIS MATTERS:
  Reproducibility across backends is a key test for any quantum result.
  If your finding only appears on one chip, it might be a hardware
  artifact. If it appears on all chips, it's more likely real physics.

TRY IT:
    from qforge.experiments.hardware.steps.step04_backend_exploration import backend_exploration

    results = backend_exploration.run_all_backends()
"""

from __future__ import annotations

from qforge.engine.models import ExperimentConfig, ExperimentResult
from qforge.experiments.base import BaseExperiment


class BackendExplorationExperiment(BaseExperiment):
    """Step 4: Run the same experiment on multiple quantum processors."""

    name = "hw_04_backend_exploration"
    description = "Step 4: Compare quantum processors — is your result hardware-independent?"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        return ExperimentConfig(
            num_qubits=4,
            state_type="GHZ",
            sim_mode="hardware",
            shots=8192,
            optimization_level=1,
            metrics="decoherence",
            visualization_type="histogram",
        )

    def run_all_backends(self) -> list[ExperimentResult]:
        """Run on all available backends for comparison."""
        backends = ["ibm_fez", "ibm_kingston", "ibm_marrakesh"]
        results = []
        for name in backends:
            try:
                results.append(self.run({"backend_name": name}))
            except Exception as e:
                import logging

                logging.getLogger(__name__).warning(f"Backend {name} unavailable: {e}")
        return results


backend_exploration = BackendExplorationExperiment()
