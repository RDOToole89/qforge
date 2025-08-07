"""
Research experiments for the Quantum Experiment Framework.

This module contains cutting-edge research experiments designed for
quantum computing research and advanced studies.
"""

from typing import Dict, Any

RESEARCH_EXPERIMENTS: Dict[str, Dict[str, Any]] = {
    "quantum_advantage": {
        "name": "Quantum Advantage Study",
        "description": "6-qubit GHZ state - pushing the limits of quantum simulation",
        "category": "research",
        "difficulty": "research",
        "config": {
            "num_qubits": 6,
            "state_type": "GHZ",
            "noise_type": "DEPOLARIZING",
            "noise_enabled": True,
            "shots": 4096,
            "sim_mode": "qasm",
            "visualization_type": "plot",
            "error_rate": 0.02,
        },
    },
    "topological_robustness": {
        "name": "Topological Robustness Analysis",
        "description": "Cluster state with multiple noise types - study topological protection",
        "category": "research",
        "difficulty": "research",
        "config": {
            "num_qubits": 4,
            "state_type": "CLUSTER",
            "noise_type": "THERMAL_RELAXATION",
            "noise_enabled": True,
            "shots": 2048,
            "sim_mode": "qasm",
            "visualization_type": "plot",
            "t1": 50e-6,
            "t2": 40e-6,
        },
    },
    "entanglement_scaling": {
        "name": "Entanglement Scaling Study",
        "description": "W state with varying system sizes - study entanglement scaling",
        "category": "research",
        "difficulty": "research",
        "config": {
            "num_qubits": 4,
            "state_type": "W",
            "noise_type": "PHASE_FLIP",
            "noise_enabled": True,
            "shots": 2048,
            "sim_mode": "qasm",
            "visualization_type": "plot",
            "error_rate": 0.1,
        },
    },
}
