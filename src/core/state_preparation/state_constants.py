"""State Registry for Quantum Decoherence Research Framework.

# State Class Registry Pattern
Centralized registry of all available quantum state preparation classes
for structured decoherence pathway research. Implements the Registry Pattern
to provide clean separation between state implementation and factory logic.

# Educational Purpose
This registry demonstrates the Registry Pattern in quantum computing applications,
showing how to organize different quantum state types systematically while
maintaining loose coupling between components.

# Research Framework Integration
Each registered state class implements different entanglement topologies:
- GHZ: Global multipartite entanglement for pathway propagation studies
- Bell: Fundamental bipartite entanglement for baseline measurements
- W: Symmetric multipartite entanglement for robustness analysis
- Cluster: Graph-based local correlations for network decoherence patterns
- Superposition: Non-entangled product states for control experiments
- Custom: Maximum flexibility for novel research and algorithm development

# Design Benefits
- Extensibility: New state types can be added without modifying factory code
- Discoverability: Available states are programmatically accessible
- Type Safety: Centralized mapping ensures consistent state class usage
- Separation of Concerns: Registry logic separated from state preparation logic
"""

from .base_state import BaseState
from .bell_state import BellState
from .cluster_state import ClusterState
from .custom_state import CustomState
from .ghz_state import GHZState
from .superposition_state import SuperpositionState
from .w_state import WState

# Central registry mapping state type names to implementation classes
STATE_CLASSES: dict[str, type[BaseState]] = {
    "GHZ": GHZState,  # Global entanglement: |000⟩ + |111⟩
    "BELL": BellState,  # Bipartite entanglement: Bell states
    "W": WState,  # Symmetric multipartite: |100⟩ + |010⟩ + |001⟩
    "CLUSTER": ClusterState,  # Graph-based network: local correlations
    "SUPERPOSITION": SuperpositionState,  # Product states: |+⟩^n (no entanglement)
    "CUSTOM": CustomState,  # Advanced research: arbitrary circuits
}


def get_state_class(state_type: str) -> type[BaseState]:
    """Get state class for given state type with validation.

    # Registry Lookup Pattern
    Provides type-safe access to state classes with clear error messages
    for invalid state types. Enables dynamic state creation while maintaining
    compile-time type safety.

    Args:
        state_type: Name of quantum state type (case-sensitive)

    Returns:
        Type[BaseState]: State class for the requested type

    Raises:
        ValueError: If state type is not registered

    Example:
        >>> state_class = get_state_class("GHZ")
        >>> state = state_class(3)  # Create 3-qubit GHZ state
    """
    if state_type not in STATE_CLASSES:
        available = list(STATE_CLASSES.keys())
        raise ValueError(f"Unknown state type: '{state_type}'. Available types: {available}")

    return STATE_CLASSES[state_type]


def get_available_states() -> list[str]:
    """Get list of all available state types.

    # State Discovery Pattern
    Enables programmatic discovery of available quantum state types
    for user interfaces, documentation generation, and validation.

    Returns:
        List[str]: Sorted list of available state type names

    Example:
        >>> states = get_available_states()
        >>> print(f"Available states: {states}")
        Available states: ['BELL', 'CLUSTER', 'CUSTOM', 'GHZ', 'SUPERPOSITION', 'W']
    """
    return sorted(STATE_CLASSES.keys())


def get_state_info() -> dict[str, dict[str, str]]:
    """Get comprehensive information about all registered state types.

    # State Documentation Pattern
    Provides structured information about each state type for documentation,
    user interfaces, and educational purposes.

    Returns:
        Dict mapping state names to their characteristics

    Example:
        >>> info = get_state_info()
        >>> print(info["GHZ"]["description"])
        Global multipartite entanglement state
    """
    return {
        "GHZ": {
            "description": "Global multipartite entanglement state",
            "formula": "|000⟩ + |111⟩ (normalized)",
            "entanglement_type": "maximal_multipartite",
            "research_focus": "pathway_propagation_studies",
            "typical_qubits": "3-10",
        },
        "BELL": {
            "description": "Fundamental bipartite entanglement states",
            "formula": "Four Bell states: |Φ±⟩, |Ψ±⟩",
            "entanglement_type": "maximal_bipartite",
            "research_focus": "baseline_entanglement_analysis",
            "typical_qubits": "2",
        },
        "W": {
            "description": "Symmetric multipartite entanglement state",
            "formula": "|100⟩ + |010⟩ + |001⟩ (normalized)",
            "entanglement_type": "symmetric_multipartite",
            "research_focus": "robustness_vs_fragility_studies",
            "typical_qubits": "3-8",
        },
        "CLUSTER": {
            "description": "Graph-based quantum network states",
            "formula": "H⊗n followed by CZ on graph edges",
            "entanglement_type": "graph_state_network",
            "research_focus": "topology_dependent_pathways",
            "typical_qubits": "4-20",
        },
        "SUPERPOSITION": {
            "description": "Product superposition states (no entanglement)",
            "formula": "|+⟩^n = (H⊗n)|0⟩^n",
            "entanglement_type": "none_separable",
            "research_focus": "control_baseline_experiments",
            "typical_qubits": "1-10",
        },
        "CUSTOM": {
            "description": "User-defined arbitrary quantum circuits",
            "formula": "User-specified gate sequences",
            "entanglement_type": "user_defined",
            "research_focus": "novel_experiments_and_algorithms",
            "typical_qubits": "1-20",
        },
    }


def validate_state_registry() -> bool:
    """Validate the integrity of the state registry.

    # Registry Validation Pattern
    Ensures all registered state classes properly implement the BaseState
    interface and can be instantiated correctly.

    Returns:
        bool: True if registry is valid

    Raises:
        TypeError: If any registered class doesn't inherit from BaseState
        RuntimeError: If any state class has implementation issues
    """
    for state_name, state_class in STATE_CLASSES.items():
        # Check inheritance
        if not issubclass(state_class, BaseState):
            raise TypeError(f"State class {state_name} ({state_class}) must inherit from BaseState")

        # Check required methods exist
        required_methods = ["create", "get_theoretical_properties", "get_research_context"]
        for method in required_methods:
            if not hasattr(state_class, method):
                raise RuntimeError(f"State class {state_name} missing required method: {method}")

    return True


# Validate registry at import time to catch configuration errors early
validate_state_registry()
