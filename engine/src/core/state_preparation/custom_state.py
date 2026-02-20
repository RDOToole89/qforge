"""
Custom State Preparation for Advanced Quantum Research

# Custom States - Flexible Circuit Definition
Custom states provide maximum flexibility for advanced quantum experiments,
allowing researchers to define arbitrary quantum circuits through multiple
input methods. This bridges the gap between standard state preparation
and cutting-edge research requirements.

# Mathematical Flexibility
Custom states can represent any quantum state |ψ⟩ that can be prepared
through a sequence of quantum gates, imported from external sources,
or defined programmatically through builder functions.

# Research Applications in Advanced Studies
- Novel state topologies: Experiment with new entanglement structures
- Algorithm development: Test custom initialization states
- Hardware validation: Import real device characterization circuits
- Collaborative research: Share and reproduce exact circuit definitions
- OpenQASM integration: Compatibility with quantum software ecosystem
"""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit

from .base_state import BaseState


class CustomState(BaseState):
    """
    Advanced custom state preparation for cutting-edge quantum research.

    # Quantum Circuit Flexibility
    Custom states enable researchers to define arbitrary quantum circuits through
    multiple input methods, providing maximum flexibility for novel experiments
    while maintaining integration with the structured decoherence framework.

    # Input Methods Supported
    1. **Gate Sequences**: Define circuits as lists of quantum gates with parameters
    2. **Builder Functions**: Use Python functions to generate circuits programmatically
    3. **OpenQASM Files**: Import circuits from the quantum assembly language standard

    # Research Applications
    - **Novel Topologies**: Test new entanglement structures not covered by standard states
    - **Algorithm Development**: Create custom initialization states for quantum algorithms
    - **Hardware Validation**: Import characterized circuits from real quantum devices
    - **Reproducible Research**: Share exact circuit definitions with collaborators
    - **Legacy Integration**: Bridge with existing quantum software and research

    # Custom Parameters Schema
    Required:
    - source: 'gates' | 'builder' | 'openqasm'

    For 'gates' source:
    - num_qubits: int (positive)
    - gates: List of gate dictionaries with 'name', 'qargs', optional 'params'/'cargs'

    For 'builder' source:
    - num_qubits: int (positive)
    - builder: str (dotted path 'package.module:function')

    For 'openqasm' source:
    - openqasm: str (file path)
    - num_qubits: int (optional, for validation)

    Optional:
    - validate: bool (default True)
    - metadata: Dict (research context)

    # Educational Notes
    Custom states demonstrate the flexibility of quantum circuit model,
    showing how quantum computation can be expressed through gate sequences,
    functional programming, or quantum assembly language.
    """

    def create(self, add_barrier: bool = False) -> QuantumCircuit:
        """
        Create quantum circuit from custom specification.

        # Custom Circuit Construction Strategy
        Supports three distinct input methods for maximum research flexibility:

        1. **Gate Sequence Method**:
           - Define circuits as lists of quantum gates
           - Full control over gate parameters and qubit addressing
           - Ideal for algorithmic state preparation

        2. **Builder Function Method**:
           - Use Python functions to generate circuits programmatically
           - Enables complex conditional logic and parameterization
           - Perfect for automated circuit generation

        3. **OpenQASM Import Method**:
           - Load circuits from quantum assembly language files
           - Compatibility with quantum software ecosystem
           - Research collaboration and legacy integration

        Args:
            add_barrier: Add quantum barrier for circuit visualization

        Returns:
            QuantumCircuit: Custom quantum circuit as specified

        Raises:
            ValueError: If source type, parameters, or circuit structure is invalid

        Example:
            >>> # Gate sequence method
            >>> custom = CustomState(2, {
            ...     "source": "gates",
            ...     "num_qubits": 2,
            ...     "gates": [
            ...         {"name": "h", "qargs": [0]},
            ...         {"name": "cx", "qargs": [0, 1]}
            ...     ]
            ... })

            >>> # Builder function method
            >>> custom = CustomState(3, {
            ...     "source": "builder",
            ...     "num_qubits": 3,
            ...     "builder": "my_module.states:create_w_state"
            ... })
        """
        params: dict[str, Any] = self.custom_params or {}

        source = params.get("source")
        validate = bool(params.get("validate", True))
        metadata = params.get("metadata", {})

        if source not in {"gates", "builder", "openqasm"}:
            raise ValueError(
                "CustomState requires 'source' to be one of 'gates'|'builder'|'openqasm'"
            )

        if source == "gates":
            num_qubits = params.get("num_qubits")
            if not isinstance(num_qubits, int) or num_qubits <= 0:
                raise ValueError("'num_qubits' must be a positive integer for gates source")
            qc = QuantumCircuit(num_qubits)
            gates: list[dict[str, Any]] = params.get("gates", [])
            if not isinstance(gates, list) or not gates:
                raise ValueError("'gates' must be a non-empty list for gates source")
            for _i, g in enumerate(gates):
                if not isinstance(g, dict):
                    raise ValueError("Each gate entry must be a dict")
                name = g.get("name")
                qargs = g.get("qargs", [])
                par = g.get("params", [])
                cargs = g.get("cargs", [])
                if not isinstance(name, str) or not name:
                    raise ValueError("Gate 'name' must be a non-empty string")
                if not isinstance(qargs, list) or not all(isinstance(q, int) for q in qargs):
                    raise ValueError("Gate 'qargs' must be a list of integers")
                if validate:
                    for q in qargs:
                        if q < 0 or q >= num_qubits:
                            raise ValueError("qargs index out of range")
                # Append gate operation
                method = getattr(qc, name)
                if par and cargs:
                    method(*par, *qargs, *cargs)  # rarely used path
                elif par:
                    method(*par, *qargs)
                else:
                    method(*qargs)

        elif source == "builder":
            builder_path = params.get("builder")
            num_qubits = params.get("num_qubits")
            if not isinstance(builder_path, str) or ":" not in builder_path:
                raise ValueError("'builder' must be a dotted path 'package.module:function'")
            if not isinstance(num_qubits, int) or num_qubits <= 0:
                raise ValueError("'num_qubits' must be a positive integer for builder source")
            mod_path, func_name = builder_path.split(":", 1)
            mod = importlib.import_module(mod_path)
            func = getattr(mod, func_name)
            qc = func(num_qubits)
            if not isinstance(qc, QuantumCircuit):
                raise ValueError("builder did not return a QuantumCircuit")
            if validate and qc.num_qubits != num_qubits:
                raise ValueError("builder returned circuit with unexpected num_qubits")

        else:  # openqasm
            qasm_path = params.get("openqasm")
            if not isinstance(qasm_path, str):
                raise ValueError("'openqasm' must be a file path string")
            path = Path(qasm_path)
            if not path.exists():
                raise ValueError("OpenQASM file not found")
            qc = QuantumCircuit.from_qasm_file(str(path))
            num_qubits = params.get("num_qubits")
            if num_qubits is not None and validate and qc.num_qubits != num_qubits:
                raise ValueError("QASM circuit num_qubits mismatch")

        if add_barrier:
            qc.barrier()

        # Log successful creation with comprehensive metadata
        self.log_state_creation(
            f"Custom State ({source} source)",
            {
                "entanglement_type": "user_defined",
                "source_method": source,
                "circuit_depth": qc.depth(),
                "gate_count": len(qc.data),
                "gate_types": list(qc.count_ops().keys()),
                "num_qubits": qc.num_qubits,
                "user_metadata": metadata,
                "research_role": "advanced_custom_experiment",
                "reproducibility": "full_specification_provided",
            },
        )

        return qc

    def get_theoretical_state_vector(self) -> np.ndarray:
        """
        Calculate theoretical state vector for custom circuit (warning: may be computationally intensive).

        # Computational Warning
        Custom circuits can be arbitrarily complex, making state vector calculation
        expensive or impossible for large systems. This method provides theoretical
        construction but should be used carefully.

        # Implementation Strategy
        Custom circuits require simulation since they can contain arbitrary gate
        sequences without analytical formulas. Uses BaseState simulation helper
        for consistent behavior and error handling across all state types.

        Returns:
            np.ndarray: Complex state vector of shape (2^n,)

        Note:
            For complex custom circuits, consider using circuit simulation
            rather than computing the full state vector.
        """
        # Create circuit first to determine actual qubit count
        circuit = self.create()

        # Use BaseState validation helper for consistent size checking
        self._validate_large_system("Theoretical state vector calculation", threshold=10)

        # Use BaseState simulation helper for consistent behavior
        return self._simulate_circuit_state_vector(circuit)

    def _estimate_circuit_depth(self) -> int:
        """
        Estimate circuit depth for custom state preparation.

        # Depth Analysis
        Custom circuits have user-defined depth that depends entirely
        on the specific circuit construction method used.

        Returns:
            int: Estimated circuit depth
        """
        try:
            circuit = self.create()
            return circuit.depth()
        except Exception:
            # If circuit creation fails, return conservative estimate
            return self.num_qubits  # Conservative estimate

    def _get_required_gates(self) -> list[str]:
        """
        Get quantum gates required for custom state preparation.

        Returns:
            List[str]: Required gate names (depends on custom specification)
        """
        try:
            circuit = self.create()
            return list(circuit.count_ops().keys())
        except Exception:
            # If circuit creation fails, return common gates
            return ["h", "cx", "u3"]  # Common gate set

    def get_theoretical_properties(self) -> dict[str, Any]:
        """
        Get theoretical quantum properties of custom states.

        Returns:
            Dict with custom state properties (limited analysis due to arbitrary nature)
        """
        params = self.custom_params or {}
        source = params.get("source", "unknown")
        metadata = params.get("metadata", {})

        return {
            "entanglement_type": "user_defined",
            "source_method": source,
            "separability": "unknown_requires_analysis",
            "schmidt_rank": "unknown_arbitrary_circuit",
            "measurement_correlations": "depends_on_circuit_structure",
            "custom_metadata": metadata,
            "analysis_complexity": "high_arbitrary_circuit",
            "research_flexibility": "maximum",
            "reproducibility": "exact_specification_provided",
        }

    def get_research_context(self) -> dict[str, Any]:
        """
        Get research context for custom state studies.

        Returns:
            Dict with research context and experimental considerations
        """
        params = self.custom_params or {}
        source = params.get("source", "unknown")

        return {
            "pathway_hypothesis": {
                "prediction": "Pathway structure depends on circuit topology and gate sequence",
                "test_method": "Analyze custom circuit structure for entanglement patterns",
                "expected_signature": "Varies based on circuit design and gate connectivity",
            },
            "decoherence_characteristics": {
                "circuit_dependence": "Highly dependent on specific gate sequence and topology",
                "entanglement_structure": "Determined by user-defined circuit architecture",
                "pathway_complexity": "Can range from trivial to maximally complex",
                "noise_interaction": "Depends on gate types and circuit depth",
            },
            "experimental_role": {
                "research_flexibility": "Maximum flexibility for novel experiments",
                "hypothesis_testing": "Custom states for specific research questions",
                "algorithm_development": "Test novel quantum algorithms and protocols",
                "hardware_characterization": "Validate device performance with known circuits",
            },
            "research_predictions": {
                "pathway_analysis": "Requires case-by-case analysis based on circuit structure",
                "decoherence_patterns": "Depends on entanglement topology defined by gates",
                "comparison_utility": "Ideal for testing specific hypotheses",
                "reproducibility": "Exact circuit specification enables perfect reproduction",
            },
            "practical_applications": {
                "algorithm_research": "Development and testing of quantum algorithms",
                "device_validation": "Hardware characterization with known reference circuits",
                "educational_examples": "Custom examples for teaching quantum mechanics",
                "collaborative_research": "Share exact circuit definitions between researchers",
                "legacy_integration": f"Import circuits from {source} sources",
            },
        }

    def __str__(self) -> str:
        """Human-readable description for educational purposes."""
        params = self.custom_params or {}
        source = params.get("source", "unknown")

        if source == "gates":
            gates = params.get("gates", [])
            gate_names = [g.get("name", "?") for g in gates[:3]]  # Show first 3 gates
            gate_desc = "+".join(gate_names)
            if len(gates) > 3:
                gate_desc += f"+{len(gates) - 3}more"
            return f"Custom state: {self.num_qubits}-qubit circuit ({gate_desc}) [user-defined]"
        elif source == "builder":
            builder = params.get("builder", "unknown")
            func_name = builder.split(":")[-1] if ":" in builder else builder
            return f"Custom state: {self.num_qubits}-qubit circuit (builder: {func_name}) [user-defined]"
        elif source == "openqasm":
            qasm_path = params.get("openqasm", "unknown")
            filename = Path(qasm_path).name if isinstance(qasm_path, str) else "unknown"
            return f"Custom state: circuit from {filename} [user-defined]"
        else:
            return (
                f"Custom state: {self.num_qubits}-qubit circuit (source: {source}) [user-defined]"
            )
