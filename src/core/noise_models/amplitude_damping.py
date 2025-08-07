# src/noise_models/amplitude_damping.py

import numpy as np
from qiskit_aer.noise import amplitude_damping_error, NoiseModel
from .base_noise import BaseNoise

class AmplitudeDampingNoise(BaseNoise):
    """
    Enhanced amplitude damping noise modeling T1 energy relaxation.

    Represents spontaneous emission and energy decay from |1⟩ to |0⟩ state.
    This is the dominant source of T1 relaxation in superconducting qubits.

    Physics: E(ρ) = (1-γ)ρ + γ σ⁻ ρ σ⁺
    where γ is the damping parameter and σ⁻ = |0⟩⟨1| is the lowering operator.
    """

    def __init__(self, error_rate: float, num_qubits: int = 1, t1: float = None,
                 gate_time: float = 20e-9, temperature: float = 0.015, experiment_id: str = "N/A"):
        # Validate error rate (amplitude damping probability)
        if not 0 <= error_rate <= 1:
            raise ValueError(f"Amplitude damping rate must be between 0 and 1, got {error_rate}")

        super().__init__(error_rate=error_rate, num_qubits=num_qubits, experiment_id=experiment_id)

        self.gate_time = gate_time
        self.temperature = temperature

        # If T1 is provided, calculate damping rate from physics
        if t1 is not None:
            if t1 <= 0:
                raise ValueError(f"T1 must be positive, got {t1}")
            self.t1 = t1
            # γ = 1 - exp(-t_gate/T1) for realistic time-dependent damping
            self.physics_based_rate = 1 - np.exp(-gate_time / t1)

            # Calculate thermal population
            kb = 8.617e-5  # Boltzmann constant in eV/K
            freq = 5.5e9  # Typical qubit frequency
            h = 4.136e-15  # Planck constant in eV⋅s
            self.thermal_population = 1 / (1 + np.exp(h * freq / (kb * temperature)))
        else:
            self.t1 = None
            self.physics_based_rate = error_rate
            self.thermal_population = 0.0  # Assume zero temperature if T1 not given

    def apply(self, noise_model: NoiseModel, gate_list: list, qubits_for_error: int = None) -> None:
        """Apply physics-based amplitude damping noise."""

        # Comprehensive list of single-qubit gates
        single_qubit_gates = [
            'id', 'x', 'y', 'z', 'h', 's', 't', 'sdg', 'tdg',
            'rx', 'ry', 'rz', 'u1', 'u2', 'u3', 'u', 'p'
        ]

        # Filter to only single-qubit gates (amplitude damping is 1-qubit only)
        valid_gates = [g for g in gate_list if g in single_qubit_gates]

        if not valid_gates:
            self.log_noise_application(
                noise_type="AMPLITUDE_DAMPING",
                gates=gate_list,
                extra_info={"warning": "No valid 1-qubit gates found, applying to all gates"}
            )
            # Apply to all gates anyway (for custom gates)
            valid_gates = gate_list

        # Use physics-based rate if T1 was provided, otherwise use error_rate
        damping_rate = self.physics_based_rate

        # Create amplitude damping error with thermal population
        if self.thermal_population > 0:
            # Include thermal excitation (reverse process)
            # In reality, this is more complex, but this gives a first-order correction
            effective_rate = damping_rate * (1 - self.thermal_population)
            noise = amplitude_damping_error(effective_rate)
        else:
            noise = amplitude_damping_error(damping_rate)

        # Apply noise to valid gates
        for gate in valid_gates:
            noise_model.add_all_qubit_quantum_error(noise, gate)

        self.log_noise_application(
            noise_type="AMPLITUDE_DAMPING",
            gates=valid_gates,
            extra_info={
                "damping_rate": damping_rate,
                "t1": self.t1,
                "gate_time": self.gate_time,
                "thermal_population": self.thermal_population,
                "physics_based": self.t1 is not None
            }
        )
