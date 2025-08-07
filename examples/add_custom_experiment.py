#!/usr/bin/env python3
"""
Example script showing how to add custom experiments to the Quantum Experiment Runner.

This demonstrates how users can easily extend the framework with their own
experiment configurations without modifying the core code.

Usage:
    python examples/add_custom_experiment.py
"""

import sys
import os

# Add the project root to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.config.quick_experiments import (
    QUICK_EXPERIMENTS,
    add_custom_experiment,
    validate_experiment_config,
    get_experiment_info,
)


def add_my_custom_experiments():
    """
    Example function showing how to add custom experiments.
    """
    print("🔧 Adding custom experiments to the framework...")

    # Example 1: Add a custom Bell state experiment
    add_custom_experiment(
        key="9",
        name="Bell State with Amplitude Damping",
        description="2-qubit Bell state with amplitude damping noise (quantum communication)",
        category="entanglement",
        difficulty="beginner",
        config={
            "num_qubits": 2,
            "state_type": "GHZ",  # GHZ for 2 qubits creates a Bell state
            "noise_type": "AMPLITUDE_DAMPING",
            "noise_enabled": True,
            "shots": 1024,
            "sim_mode": "qasm",
            "visualization_type": "plot",
            "error_rate": 0.05,
        },
    )

    # Example 2: Add a custom research experiment
    add_custom_experiment(
        key="10",
        name="High-Fidelity GHZ (Research)",
        description="5-qubit GHZ state with low noise for research applications",
        category="scaling",
        difficulty="advanced",
        config={
            "num_qubits": 5,
            "state_type": "GHZ",
            "noise_type": "DEPOLARIZING",
            "noise_enabled": True,
            "shots": 2048,
            "sim_mode": "qasm",
            "visualization_type": "plot",
            "error_rate": 0.02,
        },
    )

    # Example 3: Add a custom analysis experiment
    add_custom_experiment(
        key="11",
        name="W State Density Analysis",
        description="W state density matrix with detailed analysis",
        category="analysis",
        difficulty="intermediate",
        config={
            "num_qubits": 3,
            "state_type": "W",
            "noise_type": "PHASE_FLIP",
            "noise_enabled": True,
            "shots": 1024,
            "sim_mode": "density",
            "visualization_type": "plot",
            "error_rate": 0.1,
            "show_real": True,
            "show_imag": True,
        },
    )

    print("✅ Custom experiments added successfully!")


def validate_my_experiments():
    """
    Example function showing how to validate experiment configurations.
    """
    print("\n🔍 Validating experiment configurations...")

    # Get all experiments including the ones we just added
    for key in ["9", "10", "11"]:
        if key in QUICK_EXPERIMENTS:
            exp = QUICK_EXPERIMENTS[key]
            config = exp["config"]

            is_valid = validate_experiment_config(config)
            status = "✅ Valid" if is_valid else "❌ Invalid"

            print(f"Experiment {key}: {exp['name']} - {status}")

            if is_valid:
                info = get_experiment_info(key)
                print(f"   Category: {info['category']}")
                print(f"   Difficulty: {info['difficulty']}")
                print(f"   Qubits: {config['num_qubits']}")
                print(f"   Shots: {config['shots']}")


def show_all_experiments():
    """
    Display all available experiments including custom ones.
    """
    print("\n📋 All Available Experiments:")
    print("=" * 80)

    for key, exp in QUICK_EXPERIMENTS.items():
        config = exp["config"]
        print(f"{key:2}. {exp['name']}")
        print(f"    Description: {exp['description']}")
        print(f"    Category: {exp.get('category', 'unknown')}")
        print(f"    Difficulty: {exp.get('difficulty', 'unknown')}")
        print(
            f"    Config: {config['num_qubits']} qubits, {config['state_type']}, {config['noise_type']}"
        )
        print()


def main():
    """
    Main function demonstrating custom experiment addition.
    """
    print("🚀 Quantum Experiment Framework - Custom Experiment Example")
    print("=" * 60)

    # Add custom experiments
    add_my_custom_experiments()

    # Validate the experiments
    validate_my_experiments()

    # Show all experiments
    show_all_experiments()

    print("\n💡 To use these custom experiments:")
    print("1. Run the main simulator: python main.py")
    print("2. Choose 's' for skip/default settings")
    print("3. Select option 9, 10, or 11 for your custom experiments")
    print("\n🔧 To add your own experiments:")
    print("1. Import the quick_experiments module")
    print("2. Use add_custom_experiment() function")
    print("3. Validate your configuration with validate_experiment_config()")


if __name__ == "__main__":
    main()
