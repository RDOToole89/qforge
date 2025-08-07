#!/usr/bin/env python3
"""
Quantum Experiment Framework - New Modular Entry Point

This is the new modular entry point for the quantum experiment framework.
It uses the experiment manager and smart matplotlib backend configuration.

Usage:
    python3 main_new.py                    # Interactive CLI mode
    python3 main_new.py --list            # List available experiments
    python3 main_new.py --run <exp_name>  # Run specific experiment
    QUANTUM_INTERACTIVE=false python3 main_new.py  # Non-interactive mode
"""

import os
import sys
import logging
from typing import Optional, Dict, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment() -> None:
    """Set up environment for quantum experiments."""
    # Set interactive mode for CLI
    if not os.environ.get('QUANTUM_INTERACTIVE'):
        os.environ['QUANTUM_INTERACTIVE'] = 'true'

    logger.info("🚀 Initializing Quantum Experiment Framework")

def import_core_modules():
    """Import core modules with error handling."""
    try:
        from src.experiments import get_experiment_manager
        from src.core import ExperimentRunner
        from src.config.settings import settings
        from src.visualization import configure_matplotlib_backend, get_all_visualizers

        logger.info("✅ Core modules imported successfully")
        return get_experiment_manager, ExperimentRunner, settings, get_all_visualizers
    except ImportError as e:
        logger.error(f"❌ Failed to import core modules: {e}")
        sys.exit(1)

def run_interactive_mode():
    """Run the framework in interactive CLI mode."""
    try:
        from src.cli.interactive import InteractiveCLI
        from src.cli.display import DisplayManager

        logger.info("🎮 Starting interactive CLI mode")

        # Initialize CLI components
        cli = InteractiveCLI()

        # Run interactive session
        cli.run_interactive_session()

    except Exception as e:
        logger.error(f"❌ Error in interactive mode: {e}")
        sys.exit(1)

def run_experiment_by_name(exp_name: str):
    """Run a specific experiment by name."""
    try:
        get_experiment_manager, ExperimentRunner, settings, get_all_visualizers = import_core_modules()

        # Get experiment manager
        em = get_experiment_manager()

        # Get experiment configuration
        experiment_config = em.get_experiment(exp_name)
        if not experiment_config:
            logger.error(f"❌ Experiment '{exp_name}' not found")
            sys.exit(1)

        logger.info(f"🧪 Running experiment: {exp_name}")

                # Run experiment using experiment manager
        experiment_result = em.run_experiment(exp_name)

        if experiment_result is None:
            logger.error(f"❌ Experiment '{exp_name}' failed to run")
            sys.exit(1)

        # Extract results from tuple (circuit, result)
        if isinstance(experiment_result, tuple) and len(experiment_result) == 2:
            circuit, results = experiment_result
        else:
            results = experiment_result

        # Convert results to the format expected by visualizers
        if hasattr(results, 'get_counts'):  # Qiskit Counts object
            results = results.get_counts()
        elif isinstance(results, dict) and 'counts' in results:
            results = results['counts']

                # For now, just log success without visualization
        logger.info(f"✅ Experiment '{exp_name}' completed successfully")
        logger.info(f"📊 Results: {type(results)}")
        if isinstance(results, dict):
            logger.info(f"📊 Result keys: {list(results.keys())}")
        elif hasattr(results, 'get_counts'):
            logger.info(f"📊 Counts: {results.get_counts()}")

    except Exception as e:
        logger.error(f"❌ Error running experiment '{exp_name}': {e}")
        sys.exit(1)

def list_experiments():
    """List all available experiments."""
    try:
        get_experiment_manager, _, _, _ = import_core_modules()

        # Get experiment manager
        em = get_experiment_manager()

        # Get experiments by category
        categories = em.get_categories()

        print("\n📋 Available Experiments by Category:")
        print("=" * 50)

        for category in categories:
            print(f"\n🎯 {category.upper()}:")
            # Get experiments by category using list_experiments
            experiments = em.list_experiments(category=category)
            for exp_config in experiments:
                exp_name = exp_config.get('id', 'Unknown')
                difficulty = exp_config.get('metadata', {}).get('difficulty', 'Unknown')
                description = exp_config.get('metadata', {}).get('description', 'No description')
                print(f"  • {exp_name} ({difficulty}) - {description}")

        print(f"\n📊 Total experiments: {len(em.list_experiments())}")

    except Exception as e:
        logger.error(f"❌ Error listing experiments: {e}")
        sys.exit(1)

def show_help():
    """Show help information."""
    print("""
🚀 Quantum Experiment Framework - New Modular Entry Point

Usage:
    python3 main_new.py                    # Interactive CLI mode
    python3 main_new.py --list            # List available experiments
    python3 main_new.py --run <exp_name>  # Run specific experiment
    QUANTUM_INTERACTIVE=false python3 main_new.py  # Non-interactive mode

Environment Variables:
    QUANTUM_INTERACTIVE=true/false        # Control interactive mode
    QUANTUM_LOG_LEVEL=INFO/DEBUG          # Set logging level

Examples:
    python3 main_new.py --list
    python3 main_new.py --run ghz_basic
    QUANTUM_INTERACTIVE=false python3 main_new.py --run w_phase_flip
    """)

def main():
    """Main entry point."""
    # Set up environment
    setup_environment()

    # Parse command line arguments
    args = sys.argv[1:]

    if not args:
        # No arguments - run interactive mode
        run_interactive_mode()
    elif args[0] == '--help' or args[0] == '-h':
        show_help()
    elif args[0] == '--list':
        list_experiments()
    elif args[0] == '--run' and len(args) > 1:
        run_experiment_by_name(args[1])
    else:
        print("❌ Invalid arguments. Use --help for usage information.")
        sys.exit(1)

if __name__ == "__main__":
    main()
