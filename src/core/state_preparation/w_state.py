# src/state_preparation/w_state.py

from qiskit import QuantumCircuit
import numpy as np
from .base_state import BaseState


class WState(BaseState):
    """
    W state preparation (e.g., (|100⟩ + |010⟩ + |001⟩)/√3 for 3 qubits).
    """

    def create(
        self, add_barrier: bool = False, experiment_id: str = "N/A"
    ) -> QuantumCircuit:
        qc = QuantumCircuit(self.num_qubits)

        # Optional gate-based path for n=3 using decomposition of Initialize
        custom_params = self.custom_params or {}
        method = custom_params.get("method")
        prefer_initialize = custom_params.get("prefer_initialize", True)
        use_gate_based = (method == "gate") or (not prefer_initialize)

        if use_gate_based and self.num_qubits == 3:
            w_state = np.zeros(2**self.num_qubits, dtype=complex)
            for i in range(self.num_qubits):
                w_state[1 << i] = 1 / np.sqrt(self.num_qubits)
            qc.initialize(w_state, range(self.num_qubits))
            qc = qc.decompose()
        else:
            # Default exact initialize for arbitrary n
            w_state = np.zeros(2**self.num_qubits, dtype=complex)
            for i in range(self.num_qubits):
                w_state[1 << i] = 1 / np.sqrt(self.num_qubits)
            qc.initialize(w_state, range(self.num_qubits))

        if add_barrier:
            qc.barrier()
        self.log_state_creation(
            state_type="W",
            extra_info={
                "method": (
                    "gate"
                    if (use_gate_based and self.num_qubits == 3)
                    else "initialize"
                )
            },
        )
        return qc
