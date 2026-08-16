"""Product superposition state preparation.

# Product Superposition States (Non-Entangled)
Product superposition states consist of multiple qubits each in superposition
but with NO entanglement between them. They are useful as non-entangled
baselines and as starting states for quantum algorithms.

# Mathematical Definition
Product superposition: |ψ⟩ = |ψ₁⟩ ⊗ |ψ₂⟩ ⊗ ... ⊗ |ψₙ⟩
where each |ψᵢ⟩ = cos(θᵢ/2)|0⟩ + e^(iφᵢ)sin(θᵢ/2)|1⟩
"""

from __future__ import annotations

from typing import Any, cast

import numpy as np
from qiskit import QuantumCircuit

from .base_state import BaseState


class SuperpositionState(BaseState):
    """Product superposition state preparation.

    # Quantum State Definition
    Creates separable (non-entangled) multi-qubit states where each qubit
    is independently in superposition. This contrasts with entangled states
    where qubits have quantum correlations.

    # Key Characteristics
    - **Separable**: Can be written as tensor product of single-qubit states
    - **No entanglement**: Measuring one qubit doesn't affect others
    - **Independent decoherence**: Each qubit decoheres independently
    - **Classical correlations only**: No quantum correlations between qubits

    # State Variants
    1. **Uniform superposition**: |+⟩^n = (H⊗H⊗...⊗H)|00...0⟩
    2. **Parametric product**: Custom angles for each qubit independently
    """

    def create(self, add_barrier: bool = False) -> QuantumCircuit:
        """Create quantum circuit that prepares product superposition state.

        # Product State Construction Strategy
        Each qubit is prepared independently using single-qubit rotations:
        1. Apply Ry(θᵢ) to set amplitude ratio for qubit i
        2. Apply Rz(φᵢ) to set relative phase for qubit i
        3. Result: |ψᵢ⟩ = cos(θᵢ/2)|0⟩ + e^(iφᵢ)sin(θᵢ/2)|1⟩

        # Default Behavior
        Without custom parameters, applies H gate to all qubits:
        |+⟩ = (|0⟩ + |1⟩)/√2 for each qubit independently

        # Custom Parameters
        - qubits: "all" or list of specific qubit indices
        - angles: {"theta": θ, "phi": φ} per qubit for custom superposition

        Args:
            add_barrier: Add quantum barrier for circuit visualization

        Returns:
            QuantumCircuit: Circuit that prepares product superposition state

        Example:
            >>> # Uniform superposition (default)
            >>> state = SuperpositionState(3)
            >>> circuit = state.create()  # |+++⟩ state

            >>> # Custom angles per qubit
            >>> state = SuperpositionState(2, {
            ...     "angles": [{"theta": 0.5, "phi": 0.2}, {"theta": 1.0, "phi": 0.0}]
            ... })
        """
        # Create quantum circuit
        circuit = QuantumCircuit(self.num_qubits)

        # Parse parameters
        target_qubits = self._parse_qubits(self.num_qubits, self.custom_params or {})
        angles_by_qubit = self._parse_angles(
            self.num_qubits, self.custom_params or {}, target_qubits
        )

        if angles_by_qubit is None:
            # Default: uniform superposition |+⟩ on target qubits
            for qubit in target_qubits:
                circuit.h(qubit)  # Hadamard creates (|0⟩ + |1⟩)/√2
            variant = "uniform_plus"
            construction_method = "hadamard_gates"

        else:
            # Parametric product state using custom angles
            for qubit in target_qubits:
                angle_dict = angles_by_qubit[qubit]
                if angle_dict is None:
                    # Default to |+⟩ if no specific angles provided
                    circuit.h(qubit)
                else:
                    # Apply custom rotation: Ry(θ) then Rz(φ)
                    circuit.ry(angle_dict["theta"], qubit)
                    circuit.rz(angle_dict["phi"], qubit)
            variant = "parametric_product"
            construction_method = "rotation_gates"

        # Gate-count balancing (equalize noise exposure across qubits)
        if self.balance == "gate_count":
            circuit = self._apply_gate_count_balancing(circuit)

        # Optional: Add barrier for visualization
        if add_barrier:
            circuit.barrier()

        # Log successful creation
        self.log_state_creation(
            f"Product Superposition ({len(target_qubits)} qubits)",
            {
                "entanglement_type": "none_separable",
                "addressed_qubits": target_qubits,
                "variant": variant,
                "construction_method": construction_method,
                "separability": "fully_separable",
            },
        )

        return circuit

    def _parse_qubits(self, num_qubits: int, custom_params: dict) -> list[int]:
        """Parse which qubits to address for superposition preparation.

        Args:
            num_qubits: Total number of qubits in the system
            custom_params: Dictionary containing qubit specifications

        Returns:
            List[int]: Sorted list of qubit indices to address

        Raises:
            ValueError: If qubit specifications are invalid
        """
        qubits_param: str | list[int] = custom_params.get("qubits", "all")

        if qubits_param == "all":
            return list(range(num_qubits))

        if not isinstance(qubits_param, list) or not all(isinstance(q, int) for q in qubits_param):
            raise ValueError("custom_params['qubits'] must be 'all' or a list of integer indices")

        if any(q < 0 or q >= num_qubits for q in qubits_param):
            raise ValueError(f"Qubit indices out of range [0, {num_qubits - 1}]: {qubits_param}")

        return sorted(set(qubits_param))

    def _parse_angles(
        self, num_qubits: int, custom_params: dict, target_qubits: list[int]
    ) -> list[dict[str, float] | None] | None:
        """Parse angle specifications for parametric superposition states.

        Args:
            num_qubits: Total number of qubits
            custom_params: Dictionary containing angle specifications
            target_qubits: List of qubits to be addressed

        Returns:
            List or None: Per-qubit angle dictionaries or None for default

        Raises:
            ValueError: If angle specifications are invalid
        """
        angles = custom_params.get("angles")
        if angles is None:
            return None

        def _normalize_angle_dict(d: dict[str, float]) -> dict[str, float]:
            """Validate and normalize a single angle dictionary."""
            if not isinstance(d, dict):
                raise ValueError("Each angles entry must be a dict with 'theta' and 'phi'")
            if "theta" not in d or "phi" not in d:
                raise ValueError("Angles dict must contain 'theta' and 'phi' keys")

            try:
                theta = float(d["theta"])
                phi = float(d["phi"])
            except (ValueError, TypeError) as e:
                raise ValueError("'theta' and 'phi' must be convertible to float") from e

            return {"theta": theta, "phi": phi}

        # Handle single dict → broadcast to all target qubits
        if isinstance(angles, dict):
            angle_dict = _normalize_angle_dict(angles)
            per_qubit: list[dict[str, float] | None] = [None] * num_qubits
            for qubit in target_qubits:
                per_qubit[qubit] = angle_dict
            return per_qubit

        # Handle list of dicts
        if isinstance(angles, list):
            # List length matches total qubits → map by index
            if len(angles) == num_qubits:
                per_qubit = [None] * num_qubits
                for idx in range(num_qubits):
                    entry = angles[idx]
                    per_qubit[idx] = _normalize_angle_dict(entry) if entry is not None else None
                return per_qubit

            # List length matches target qubits → map onto targets in order
            if len(angles) == len(target_qubits):
                per_qubit = [None] * num_qubits
                for i, qubit in enumerate(target_qubits):
                    entry = angles[i]
                    per_qubit[qubit] = _normalize_angle_dict(entry) if entry is not None else None
                return per_qubit

            raise ValueError(
                f"Angles list length ({len(angles)}) must match either "
                f"num_qubits ({num_qubits}) or target qubits ({len(target_qubits)})"
            )

        raise ValueError("custom_params['angles'] must be a dict or a list of dicts")

    def get_theoretical_state_vector(self) -> np.ndarray:
        """Calculate theoretical state vector for product superposition state.

        # Mathematical Construction
        For product states, the full state vector is the tensor product
        of individual qubit states:
        |ψ⟩ = |ψ₁⟩ ⊗ |ψ₂⟩ ⊗ ... ⊗ |ψₙ⟩

        Returns:
            np.ndarray: Complex state vector of shape (2^n,)

        Example:
            >>> state = SuperpositionState(2)  # Two qubits in |+⟩
            >>> vector = state.get_theoretical_state_vector()
            >>> # [0.5, 0.5, 0.5, 0.5] for |++⟩ = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2
        """
        # Parse configuration
        target_qubits = self._parse_qubits(self.num_qubits, self.custom_params or {})
        angles_by_qubit = self._parse_angles(
            self.num_qubits, self.custom_params or {}, target_qubits
        )

        # Build individual qubit states
        single_qubit_states = []

        for qubit in range(self.num_qubits):
            if qubit not in target_qubits:
                # Unaddressed qubit remains in |0⟩
                qubit_state = np.array([1.0, 0.0], dtype=complex)
            elif angles_by_qubit is None or angles_by_qubit[qubit] is None:
                # Default: |+⟩ = (|0⟩ + |1⟩)/√2
                qubit_state = np.array([1.0, 1.0], dtype=complex) / np.sqrt(2)
            else:
                # Custom angles: cos(θ/2)|0⟩ + e^(iφ)sin(θ/2)|1⟩
                # Guarded above: this branch implies angles_by_qubit[qubit] is not None
                angles = cast("dict[str, float]", angles_by_qubit[qubit])
                theta, phi = angles["theta"], angles["phi"]
                qubit_state = np.array(
                    [np.cos(theta / 2), np.exp(1j * phi) * np.sin(theta / 2)], dtype=complex
                )

            single_qubit_states.append(qubit_state)

        # Compute tensor product of all single-qubit states.
        # Qiskit uses little-endian ordering: qubit 0 is the least-significant
        # bit, so the full state is |q_{n-1}⟩ ⊗ ... ⊗ |q_1⟩ ⊗ |q_0⟩.
        full_state = single_qubit_states[self.num_qubits - 1]
        for i in range(self.num_qubits - 2, -1, -1):
            full_state = np.kron(full_state, single_qubit_states[i])

        return full_state

    def _estimate_circuit_depth(self) -> int:
        """Estimate circuit depth for product superposition preparation.

        # Depth Analysis
        Product states require only single-qubit gates:
        - Uniform superposition: 1 layer (all H gates in parallel)
        - Parametric: 2 layers (Ry then Rz gates in parallel)

        Returns:
            int: Estimated circuit depth
        """
        angles_by_qubit = self._parse_angles(
            self.num_qubits,
            self.custom_params or {},
            self._parse_qubits(self.num_qubits, self.custom_params or {}),
        )

        if angles_by_qubit is None:
            return 1  # Single layer of H gates
        else:
            return 2  # Ry + Rz layers

    def _get_required_gates(self) -> list[str]:
        """Get quantum gates required for product superposition preparation.

        Returns:
            List[str]: Required gate names
        """
        angles_by_qubit = self._parse_angles(
            self.num_qubits,
            self.custom_params or {},
            self._parse_qubits(self.num_qubits, self.custom_params or {}),
        )

        if angles_by_qubit is None:
            return ["h"]  # Hadamard gates only
        else:
            return ["ry", "rz"]  # Rotation gates

    def get_theoretical_properties(self) -> dict[str, Any]:
        """Get theoretical quantum properties of product superposition states.

        Returns:
            Dict with product superposition specific properties
        """
        target_qubits = self._parse_qubits(self.num_qubits, self.custom_params or {})
        angles_by_qubit = self._parse_angles(
            self.num_qubits, self.custom_params or {}, target_qubits
        )

        return {
            "entanglement_type": "none",
            "separability": "fully_separable",
            "addressed_qubits": len(target_qubits),
            "unaddressed_qubits": self.num_qubits - len(target_qubits),
            "schmidt_rank": 1,  # Product states have Schmidt rank 1
            "von_neumann_entropy": 0.0,  # Pure product states have zero entanglement entropy
            "measurement_independence": "complete",  # Measuring one qubit doesn't affect others
            "decoherence_pattern": "independent_per_qubit",
            "classical_correlations_only": True,
            "superposition_type": "parametric" if angles_by_qubit else "uniform",
            "quantum_parallelism": f"2^{len(target_qubits)}_computational_paths",
            "algorithmic_utility": "quantum_algorithm_initialization",
        }

    def __str__(self) -> str:
        """Human-readable description for educational purposes."""
        target_qubits = self._parse_qubits(self.num_qubits, self.custom_params or {})
        angles_by_qubit = self._parse_angles(
            self.num_qubits, self.custom_params or {}, target_qubits
        )

        if len(target_qubits) == self.num_qubits:
            qubit_desc = f"{self.num_qubits} qubits"
        else:
            qubit_desc = f"qubits {target_qubits}"

        if angles_by_qubit is None:
            return (
                f"Product superposition: |+⟩^{len(target_qubits)} on {qubit_desc} [no entanglement]"
            )
        else:
            return f"Parametric product superposition on {qubit_desc} [no entanglement]"
