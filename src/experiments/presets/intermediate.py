"""
Intermediate experiments for the Quantum Experiment Framework.

This module contains intermediate-level experiments designed for
users with some quantum computing experience.
"""

from typing import Dict, Any

INTERMEDIATE_EXPERIMENTS: Dict[str, Dict[str, Any]] = {
    "w_phase_flip": {
        "name": "W State with Phase Flip",
        "description": "3-qubit W state with phase flip noise - study phase decoherence",
        "category": "entanglement",
        "difficulty": "intermediate",
        "config": {
            "num_qubits": 3,
            "state_type": "W",
            "noise_type": "PHASE_FLIP",
            "noise_enabled": True,
            "shots": 1024,
            "sim_mode": "qasm",
            "visualization_type": "plot",
            "error_rate": 0.15,
        },
    },
    "cluster_basic": {
        "name": "Cluster State Basics",
        "description": "3-qubit cluster state - topological quantum computing",
        "category": "topological",
        "difficulty": "intermediate",
        "config": {
            "num_qubits": 3,
            "state_type": "CLUSTER",
            "noise_type": "DEPOLARIZING",
            "noise_enabled": False,
            "shots": 1024,
            "sim_mode": "qasm",
            "visualization_type": "plot",
        },
    },
    "larger_ghz": {
        "name": "Larger GHZ State",
        "description": "4-qubit GHZ state - scaling entanglement",
        "category": "scaling",
        "difficulty": "intermediate",
        "config": {
            "num_qubits": 4,
            "state_type": "GHZ",
            "noise_type": "DEPOLARIZING",
            "noise_enabled": True,
            "shots": 1024,
            "sim_mode": "qasm",
            "visualization_type": "plot",
            "error_rate": 0.1,
        },
    },
}
