"""
Advanced experiments for the Quantum Experiment Framework.

This module contains advanced experiments designed for
experienced quantum computing researchers.
"""

from typing import Dict, Any

ADVANCED_EXPERIMENTS: Dict[str, Dict[str, Any]] = {
    "cluster_thermal": {
        "name": "Cluster State with Thermal Relaxation",
        "description": "3-qubit cluster state with thermal relaxation - realistic quantum hardware",
        "category": "topological",
        "difficulty": "advanced",
        "config": {
            "num_qubits": 3,
            "state_type": "CLUSTER",
            "noise_type": "THERMAL_RELAXATION",
            "noise_enabled": True,
            "shots": 1024,
            "sim_mode": "qasm",
            "visualization_type": "plot",
            "t1": 100e-6,
            "t2": 80e-6,
        },
    },
    "large_ghz": {
        "name": "Large GHZ State",
        "description": "5-qubit GHZ state - challenging entanglement scaling",
        "category": "scaling",
        "difficulty": "advanced",
        "config": {
            "num_qubits": 5,
            "state_type": "GHZ",
            "noise_type": "DEPOLARIZING",
            "noise_enabled": True,
            "shots": 2048,
            "sim_mode": "qasm",
            "visualization_type": "plot",
            "error_rate": 0.05,
        },
    },
    "complex_dynamics": {
        "name": "Complex Quantum Dynamics",
        "description": "GHZ state with amplitude damping - study energy dissipation",
        "category": "dynamics",
        "difficulty": "advanced",
        "config": {
            "num_qubits": 3,
            "state_type": "GHZ",
            "noise_type": "AMPLITUDE_DAMPING",
            "noise_enabled": True,
            "shots": 1024,
            "sim_mode": "qasm",
            "visualization_type": "plot",
            "error_rate": 0.1,
        },
    },
}
