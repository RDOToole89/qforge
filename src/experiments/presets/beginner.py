"""
Beginner experiments for the Quantum Experiment Framework.

This module contains simple, educational experiments designed for
beginners learning quantum computing concepts.
"""

from typing import Dict, Any

BEGINNER_EXPERIMENTS: Dict[str, Dict[str, Any]] = {
    "ghz_basic": {
        "name": "GHZ State Basics",
        "description": "3-qubit GHZ state - the classic quantum entanglement experiment",
        "category": "entanglement",
        "difficulty": "beginner",
        "config": {
            "num_qubits": 3,
            "state_type": "GHZ",
            "noise_type": "DEPOLARIZING",
            "noise_enabled": False,
            "shots": 1024,
            "sim_mode": "qasm",
            "visualization_type": "plot",
        },
    },
    "ghz_noise": {
        "name": "GHZ State with Noise",
        "description": "3-qubit GHZ state with depolarizing noise - see how noise affects entanglement",
        "category": "entanglement",
        "difficulty": "beginner",
        "config": {
            "num_qubits": 3,
            "state_type": "GHZ",
            "noise_type": "DEPOLARIZING",
            "noise_enabled": True,
            "shots": 1024,
            "sim_mode": "qasm",
            "visualization_type": "plot",
            "error_rate": 0.1,
        },
    },
    "w_basic": {
        "name": "W State Basics",
        "description": "3-qubit W state - symmetric entanglement pattern",
        "category": "entanglement",
        "difficulty": "beginner",
        "config": {
            "num_qubits": 3,
            "state_type": "W",
            "noise_type": "DEPOLARIZING",
            "noise_enabled": False,
            "shots": 1024,
            "sim_mode": "qasm",
            "visualization_type": "plot",
        },
    },
    "density_analysis": {
        "name": "Density Matrix Analysis",
        "description": "GHZ state density matrix analysis - theoretical quantum state study",
        "category": "analysis",
        "difficulty": "beginner",
        "config": {
            "num_qubits": 3,
            "state_type": "GHZ",
            "noise_type": "DEPOLARIZING",
            "noise_enabled": False,
            "shots": 1,
            "sim_mode": "density",
            "visualization_type": "plot",
        },
    },
    "small_ghz": {
        "name": "Small GHZ State",
        "description": "2-qubit GHZ state - simplest entanglement experiment",
        "category": "entanglement",
        "difficulty": "beginner",
        "config": {
            "num_qubits": 2,
            "state_type": "GHZ",
            "noise_type": "DEPOLARIZING",
            "noise_enabled": False,
            "shots": 1024,
            "sim_mode": "qasm",
            "visualization_type": "plot",
        },
    },
}
