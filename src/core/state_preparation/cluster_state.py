"""
Cluster State Preparation for Graph-State Network Research

# Cluster States - Graph-Based Quantum Networks
Cluster states are a class of highly entangled quantum states that form the basis
of measurement-based quantum computing. They represent quantum networks where
qubits are arranged in graph structures with nearest-neighbor entanglement.

# Mathematical Definition
|Cluster⟩ = ∏ᵢⱼ CZ(i,j) (H⊗H⊗...⊗H) |00...0⟩
where CZ(i,j) are controlled-Z gates applied between connected qubits in the graph.

# Research Applications in Decoherence Studies
- Network topology effects: How does graph structure affect pathway propagation?
- Local vs distributed entanglement: Compare with global states like GHZ
- Measurement cascades: How do measurements propagate through the network?
- Quantum error correction: Foundation for topological quantum codes
"""

import numpy as np
from typing import List, Dict, Any, Tuple
from qiskit import QuantumCircuit

from .base_state import BaseState


class ClusterState(BaseState):
    """
    Cluster state preparation for graph-based network research.
    
    # Quantum Graph State Definition
    Cluster states are graph states where qubits correspond to vertices and
    entanglement bonds correspond to edges. The state is prepared by:
    1. Creating superposition on all qubits (H gates)
    2. Applying controlled-Z gates between connected neighbors
    
    # Network Topologies Supported
    - **1D Chain**: Linear nearest-neighbor connections
    - **1D Ring**: Circular chain with periodic boundary conditions
    - **2D Grid**: Rectangular lattice with nearest-neighbor connections
    - **2D Torus**: Grid with periodic boundaries in both dimensions
    
    # Research Significance
    Cluster states bridge quantum computing and network science, showing how
    local connectivity creates global entanglement. They're essential for
    studying how network topology affects decoherence pathway structure.
    
    # Educational Notes
    - Foundation of measurement-based quantum computing (one-way quantum computer)
    - Resource states for distributed quantum protocols
    - Natural testbed for studying quantum networks and connectivity
    """

    def create(self, add_barrier: bool = False) -> QuantumCircuit:
        """
        Create quantum circuit that prepares cluster state on specified graph.
        
        # Cluster State Construction Strategy
        1. **Superposition preparation**: Apply H to all qubits
           - Creates local superposition: |+⟩ = (|0⟩ + |1⟩)/√2
        2. **Entanglement creation**: Apply CZ gates between graph edges
           - CZ gate: |00⟩→|00⟩, |01⟩→|01⟩, |10⟩→|10⟩, |11⟩→-|11⟩
        3. **Result**: Highly entangled network state
        
        # Graph Topology Parameters
        - lattice: "1d" (chain) or "2d" (grid)
        - ring: Boolean for periodic boundary conditions
        - rows, cols: Dimensions for 2D lattice (rows × cols = num_qubits)
        
        Args:
            add_barrier: Add quantum barrier for circuit visualization
            
        Returns:
            QuantumCircuit: Circuit that prepares cluster state
            
        Example:
            >>> # 1D chain cluster state
            >>> cluster = ClusterState(4, {"lattice": "1d"})
            >>> circuit = cluster.create()
            
            >>> # 2D grid cluster state  
            >>> cluster_2d = ClusterState(6, {"lattice": "2d", "rows": 2, "cols": 3})
            >>> circuit_2d = cluster_2d.create()
        """
        # Validate minimum system size
        if self.num_qubits < 1:
            raise ValueError("Cluster state requires at least 1 qubit")
        
        # Parse graph parameters
        params = self.custom_params or {}
        lattice = params.get("lattice", "1d").lower()
        ring = bool(params.get("ring", False))
        
        # Validate lattice type
        if lattice not in ["1d", "2d"]:
            raise ValueError(
                f"Invalid lattice type: '{lattice}'. "
                f"Choose '1d' (chain) or '2d' (grid)"
            )
        
        # Create quantum circuit
        circuit = QuantumCircuit(self.num_qubits)
        
        # Step 1: Create superposition on all qubits
        circuit.h(range(self.num_qubits))
        
        # Step 2: Apply entangling gates based on graph topology
        if lattice == "1d":
            graph_edges, topology_info = self._create_1d_cluster(circuit, ring)
        else:  # lattice == "2d"
            graph_edges, topology_info = self._create_2d_cluster(circuit, ring, params)
        
        # Optional: Add barrier for visualization
        if add_barrier:
            circuit.barrier()
            
        # Log successful creation
        self.log_state_creation(
            f"Cluster State ({lattice.upper()})",
            {
                "entanglement_type": "graph_state_network",
                "graph_topology": lattice,
                "num_edges": len(graph_edges),
                "connectivity": topology_info["connectivity"],
                "periodic_boundaries": ring,
                **topology_info
            }
        )
        
        return circuit

    def _create_1d_cluster(self, circuit: QuantumCircuit, ring: bool) -> Tuple[List[Tuple[int, int]], Dict]:
        """
        Create 1D cluster state (chain or ring topology).
        
        Args:
            circuit: Quantum circuit to modify
            ring: Whether to add periodic boundary (last qubit to first)
            
        Returns:
            Tuple of (edge_list, topology_info)
        """
        edges = []
        
        # Connect nearest neighbors in chain
        for i in range(self.num_qubits - 1):
            circuit.cz(i, i + 1)
            edges.append((i, i + 1))
        
        # Optional: Add periodic boundary condition
        if ring and self.num_qubits > 2:
            circuit.cz(self.num_qubits - 1, 0)
            edges.append((self.num_qubits - 1, 0))
        
        topology_info = {
            "topology_type": "ring" if ring else "chain",
            "coordination_number": 2 if ring else "1-2",  # Interior vs boundary qubits
            "diameter": self.num_qubits // 2 if ring else self.num_qubits - 1,
            "connectivity": "nearest_neighbor_1d"
        }
        
        return edges, topology_info

    def _create_2d_cluster(self, circuit: QuantumCircuit, ring: bool, params: Dict) -> Tuple[List[Tuple[int, int]], Dict]:
        """
        Create 2D cluster state (grid or torus topology).
        
        Args:
            circuit: Quantum circuit to modify
            ring: Whether to add periodic boundary conditions
            params: Parameters containing rows and cols
            
        Returns:
            Tuple of (edge_list, topology_info)
        """
        # Parse 2D grid parameters
        rows = params.get("rows")
        cols = params.get("cols")
        
        # Validate 2D parameters
        if rows is None or cols is None:
            raise ValueError(
                "2D cluster state requires 'rows' and 'cols' in custom_params. "
                f"Example: custom_params={{'lattice': '2d', 'rows': 2, 'cols': 3}}"
            )
        
        if not isinstance(rows, int) or not isinstance(cols, int) or rows <= 0 or cols <= 0:
            raise ValueError(
                f"'rows' and 'cols' must be positive integers. "
                f"Got rows={rows}, cols={cols}"
            )
        
        if rows * cols != self.num_qubits:
            raise ValueError(
                f"Grid dimensions don't match qubit count: "
                f"{rows} × {cols} = {rows * cols} ≠ {self.num_qubits}"
            )
        
        edges = []
        
        # Index mapping: (row, col) → qubit_index
        def qubit_index(r: int, c: int) -> int:
            return r * cols + c
        
        # Horizontal edges (within rows)
        for r in range(rows):
            for c in range(cols - 1):
                q1, q2 = qubit_index(r, c), qubit_index(r, c + 1)
                circuit.cz(q1, q2)
                edges.append((q1, q2))
            
            # Periodic horizontal boundary (if torus)
            if ring and cols > 2:
                q1, q2 = qubit_index(r, cols - 1), qubit_index(r, 0)
                circuit.cz(q1, q2)
                edges.append((q1, q2))
        
        # Vertical edges (within columns)
        for c in range(cols):
            for r in range(rows - 1):
                q1, q2 = qubit_index(r, c), qubit_index(r + 1, c)
                circuit.cz(q1, q2)
                edges.append((q1, q2))
            
            # Periodic vertical boundary (if torus)
            if ring and rows > 2:
                q1, q2 = qubit_index(rows - 1, c), qubit_index(0, c)
                circuit.cz(q1, q2)
                edges.append((q1, q2))
        
        topology_info = {
            "topology_type": "torus" if ring else "grid",
            "grid_dimensions": (rows, cols),
            "coordination_number": 4 if ring else "2-4",  # Interior vs boundary/corner
            "diameter": (rows + cols) // 2 if ring else rows + cols - 2,
            "connectivity": "nearest_neighbor_2d"
        }
        
        return edges, topology_info

    def get_theoretical_state_vector(self) -> np.ndarray:
        """
        Calculate theoretical cluster state vector (warning: exponentially hard).
        
        # Computational Warning
        Cluster states for n>4 qubits become computationally expensive to simulate
        exactly. This method provides the theoretical construction but may be
        slow for large systems.
        
        # Implementation Strategy
        Cluster states require circuit simulation since they don't have simple
        analytical formulas like GHZ or Bell states. Uses BaseState simulation
        helper for consistent behavior and error handling.
        
        Returns:
            np.ndarray: Complex state vector of shape (2^n,)
            
        Note:
            For large cluster states, consider using the circuit directly
            rather than computing the full state vector.
        """
        # Use BaseState validation helper for consistent size checking
        self._validate_large_system("Theoretical state vector calculation", threshold=10)
        
        # Create circuit and use BaseState simulation helper
        circuit = self.create()
        return self._simulate_circuit_state_vector(circuit)

    def _estimate_circuit_depth(self) -> int:
        """
        Estimate circuit depth for cluster state preparation.
        
        # Depth Analysis by Topology
        - 1D chain: depth = 2 (H layer + CZ layer)
        - 2D grid: depth = 2 (H layer + CZ layer, CZ gates can be parallelized)
        
        Returns:
            int: Estimated circuit depth
        """
        return 2  # H gates + CZ gates (parallelizable)

    def _get_required_gates(self) -> List[str]:
        """
        Get quantum gates required for cluster state preparation.
        
        Returns:
            List[str]: Required gate names
        """
        return ["h", "cz"]  # Hadamard and controlled-Z gates

    def get_theoretical_properties(self) -> Dict[str, Any]:
        """
        Get theoretical quantum properties specific to cluster states.
        
        Returns:
            Dict with cluster state specific properties
        """
        params = self.custom_params or {}
        lattice = params.get("lattice", "1d")
        ring = bool(params.get("ring", False))
        
        # Calculate graph properties
        if lattice == "1d":
            num_edges = self.num_qubits - 1 + (1 if ring and self.num_qubits > 2 else 0)
            diameter = self.num_qubits // 2 if ring else self.num_qubits - 1
        else:  # 2d
            rows = params.get("rows", 1)
            cols = params.get("cols", self.num_qubits)
            edges_horizontal = rows * (cols - 1 + (1 if ring and cols > 2 else 0))
            edges_vertical = cols * (rows - 1 + (1 if ring and rows > 2 else 0))
            num_edges = edges_horizontal + edges_vertical
            diameter = (rows + cols) // 2 if ring else rows + cols - 2
        
        return {
            "entanglement_type": "graph_state",
            "graph_topology": lattice,
            "periodic_boundaries": ring,
            "num_edges": num_edges,
            "graph_diameter": diameter,
            "schmidt_rank": 2**(self.num_qubits-1),  # Maximal for generic graph states
            "stabilizer_generators": self.num_qubits,  # One per qubit
            "measurement_based_computing": "universal_resource_state",
            "error_correction_potential": "topological_codes" if lattice == "2d" else "limited",
            "network_connectivity": "nearest_neighbor",
            "entanglement_distribution": "local_correlations_global_state"
        }

    def get_research_context(self) -> Dict[str, Any]:
        """
        Get research context for cluster state decoherence studies.
        
        Returns:
            Dict with research context and experimental predictions
        """
        params = self.custom_params or {}
        lattice = params.get("lattice", "1d")
        
        return {
            "pathway_hypothesis": {
                "prediction": "Network topology → structured pathway propagation",
                "test_method": "Monitor how decoherence spreads through graph edges",
                "expected_signature": "Pathway propagation follows graph connectivity"
            },
            "decoherence_characteristics": {
                "propagation_pattern": "Along graph edges",
                "dimensionality_effects": "1D: linear propagation, 2D: area spreading",
                "boundary_effects": "Different behavior at graph boundaries vs interior",
                "network_robustness": "Fault tolerance depends on graph connectivity"
            },
            "research_applications": {
                "measurement_based_computing": "Foundation for one-way quantum computer",
                "quantum_networks": "Model for distributed quantum systems",
                "error_correction": "Basis for topological quantum codes",
                "network_science": "Quantum analog of classical network phenomena"
            },
            "experimental_predictions": {
                "vs_ghz_states": "Local vs global entanglement structure differences",
                "topology_dependence": "1D chain vs 2D grid pathway differences",
                "scaling_behavior": "How pathway structure scales with network size",
                "fault_tolerance": "Error correction capabilities of different topologies"
            },
            "pathway_predictions": {
                "early_stage": "Local decoherence near initial error sites",
                "propagation_phase": "Decoherence spreads along graph edges",
                "late_stage": "Global network decoherence patterns",
                f"{lattice}_specific": f"Dimensional effects of {lattice} topology"
            }
        }

    def __str__(self) -> str:
        """Human-readable description for educational purposes."""
        params = self.custom_params or {}
        lattice = params.get("lattice", "1d")
        ring = bool(params.get("ring", False))
        
        if lattice == "1d":
            topology = "ring" if ring else "chain"
            return f"Cluster state: {self.num_qubits}-qubit {topology} [graph entanglement]"
        else:
            rows = params.get("rows", 1)
            cols = params.get("cols", self.num_qubits)
            topology = "torus" if ring else "grid"
            return f"Cluster state: {rows}×{cols} {topology} [graph entanglement]"