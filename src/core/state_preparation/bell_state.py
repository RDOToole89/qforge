# src/state_preparation/bell_state.py

from qiskit import QuantumCircuit
from .base_state import BaseState


class BellState(BaseState):
    """
    Prepares a 2-qubit Bell (EPR) state.

    Variants (custom_params['variant']):
      - 'phi_plus'  (|00> + |11>)/√2  [default]
      - 'phi_minus' (|00> - |11>)/√2
      - 'psi_plus'  (|01> + |10>)/√2
      - 'psi_minus' (|01> - |10>)/√2
    """

    def create(self, add_barrier: bool = False, experiment_id: str = "N/A") -> QuantumCircuit:
        if self.num_qubits != 2:
            raise ValueError("Bell state requires exactly 2 qubits")

        variant = (self.custom_params or {}).get("variant", "phi_plus").lower()

        qc = QuantumCircuit(2)
        # Prepare |phi_plus> baseline
        qc.h(0)
        qc.cx(0, 1)

        if variant == "phi_plus":
            pass
        elif variant == "phi_minus":
            qc.z(0)
        elif variant == "psi_plus":
            qc.x(1)
        elif variant == "psi_minus":
            qc.z(0)
            qc.x(1)
        else:
            raise ValueError("Unknown Bell variant. Use phi_plus|phi_minus|psi_plus|psi_minus")

        if add_barrier:
            qc.barrier()

        self.log_state_creation(state_type="BELL", extra_info={"variant": variant})
        return qc

