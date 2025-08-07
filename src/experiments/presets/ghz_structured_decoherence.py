"""
GHZ Structured Decoherence Research Experiments.

This module contains the reference implementation for studying structured
decoherence in GHZ states - investigating whether quantum noise exhibits
non-random, pattern-biased deviations from ideal distributions.

Research Hypothesis:
    Quantum decoherence is not purely stochastic, but follows preferred
    pathways - structured, constraint-based transitions that may reveal
    deeper computational structure.

Author: Independent Quantum Research
Created: 2025-01-07
"""

from typing import Dict, Any, List

# Core GHZ structured decoherence experiment
GHZ_STRUCTURED_DECOHERENCE_EXPERIMENTS: Dict[str, Dict[str, Any]] = {

    # Primary reference experiment
    "ghz_structured_decoherence_ref": {
        "name": "GHZ Structured Decoherence (Reference)",
        "description": "3-qubit GHZ with 5% depolarizing noise - reference experiment for structured decoherence research",
        "category": "research",
        "difficulty": "research",
        "research_type": "structured_decoherence",
        "hypothesis": "Decoherence exhibits structured preference patterns in bitstring outcomes",
        "config": {
            "num_qubits": 3,
            "state_type": "GHZ",
            "noise_type": "DEPOLARIZING",
            "noise_enabled": True,
            "shots": 4096,  # Higher shot count for statistical significance
            "sim_mode": "qasm",
            "visualization_type": "research",
            "error_rate": 0.05,  # 5% depolarizing noise
            # Research parameters
            "enable_research_metrics": True,
            "track_convergence": True,
            "multiple_runs": 3,  # For reproducibility analysis
        },
        "expected_outcomes": {
            "ideal_distribution": {"000": 0.5, "111": 0.5},
            "max_entropy": 1.0,  # For 2 equally likely outcomes
            "baseline_kl_divergence": 0.0,
        },
        "research_questions": [
            "Does decoherence produce uniform errors across all non-ideal bitstrings?",
            "Are certain bit-flip patterns (e.g., 001, 110) preferred over others?",
            "Does qubit-wise collapse bias reveal asymmetric decoherence pressure?",
            "Are correlation patterns reproducible across multiple runs?"
        ]
    },

    # Parameter sweep experiments
    "ghz_decoherence_sweep_low": {
        "name": "GHZ Decoherence Sweep (Low Noise)",
        "description": "1% depolarizing noise - minimal decoherence regime",
        "category": "research",
        "difficulty": "research",
        "research_type": "parameter_sweep",
        "config": {
            "num_qubits": 3,
            "state_type": "GHZ",
            "noise_type": "DEPOLARIZING",
            "noise_enabled": True,
            "shots": 8192,  # Higher precision for subtle effects
            "sim_mode": "qasm",
            "visualization_type": "research",
            "error_rate": 0.01,  # 1% noise
            "enable_research_metrics": True,
            "multiple_runs": 5,
        }
    },

    "ghz_decoherence_sweep_med": {
        "name": "GHZ Decoherence Sweep (Medium Noise)",
        "description": "10% depolarizing noise - intermediate decoherence regime",
        "category": "research",
        "difficulty": "research",
        "research_type": "parameter_sweep",
        "config": {
            "num_qubits": 3,
            "state_type": "GHZ",
            "noise_type": "DEPOLARIZING",
            "noise_enabled": True,
            "shots": 4096,
            "sim_mode": "qasm",
            "visualization_type": "research",
            "error_rate": 0.10,  # 10% noise
            "enable_research_metrics": True,
            "multiple_runs": 3,
        }
    },

    "ghz_decoherence_sweep_high": {
        "name": "GHZ Decoherence Sweep (High Noise)",
        "description": "20% depolarizing noise - strong decoherence regime",
        "category": "research",
        "difficulty": "research",
        "research_type": "parameter_sweep",
        "config": {
            "num_qubits": 3,
            "state_type": "GHZ",
            "noise_type": "DEPOLARIZING",
            "noise_enabled": True,
            "shots": 2048,  # Faster runs in high-noise regime
            "sim_mode": "qasm",
            "visualization_type": "research",
            "error_rate": 0.20,  # 20% noise
            "enable_research_metrics": True,
            "multiple_runs": 3,
        }
    },

    # Alternative noise model experiments
    "ghz_phase_damping": {
        "name": "GHZ Phase Damping Analysis",
        "description": "GHZ with phase damping noise - pure dephasing effects",
        "category": "research",
        "difficulty": "research",
        "research_type": "noise_comparison",
        "config": {
            "num_qubits": 3,
            "state_type": "GHZ",
            "noise_type": "PHASE_DAMPING",
            "noise_enabled": True,
            "shots": 4096,
            "sim_mode": "qasm",
            "visualization_type": "research",
            "error_rate": 0.05,
            "enable_research_metrics": True,
            "multiple_runs": 3,
        }
    },

    "ghz_amplitude_damping": {
        "name": "GHZ Amplitude Damping Analysis",
        "description": "GHZ with amplitude damping - energy relaxation effects",
        "category": "research",
        "difficulty": "research",
        "research_type": "noise_comparison",
        "config": {
            "num_qubits": 3,
            "state_type": "GHZ",
            "noise_type": "AMPLITUDE_DAMPING",
            "noise_enabled": True,
            "shots": 4096,
            "sim_mode": "qasm",
            "visualization_type": "research",
            "error_rate": 0.05,
            "enable_research_metrics": True,
            "multiple_runs": 3,
        }
    },

    # Control experiments
    "ghz_perfect_control": {
        "name": "GHZ Perfect Control",
        "description": "Noiseless GHZ state - baseline for comparison",
        "category": "research",
        "difficulty": "research",
        "research_type": "control",
        "config": {
            "num_qubits": 3,
            "state_type": "GHZ",
            "noise_type": "DEPOLARIZING",
            "noise_enabled": False,  # No noise
            "shots": 4096,
            "sim_mode": "qasm",
            "visualization_type": "research",
            "enable_research_metrics": True,
            "multiple_runs": 3,
        }
    },

    # Scaling experiments
    "ghz_4qubit_structured": {
        "name": "4-Qubit GHZ Structured Decoherence",
        "description": "Scaling analysis - 4-qubit GHZ with structured decoherence",
        "category": "research",
        "difficulty": "research",
        "research_type": "scaling",
        "config": {
            "num_qubits": 4,
            "state_type": "GHZ",
            "noise_type": "DEPOLARIZING",
            "noise_enabled": True,
            "shots": 8192,  # More shots for larger state space
            "sim_mode": "qasm",
            "visualization_type": "research",
            "error_rate": 0.05,
            "enable_research_metrics": True,
            "multiple_runs": 3,
        }
    },

    # High-precision convergence test
    "ghz_convergence_test": {
        "name": "GHZ Convergence Test",
        "description": "High-shot convergence analysis for statistical validation",
        "category": "research",
        "difficulty": "research",
        "research_type": "convergence",
        "config": {
            "num_qubits": 3,
            "state_type": "GHZ",
            "noise_type": "DEPOLARIZING",
            "noise_enabled": True,
            "shots": 16384,  # Very high shot count
            "sim_mode": "qasm",
            "visualization_type": "research",
            "error_rate": 0.05,
            "enable_research_metrics": True,
            "multiple_runs": 1,  # Single high-precision run
        }
    }
}


def get_ghz_research_batch(noise_levels: List[float] = None) -> List[Dict[str, Any]]:
    """
    Generate a batch of GHZ experiments across different noise levels.

    This function creates a systematic parameter sweep for structured
    decoherence analysis across multiple noise regimes.

    Args:
        noise_levels: List of noise levels to test (default: [0.01, 0.05, 0.10, 0.20])

    Returns:
        List of experiment configurations for batch execution
    """
    if noise_levels is None:
        noise_levels = [0.01, 0.05, 0.10, 0.20]

    batch_experiments = []

    for i, noise_level in enumerate(noise_levels):
        exp_config = {
            "name": f"GHZ Batch {i+1} (ε={noise_level:.2f})",
            "description": f"Batch experiment: GHZ with {noise_level*100:.1f}% depolarizing noise",
            "category": "research",
            "difficulty": "research",
            "research_type": "batch_sweep",
            "batch_id": f"ghz_sweep_{i+1}",
            "config": {
                "num_qubits": 3,
                "state_type": "GHZ",
                "noise_type": "DEPOLARIZING",
                "noise_enabled": True,
                "shots": 4096,
                "sim_mode": "qasm",
                "visualization_type": "research",
                "error_rate": noise_level,
                "enable_research_metrics": True,
                "multiple_runs": 3,
            }
        }
        batch_experiments.append(exp_config)

    return batch_experiments


def get_ideal_ghz_distribution(num_qubits: int) -> Dict[str, float]:
    """
    Get the ideal probability distribution for a GHZ state.

    For an n-qubit GHZ state |GHZ⟩ = (|00...0⟩ + |11...1⟩)/√2,
    the ideal distribution has equal probability (0.5) for the
    all-zeros and all-ones states, and zero probability elsewhere.

    Args:
        num_qubits: Number of qubits in the GHZ state

    Returns:
        Dictionary mapping bitstrings to ideal probabilities
    """
    ideal_dist = {}

    # Generate all possible bitstrings
    for i in range(2**num_qubits):
        bitstring = format(i, f'0{num_qubits}b')
        if bitstring == '0' * num_qubits or bitstring == '1' * num_qubits:
            ideal_dist[bitstring] = 0.5  # Equal superposition
        else:
            ideal_dist[bitstring] = 0.0  # No probability for other states

    return ideal_dist


# Export the experiments
__all__ = [
    "GHZ_STRUCTURED_DECOHERENCE_EXPERIMENTS",
    "get_ghz_research_batch",
    "get_ideal_ghz_distribution"
]
