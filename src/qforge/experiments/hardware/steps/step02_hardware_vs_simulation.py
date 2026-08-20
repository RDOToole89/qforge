"""Step 2: Hardware vs Simulation — How good are our models?

WHAT YOU'LL LEARN:
  Simulation uses mathematical noise models (depolarizing, amplitude damping).
  Real hardware has PHYSICAL noise (thermal relaxation, crosstalk, control errors).
  How well do the models match reality?

  This step runs the EXACT same circuit on both hardware and simulation,
  then compares the measurement distributions. Where they agree, the
  model is accurate. Where they differ, there's real physics the model misses.

THE EXPERIMENT:
  Run a 3-qubit GHZ state on hardware and in simulation (with 2% depolarizing).
  Compare the counts side by side.

WHAT TO LOOK FOR:
  - Both should show dominant |000⟩ and |111⟩ peaks
  - Hardware will likely show more |001⟩, |010⟩ etc. (single-bit-flip errors)
  - The ERROR PATTERN may differ: simulation errors are symmetric,
    hardware errors are often asymmetric (more |111⟩→|110⟩ than |000⟩→|001⟩)
  - Fidelity: hardware fidelity depends on the day's calibration

CIRCUIT:
  q0: ─H──●──●── M
  q1: ────X──┼── M
  q2: ───────X── M

  Same GHZ-3 circuit in both modes. Only the execution backend differs.

WHY THIS MATTERS:
  Understanding where simulation breaks down is essential before trusting simulated results.
  If you're comparing error distributions on hardware, you need to know
  which simulation results you can trust and which need real hardware validation.

TRY IT:
    from qforge.experiments.hardware.steps.step02_hardware_vs_simulation import hardware_vs_sim

    hw_result, sim_result = hardware_vs_sim.run_comparison()
"""

from __future__ import annotations

from qforge.engine.models import ExperimentConfig, ExperimentResult
from qforge.experiments.base import BaseExperiment


class HardwareVsSimulationExperiment(BaseExperiment):
    """Step 2: Run the same circuit on hardware and simulation, compare."""

    name = "hw_02_hardware_vs_simulation"
    description = "Step 2: Same circuit on hardware vs simulation — where do models break down?"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        return ExperimentConfig(
            num_qubits=3,
            state_type="GHZ",
            sim_mode="hardware",
            shots=8192,
            optimization_level=1,
            visualization_type="histogram",
        )

    def run_comparison(self) -> tuple[ExperimentResult, ExperimentResult]:
        """Run on hardware and simulation, return both for comparison."""
        hw = self.run()

        sim = self.run(
            {
                "sim_mode": "qasm",
                "noise_enabled": True,
                "noise_type": "depolarizing",
                "error_rate": 0.02,
                "rng_seed": 42,
            }
        )

        return hw, sim


hardware_vs_sim = HardwareVsSimulationExperiment()
