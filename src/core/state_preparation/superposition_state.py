# src/state_preparation/superposition_state.py

from qiskit import QuantumCircuit
from typing import List, Dict, Optional, Union
from .base_state import BaseState


class SuperpositionState(BaseState):
    """
    Prepares an n-qubit product superposition state (no entanglement).

    Defaults to the uniform superposition |+>^n by applying H to each qubit.

    Supports parametric, per-qubit product states using single-qubit rotations
    without entanglement:
      - angles: list of {"theta": float, "phi": float} per qubit, or a single dict
        applied to the selected qubits. The sequence Ry(theta) followed by Rz(phi)
        is applied to prepare a general product state on each addressed qubit.

    custom_params schema (all optional):
      - qubits: "all" (default) or List[int] of qubit indices to address
      - angles: Dict[str, float] or List[Dict[str, float]] with keys "theta", "phi"

    Notes:
      - This state is separable by construction (no multi-qubit gates).
      - Useful as a phase-noise baseline and for algorithmic starting states.
    """

    def _parse_qubits(self, num_qubits: int, custom_params: Dict) -> List[int]:
        qubits_param: Union[str, List[int]] = custom_params.get("qubits", "all")
        if qubits_param == "all":
            return list(range(num_qubits))
        if not isinstance(qubits_param, list) or not all(isinstance(q, int) for q in qubits_param):
            raise ValueError("custom_params['qubits'] must be 'all' or a list of int indices")
        if any(q < 0 or q >= num_qubits for q in qubits_param):
            raise ValueError("custom_params['qubits'] indices out of range")
        return sorted(set(qubits_param))

    def _parse_angles(self, num_qubits: int, custom_params: Dict, target_qubits: List[int]) -> Optional[List[Optional[Dict[str, float]]]]:
        angles = custom_params.get("angles")
        if angles is None:
            return None

        def _norm_angle_dict(d: Dict[str, float]) -> Dict[str, float]:
            if not isinstance(d, dict):
                raise ValueError("Each angles entry must be a dict with 'theta' and 'phi'")
            if "theta" not in d or "phi" not in d:
                raise ValueError("Angles dict must contain 'theta' and 'phi'")
            theta = float(d["theta"])  # may raise
            phi = float(d["phi"])      # may raise
            return {"theta": theta, "phi": phi}

        # Accept a single dict → broadcast to all target qubits
        if isinstance(angles, dict):
            angle_dict = _norm_angle_dict(angles)
            per_qubit: List[Optional[Dict[str, float]]] = [None] * num_qubits
            for q in target_qubits:
                per_qubit[q] = angle_dict
            return per_qubit

        # Or a list with per-qubit entries aligned to num_qubits or target set
        if isinstance(angles, list):
            # If list length equals num_qubits, map by index
            if len(angles) == num_qubits:
                per_qubit = [None] * num_qubits
                for idx in range(num_qubits):
                    entry = angles[idx]
                    per_qubit[idx] = _norm_angle_dict(entry) if entry is not None else None
                return per_qubit
            # If list length equals len(target_qubits), map onto targets in order
            if len(angles) == len(target_qubits):
                per_qubit = [None] * num_qubits
                for i, q in enumerate(target_qubits):
                    entry = angles[i]
                    per_qubit[q] = _norm_angle_dict(entry) if entry is not None else None
                return per_qubit
            raise ValueError("custom_params['angles'] length must match num_qubits or number of target qubits")

        raise ValueError("custom_params['angles'] must be a dict or a list")

    def create(self, add_barrier: bool = False, experiment_id: str = "N/A") -> QuantumCircuit:
        qc = QuantumCircuit(self.num_qubits)

        target_qubits = self._parse_qubits(self.num_qubits, self.custom_params)
        angles_by_qubit = self._parse_angles(self.num_qubits, self.custom_params, target_qubits)

        if angles_by_qubit is None:
            # Default: uniform superposition on target qubits
            for q in target_qubits:
                qc.h(q)
            variant = "uniform_plus"
        else:
            # Parametric product state using single-qubit rotations
            for q in target_qubits:
                angle_dict = angles_by_qubit[q]
                if angle_dict is None:
                    # If unspecified for this qubit, default to |+>
                    qc.h(q)
                else:
                    qc.ry(angle_dict["theta"], q)
                    qc.rz(angle_dict["phi"], q)
            variant = "parametric_product"

        if add_barrier:
            qc.barrier()

        self.log_state_creation(state_type="SUPERPOSITION", extra_info={
            "addressed_qubits": target_qubits,
            "variant": variant,
        })
        return qc

