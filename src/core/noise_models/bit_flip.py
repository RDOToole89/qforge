# src/noise_models/bit_flip.py

from qiskit_aer.noise import pauli_error, NoiseModel
from .base_noise import BaseNoise
from typing import Optional, List

class BitFlipNoise(BaseNoise):
    """
    Enhanced bit flip noise modeling coherent X-axis rotation errors.

    Represents systematic over/under-rotation errors in X gates, often due to:
    - Imperfect pulse calibration
    - Microwave amplitude fluctuations
    - Control electronics drift

    This is a coherent error (unitary) unlike depolarizing noise (incoherent).
    """

    def __init__(self, error_rate: float, num_qubits: int = 1,
                 x_prob: Optional[float] = None, i_prob: Optional[float] = None,
                 experiment_id: str = "N/A"):
        # Validate error rate
        if not 0 <= error_rate <= 1:
            raise ValueError(f"Bit flip error rate must be between 0 and 1, got {error_rate}")

        super().__init__(error_rate=error_rate, num_qubits=num_qubits, experiment_id=experiment_id)

        # Allow custom X/I probabilities or use error_rate
        if x_prob is not None and i_prob is not None:
            if x_prob < 0 or i_prob < 0:
                raise ValueError(f"Probabilities must be non-negative: x_prob={x_prob}, i_prob={i_prob}")
            total_prob = x_prob + i_prob
            if abs(total_prob - 1.0) > 1e-6:
                raise ValueError(f"Probabilities must sum to 1: x_prob={x_prob}, i_prob={i_prob}, sum={total_prob}")
            self.x_prob = x_prob
            self.i_prob = i_prob
        else:
            self.x_prob = error_rate
            self.i_prob = 1.0 - error_rate

        # Validate probabilities
        if not (0 <= self.x_prob <= 1 and 0 <= self.i_prob <= 1):
            raise ValueError(f"Probabilities must be between 0 and 1: x_prob={self.x_prob}, i_prob={self.i_prob}")

    def apply(self, noise_model: NoiseModel, gate_list: list, qubits_for_error: int = None,
              specific_qubits: Optional[List[int]] = None) -> None:
        """Apply bit flip noise with gate-specific sensitivity."""

        # Comprehensive list of single-qubit gates
        single_qubit_gates = [
            'id', 'x', 'y', 'z', 'h', 's', 't', 'sdg', 'tdg',
            'rx', 'ry', 'rz', 'u1', 'u2', 'u3', 'u', 'p'
        ]

        # Filter to only single-qubit gates
        valid_gates = [g for g in gate_list if g in single_qubit_gates]

        if not valid_gates:
            self.log_noise_application(
                noise_type="BIT_FLIP",
                gates=gate_list,
                extra_info={"warning": "No valid 1-qubit gates found, applying to all gates"}
            )
            # Apply to all gates anyway (for custom gates)
            valid_gates = gate_list

        # Bit flip noise sensitivity by gate type
        # X gates are most susceptible, Z gates immune, others intermediate
        gate_sensitivity = {
            'x': 1.0, 'rx': 1.0,  # X-rotation gates most sensitive
            'y': 0.7, 'ry': 0.7,  # Y gates have some X component
            'h': 0.5,  # Hadamard has X component
            'z': 0.0, 'rz': 0.0, 'u1': 0.0, 'p': 0.0, 's': 0.0, 't': 0.0,  # Z-only gates immune
            'id': 0.1,  # Small bit flip during idle
            'u2': 0.5, 'u3': 0.8, 'u': 0.8  # General gates have intermediate sensitivity
        }

        # Create the Pauli error
        error = pauli_error([("X", self.x_prob), ("I", self.i_prob)])

        # Apply to gates with sensitivity weighting
        if specific_qubits is not None:
            # Apply to specific qubits
            for qubit in specific_qubits:
                for gate in valid_gates:
                    sensitivity = gate_sensitivity.get(gate, 0.5)  # Default moderate sensitivity
                    if sensitivity > 0:
                        # Scale error by gate sensitivity
                        scaled_x_prob = self.x_prob * sensitivity
                        scaled_i_prob = 1.0 - scaled_x_prob
                        scaled_error = pauli_error([("X", scaled_x_prob), ("I", scaled_i_prob)])
                        noise_model.add_quantum_error(scaled_error, gate, [qubit])
        else:
            # Apply to all qubits
            for gate in valid_gates:
                sensitivity = gate_sensitivity.get(gate, 0.5)  # Default moderate sensitivity
                if sensitivity > 0:
                    # Scale error by gate sensitivity
                    scaled_x_prob = self.x_prob * sensitivity
                    scaled_i_prob = 1.0 - scaled_x_prob
                    scaled_error = pauli_error([("X", scaled_x_prob), ("I", scaled_i_prob)])
                    noise_model.add_all_qubit_quantum_error(scaled_error, gate)

        self.log_noise_application(
            noise_type="BIT_FLIP",
            gates=valid_gates,
            extra_info={
                "x_prob": self.x_prob,
                "i_prob": self.i_prob,
                "gate_sensitivity_applied": True,
                "specific_qubits": specific_qubits
            }
        )
