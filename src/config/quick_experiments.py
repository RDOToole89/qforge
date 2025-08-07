"""
Quick experiment configurations for the Quantum Experiment Interactive Runner.

This module provides predefined experiment configurations that users can easily
select from the CLI. Users can extend this by adding their own experiment
configurations to the QUICK_EXPERIMENTS dictionary.

Example usage:
    from src.config.quick_experiments import QUICK_EXPERIMENTS
    QUICK_EXPERIMENTS["6"] = {
        "name": "My Custom Experiment",
        "description": "My custom quantum experiment",
        "config": {
            "num_qubits": 4,
            "state_type": "GHZ",
            "noise_type": "DEPOLARIZING",
            "noise_enabled": True,
            "shots": 2048,
            "sim_mode": "qasm",
            "visualization_type": "plot",
            "error_rate": 0.05
        }
    }
"""

from typing import Dict, Any

# ==========================
# 🚀 Quick Experiment Configurations
# ==========================

QUICK_EXPERIMENTS: Dict[str, Dict[str, Any]] = {
    "1": {
        "name": "GHZ State with Depolarizing Noise",
        "description": "3-qubit GHZ state with depolarizing noise (classic quantum entanglement)",
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
    "2": {
        "name": "W State with Phase Flip Noise",
        "description": "3-qubit W state with phase flip noise (symmetric entanglement)",
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
    "3": {
        "name": "Cluster State with Thermal Relaxation",
        "description": "3-qubit cluster state with thermal relaxation (topological quantum)",
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
    "4": {
        "name": "Pure GHZ State (No Noise)",
        "description": "3-qubit GHZ state without noise (perfect entanglement)",
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
    "5": {
        "name": "Density Matrix Analysis",
        "description": "GHZ state density matrix analysis (theoretical quantum state)",
        "category": "analysis",
        "difficulty": "intermediate",
        "config": {
            "num_qubits": 3,
            "state_type": "GHZ",
            "noise_type": "DEPOLARIZING",
            "noise_enabled": True,
            "shots": 1024,
            "sim_mode": "density",
            "visualization_type": "plot",
            "error_rate": 0.1,
            "show_real": True,
            "show_imag": False,
        },
    },
    "6": {
        "name": "Multi-Qubit GHZ (4 qubits)",
        "description": "4-qubit GHZ state with depolarizing noise (larger system)",
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
            "error_rate": 0.08,
        },
    },
    "7": {
        "name": "Hypergraph Correlation Analysis",
        "description": "GHZ state with hypergraph visualization (correlation analysis)",
        "category": "analysis",
        "difficulty": "advanced",
        "config": {
            "num_qubits": 3,
            "state_type": "GHZ",
            "noise_type": "DEPOLARIZING",
            "noise_enabled": True,
            "shots": 1024,
            "sim_mode": "qasm",
            "visualization_type": "hypergraph",
            "error_rate": 0.12,
            "hypergraph_config": {
                "max_order": 2,
                "threshold": 0.1,
                "symmetry_analysis": True,
                "plot_bloch": True,
                "plot_transitions": False,
            },
        },
    },
    "8": {
        "name": "Time-Stepped Decoherence",
        "description": "GHZ state with time-stepped noise analysis (decoherence study)",
        "category": "dynamics",
        "difficulty": "advanced",
        "config": {
            "num_qubits": 3,
            "state_type": "GHZ",
            "noise_type": "DEPOLARIZING",
            "noise_enabled": True,
            "shots": 1024,
            "sim_mode": "qasm",
            "visualization_type": "plot",
            "error_rate": 0.1,
            "noise_stepped": True,
            "noise_start": 0.0,
            "noise_end": 0.3,
            "noise_steps": 10,
        },
    },
}

# ==========================
# 🎯 Experiment Categories
# ==========================

EXPERIMENT_CATEGORIES = {
    "entanglement": "Quantum entanglement experiments",
    "topological": "Topological quantum states",
    "analysis": "Advanced analysis and visualization",
    "scaling": "Multi-qubit scaling experiments",
    "dynamics": "Time-dependent quantum dynamics",
}

DIFFICULTY_LEVELS = {
    "beginner": "Suitable for quantum computing beginners",
    "intermediate": "Requires some quantum computing knowledge",
    "advanced": "For experienced quantum researchers",
}

# ==========================
# 🔧 Utility Functions
# ==========================


def get_experiments_by_category(category: str) -> Dict[str, Dict[str, Any]]:
    """
    Returns experiments filtered by category.

    Args:
        category (str): Category to filter by

    Returns:
        Dict[str, Dict[str, Any]]: Filtered experiments
    """
    return {
        key: exp
        for key, exp in QUICK_EXPERIMENTS.items()
        if exp.get("category") == category
    }


def get_experiments_by_difficulty(difficulty: str) -> Dict[str, Dict[str, Any]]:
    """
    Returns experiments filtered by difficulty level.

    Args:
        difficulty (str): Difficulty level to filter by

    Returns:
        Dict[str, Dict[str, Any]]: Filtered experiments
    """
    return {
        key: exp
        for key, exp in QUICK_EXPERIMENTS.items()
        if exp.get("difficulty") == difficulty
    }


def add_custom_experiment(
    key: str,
    name: str,
    description: str,
    config: Dict[str, Any],
    category: str = "custom",
    difficulty: str = "intermediate",
) -> None:
    """
    Adds a custom experiment to the quick experiments.

    Args:
        key (str): Unique key for the experiment
        name (str): Display name
        description (str): Description of the experiment
        config (Dict[str, Any]): Experiment configuration
        category (str): Experiment category
        difficulty (str): Difficulty level
    """
    QUICK_EXPERIMENTS[key] = {
        "name": name,
        "description": description,
        "category": category,
        "difficulty": difficulty,
        "config": config,
    }


def validate_experiment_config(config: Dict[str, Any]) -> bool:
    """
    Validates an experiment configuration.

    Args:
        config (Dict[str, Any]): Experiment configuration

    Returns:
        bool: True if valid, False otherwise
    """
    required_keys = [
        "num_qubits",
        "state_type",
        "noise_type",
        "noise_enabled",
        "shots",
        "sim_mode",
        "visualization_type",
    ]

    for key in required_keys:
        if key not in config:
            return False

    # Validate specific values
    if config["num_qubits"] < 1:
        return False

    if config["shots"] < 1:
        return False

    return True


def get_experiment_info(key: str) -> Dict[str, Any]:
    """
    Returns detailed information about an experiment.

    Args:
        key (str): Experiment key

    Returns:
        Dict[str, Any]: Experiment information
    """
    if key not in QUICK_EXPERIMENTS:
        return {}

    exp = QUICK_EXPERIMENTS[key]
    return {
        "key": key,
        "name": exp["name"],
        "description": exp["description"],
        "category": exp.get("category", "unknown"),
        "difficulty": exp.get("difficulty", "unknown"),
        "config": exp["config"],
        "category_description": EXPERIMENT_CATEGORIES.get(exp.get("category", ""), ""),
        "difficulty_description": DIFFICULTY_LEVELS.get(exp.get("difficulty", ""), ""),
    }
