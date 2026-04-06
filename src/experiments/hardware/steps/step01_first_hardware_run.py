"""Step 1: First Hardware Run — Your first real quantum computer.

WHAT YOU'LL LEARN:
  Everything you've run so far has been simulated on your laptop.
  Now you're about to run a circuit on an ACTUAL quantum processor —
  superconducting qubits cooled to 15 millikelvin in an IBM data center.

  The experience is different from simulation:
  - There's a queue (other people are using the computer too)
  - The noise is REAL (not a model, actual physical decoherence)
  - Results vary between runs (no rng_seed — nature is random)
  - You get provenance (which chip, what calibration, transpilation details)

PREREQUISITES:
  You need IBM Quantum credentials. See docs/guides/hardware-setup.md.
  Quick version:
    from qiskit_ibm_runtime import QiskitRuntimeService
    QiskitRuntimeService.save_account(
        channel="ibm_quantum_platform", token="YOUR_TOKEN", set_as_default=True
    )

THE EXPERIMENT:
  Run the simplest possible entangled state — a 2-qubit Bell state —
  on real hardware. Compare with the simulation you ran in basics step 04.

WHAT TO LOOK FOR:
  - You should see ~50% |00⟩ and ~50% |11⟩ (just like simulation)
  - But also some |01⟩ and |10⟩ (real noise! simulation had none without noise_enabled)
  - The |01⟩ and |10⟩ fractions will be ASYMMETRIC — real hardware noise
    is not symmetric like depolarizing. This is real physics.
  - Check the provenance: which backend? What T1/T2? How deep after transpilation?

CIRCUIT:
  q0: ─H──●── M
  q1: ────X── M

  Logical depth: 2. Transpiled depth: ~8 (H and CNOT decompose to native gates).
  Native gates on IBM Heron: sx, rz, cz.

TRY IT:
    from src.experiments.hardware.steps.step01_first_hardware_run import first_hardware

    result = first_hardware.run()
    print(f"Backend: {result.provenance.simulator_info['backend_name']}")
    print(f"Counts: {result.analysis.measurement_results.raw_counts}")
"""

from __future__ import annotations

from src.engine.models import ExperimentConfig, ExperimentResult
from src.experiments.base import BaseExperiment


class FirstHardwareRunExperiment(BaseExperiment):
    """Step 1: Run your first circuit on real quantum hardware."""

    name = "hw_01_first_hardware_run"
    description = "Step 1: Your first real quantum computer — Bell state on IBM hardware"

    def default_config(self) -> ExperimentConfig:
        return ExperimentConfig(
            num_qubits=2,
            state_type="GHZ",
            sim_mode="hardware",
            shots=4096,
            optimization_level=1,
            visualization_type="histogram",
        )


first_hardware = FirstHardwareRunExperiment()
