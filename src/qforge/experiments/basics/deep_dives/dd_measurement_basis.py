"""Deep Dive: Measurement Basis — Seeing what Z-basis can't.

BEST AFTER: Step 8 (Cluster states)

WHAT YOU'LL LEARN:
  In Step 8 you saw that Cluster states look "flat" — no structure
  visible in the measurement data. But Cluster IS entangled!

  The problem: we always measure in the Z-basis (computational basis).
  Some quantum information is "invisible" in Z-basis.

  Solution: measure in a DIFFERENT basis. To measure in the X-basis,
  add a Hadamard gate before measurement. H rotates the measurement
  axis from Z to X.

  Z-basis: measures |0⟩ vs |1⟩ (north vs south pole)
  X-basis: measures |+⟩ vs |−⟩ (east vs west on equator)

THE EXPERIMENT:
  Prepare three states and measure each in both Z and X basis:
  1. |0⟩ — Z-basis: always 0. X-basis: 50/50 (|0⟩ is superposition in X)
  2. |+⟩ — Z-basis: 50/50. X-basis: always 0 (|+⟩ is definite in X)
  3. Bell state — Z-basis: 00/11. X-basis: 00/11 (Bell is symmetric)

WHAT TO LOOK FOR:
  - |0⟩ in Z: 100% "0". |0⟩ in X: 50/50. The same state looks different!
  - |+⟩ in Z: 50/50. |+⟩ in X: 100% "0". Superposition IS definite in X!
  - This is the foundation for quantum key distribution (BB84 protocol)

CIRCUITS:
  Z-basis measurement:          X-basis measurement:
  q: ─[prep]── M ──             q: ─[prep]──H── M ──

  The H before measurement rotates from Z-basis to X-basis.
  H·Z·H = X, so measuring H|ψ⟩ in Z-basis = measuring |ψ⟩ in X-basis.

  |0⟩ in Z: always 0            |0⟩ in X: 50/50 (it's a superposition in X!)
  |+⟩ in Z: 50/50               |+⟩ in X: always 0 (it's definite in X!)

TRY IT:
    from qforge.experiments.basics.deep_dives.dd_measurement_basis import measurement_basis

    results = measurement_basis.run_basis_comparison()
"""

from __future__ import annotations

from qiskit import QuantumCircuit

from qforge.engine.models import ExperimentConfig, ExperimentResult
from qforge.experiments.base import BaseExperiment


class MeasurementBasisExperiment(BaseExperiment):
    """Deep Dive: Z-basis vs X-basis measurement on various states."""

    name = "dd_measurement_basis"
    description = "Deep dive: See hidden quantum information by changing the measurement basis"

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        qc = QuantumCircuit(1, 1)
        qc.h(0)  # prepare |+⟩
        qc.h(0)  # X-basis measurement
        qc.measure(0, 0)
        return ExperimentConfig(
            num_qubits=1,
            state_type="CUSTOM",
            shots=4096,
            noise_enabled=False,
            custom_params={"source": "circuit", "circuit": qc},
            metrics=["asymmetry_index"],
        )

    def run_basis_comparison(self) -> list[ExperimentResult]:
        """Run |0⟩, |+⟩, and Bell state in both Z and X basis."""
        results = []

        states = [
            ("|0⟩", lambda qc: None),  # do nothing
            ("|+⟩", lambda qc: qc.h(0)),  # Hadamard
        ]

        for _name, prep_fn in states:
            # Z-basis
            qc = QuantumCircuit(1, 1)
            prep_fn(qc)
            qc.measure(0, 0)
            results.append(
                self.run(
                    {
                        "custom_params": {"source": "circuit", "circuit": qc},
                    }
                )
            )

            # X-basis (add H before measurement)
            qc = QuantumCircuit(1, 1)
            prep_fn(qc)
            qc.h(0)  # rotate Z→X basis
            qc.measure(0, 0)
            results.append(
                self.run(
                    {
                        "custom_params": {"source": "circuit", "circuit": qc},
                    }
                )
            )

        # Bell state in Z and X basis
        for add_h in [False, True]:
            qc = QuantumCircuit(2, 2)
            qc.h(0)
            qc.cx(0, 1)
            if add_h:
                qc.h(0)
                qc.h(1)
            qc.measure([0, 1], [0, 1])
            results.append(
                self.run(
                    {
                        "num_qubits": 2,
                        "state_type": "CUSTOM",
                        "custom_params": {"source": "circuit", "circuit": qc},
                    }
                )
            )

        return results


measurement_basis = MeasurementBasisExperiment()
