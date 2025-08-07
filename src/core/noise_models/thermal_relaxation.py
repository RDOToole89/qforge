# src/noise_models/thermal_relaxation.py

import numpy as np
from qiskit_aer.noise import NoiseModel, thermal_relaxation_error
from .base_noise import BaseNoise

class ThermalRelaxationNoise(BaseNoise):
    """
    Enhanced thermal relaxation noise model with proper physics constraints.

    Applies T1/T2 relaxation errors with gate time dependencies and quantum constraints:
    - T2 ≤ 2*T1 (fundamental quantum constraint)
    - Gate time-dependent error probabilities
    - Temperature-dependent thermal population
    """

    def __init__(self, error_rate: float, num_qubits: int, t1: float, t2: float,
                 gate_time: float = 20e-9, temperature: float = 0.015, experiment_id: str = "N/A"):
        super().__init__(error_rate=error_rate, num_qubits=num_qubits, experiment_id=experiment_id)

        # Validate quantum physics constraints
        if t2 > 2 * t1:
            raise ValueError(f"T2 ({t2}) cannot exceed 2*T1 ({2*t1}) - violates quantum physics")
        if t1 <= 0 or t2 <= 0:
            raise ValueError(f"T1 ({t1}) and T2 ({t2}) must be positive")

        self.t1 = t1
        self.t2 = t2
        self.gate_time = gate_time
        self.temperature = temperature  # in Kelvin

        # Calculate thermal population (Boltzmann distribution)
        kb = 8.617e-5  # Boltzmann constant in eV/K
        # Assuming ~5-6 GHz qubit frequency
        freq = 5.5e9  # Hz
        h = 4.136e-15  # Planck constant in eV⋅s
        self.thermal_population = 1 / (1 + np.exp(h * freq / (kb * temperature)))

    def apply(self, noise_model: NoiseModel, gates: list, qubits_for_error: int = None) -> None:
        """Apply gate-time dependent thermal relaxation noise."""

        # Gate-specific times (in seconds)
        gate_times = {
            'id': 0,  # Identity gate has no duration
            'x': self.gate_time,
            'y': self.gate_time,
            'z': 0,  # Virtual Z gate
            'h': self.gate_time,
            'cx': 2 * self.gate_time,  # Two-qubit gates take longer
            'cz': 2 * self.gate_time,
            'rz': 0,  # Virtual rotation
            'rx': self.gate_time,
            'ry': self.gate_time,
        }

        for gate in gates:
            gate_duration = gate_times.get(gate, self.gate_time)  # Default to standard gate time

            if gate_duration == 0:
                continue  # Skip virtual gates

            # Create gate-time dependent thermal relaxation error
            error = thermal_relaxation_error(
                self.t1,
                self.t2,
                gate_duration,
                excited_state_population=self.thermal_population
            )
            noise_model.add_all_qubit_quantum_error(error, gate)

        self.log_noise_application(
            noise_type="THERMAL_RELAXATION",
            gates=gates,
            extra_info={
                "t1": self.t1,
                "t2": self.t2,
                "gate_time": self.gate_time,
                "temperature": self.temperature,
                "thermal_population": self.thermal_population
            }
        )
