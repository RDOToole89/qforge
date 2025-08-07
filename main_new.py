#!/usr/bin/env python3
"""
Quantum Experiment Framework - Main Entry Point

A research-grade quantum experiment framework for conducting quantum computing
experiments with configurable parameters, noise models, and visualization capabilities.

This is the new modular version with separated CLI components.
"""

import sys
import warnings

# Suppress Qiskit deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Set matplotlib backend for interactive plotting
import matplotlib

matplotlib.use("TkAgg")

from src.cli.main import cli


def main():
    """
    Main entry point for the Quantum Experiment Framework.

    This function sets up the environment and launches the CLI.
    """
    try:
        cli()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
