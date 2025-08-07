# src/noise_models/phase_damping.py

import numpy as np
from qiskit_aer.noise import phase_damping_error, NoiseModel
from .base_noise import BaseNoise

class PhaseDampingNoise(BaseNoise):
    """
    Enhanced phase damping noise modeling pure dephasing (T2* process).

    Represents phase decoherence without energy loss - the qubit maintains
    its population but loses phase coherence between |0⟩ and |1⟩ states.

    Physics: Destroys off-diagonal elements of density matrix while preserving populations.
    This corresponds to the T2* process in superconducting qubits, often due to
    magnetic field fluctuations and charge noise.
    """

    def __init__(self, error_rate: float, num_qubits: int = 1, t2_star: float = None,
                 gate_time: float = 20e-9, experiment_id: str = "N/A"):
        # Validate error rate (phase damping probability)
        if not 0 <= error_rate <= 1:
            raise ValueError(f"Phase damping rate must be between 0 and 1, got {error_rate}")

        super().__init__(error_rate=error_rate, num_qubits=num_qubits, experiment_id=experiment_id)

        self.gate_time = gate_time

        # If T2* is provided, calculate damping rate from physics
        if t2_star is not None:
            if t2_star <= 0:
                raise ValueError(f"T2* must be positive, got {t2_star}")
            self.t2_star = t2_star
            # γ = 1 - exp(-t_gate/T2*) for realistic time-dependent dephasing
            self.physics_based_rate = 1 - np.exp(-gate_time / t2_star)
        else:
            self.t2_star = None
            self.physics_based_rate = error_rate

    def apply(self, noise_model: NoiseModel, gate_list: list, qubits_for_error: int = None) -> None:
        """Apply physics-based phase damping noise."""

        # Comprehensive list of single-qubit gates
        single_qubit_gates = [
            'id', 'x', 'y', 'z', 'h', 's', 't', 'sdg', 'tdg',
            'rx', 'ry', 'rz', 'u1', 'u2', 'u3', 'u', 'p'
        ]

        # Filter to only single-qubit gates (phase damping is 1-qubit only)
        valid_gates = [g for g in gate_list if g in single_qubit_gates]

        if not valid_gates:
            self.log_noise_application(
                noise_type="PHASE_DAMPING",
                gates=gate_list,
                extra_info={"warning": "No valid 1-qubit gates found, applying to all gates"}
            )
            # Apply to all gates anyway (for custom gates)
            valid_gates = gate_list

        # Use physics-based rate if T2* was provided, otherwise use error_rate
        damping_rate = self.physics_based_rate

        # Phase damping primarily affects gates that create superposition
        # Virtual Z gates don't contribute to dephasing
        gate_sensitivity = {
            'z': 0.0, 'rz': 0.0, 'u1': 0.0, 'p': 0.0,  # Virtual gates
            'id': 0.1,  # Idle time dephasing
            'x': 1.0, 'y': 1.0, 'h': 1.0,  # Full sensitivity for superposition gates
            'rx': 1.0, 'ry': 1.0, 's': 0.5, 't': 0.5  # Partial sensitivity
        }

        # Apply noise to valid gates with gate-dependent sensitivity
        for gate in valid_gates:
            sensitivity = gate_sensitivity.get(gate, 1.0)  # Default full sensitivity
            effective_rate = damping_rate * sensitivity

            if effective_rate > 0:  # Only apply if there's actual dephasing
                noise = phase_damping_error(effective_rate)
                noise_model.add_all_qubit_quantum_error(noise, gate)

        self.log_noise_application(
            noise_type="PHASE_DAMPING",
            gates=valid_gates,
            extra_info={
                "damping_rate": damping_rate,
                "t2_star": self.t2_star,
                "gate_time": self.gate_time,
                "physics_based": self.t2_star is not None,
                "gate_sensitivity_applied": True
            }
        )
