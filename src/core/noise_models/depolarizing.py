# src/noise_models/depolarizing.py

from qiskit_aer.noise import NoiseModel, depolarizing_error
from .base_noise import BaseNoise

class DepolarizingNoise(BaseNoise):
    """
    Enhanced depolarizing noise model with multi-qubit support and validation.

    Depolarizing noise represents uniform mixing with the maximally mixed state.
    For n qubits, it applies random Pauli errors with equal probability.
    """

    def __init__(self, error_rate: float, num_qubits: int = 1, experiment_id: str = "N/A"):
        # Validate error rate
        if not 0 <= error_rate <= 1:
            raise ValueError(f"Error rate must be between 0 and 1, got {error_rate}")

        super().__init__(error_rate=error_rate, num_qubits=num_qubits, experiment_id=experiment_id)

        # Calculate theoretical bounds
        max_rate_1q = 0.75  # For 1 qubit: 3/4
        max_rate_2q = 0.9375  # For 2 qubits: 15/16
        max_rate_nq = 1 - (1 / (4**num_qubits))  # For n qubits

        if num_qubits == 1 and error_rate > max_rate_1q:
            raise ValueError(f"Error rate {error_rate} exceeds physical bound {max_rate_1q} for 1-qubit depolarizing")
        elif num_qubits == 2 and error_rate > max_rate_2q:
            raise ValueError(f"Error rate {error_rate} exceeds physical bound {max_rate_2q} for 2-qubit depolarizing")
        elif num_qubits > 2 and error_rate > max_rate_nq:
            raise ValueError(f"Error rate {error_rate} exceeds physical bound {max_rate_nq:.4f} for {num_qubits}-qubit depolarizing")

    def apply(self, noise_model: NoiseModel, gates: list, qubits_for_error: int = None) -> None:
        """Apply depolarizing noise with proper multi-qubit support."""
        # Use qubits_for_error if provided, otherwise use self.num_qubits
        num_qubits_for_error = qubits_for_error if qubits_for_error is not None else self.num_qubits

        # Validate number of qubits
        if num_qubits_for_error < 1 or num_qubits_for_error > 3:
            raise ValueError(f"Depolarizing noise supports 1-3 qubits, got {num_qubits_for_error}")

        # Create a depolarizing error for the appropriate number of qubits
        error = depolarizing_error(self.error_rate, num_qubits_for_error)

        # Apply to gates with appropriate number of qubits
        gate_qubit_mapping = {
            1: ['id', 'x', 'y', 'z', 'h', 'rx', 'ry', 'rz', 's', 't'],
            2: ['cx', 'cy', 'cz', 'ch', 'swap', 'iswap'],
            3: ['ccx', 'cswap']
        }

        for gate in gates:
            # Check if gate is appropriate for the number of qubits
            gate_is_valid = any(gate in qubit_gates for qubit_gates in gate_qubit_mapping.values())

            if gate_is_valid:
                noise_model.add_all_qubit_quantum_error(error, gate)
            else:
                # Apply to gate regardless (for custom gates)
                noise_model.add_all_qubit_quantum_error(error, gate)

        self.log_noise_application(
            noise_type="DEPOLARIZING",
            gates=gates,
            extra_info={
                "error_rate": self.error_rate,
                "num_qubits": num_qubits_for_error,
                "max_physical_rate": 1 - (1 / (4**num_qubits_for_error))
            }
        )
