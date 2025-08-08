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
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def setup_environment() -> None:
    """Set up environment for quantum experiments."""
    # Set interactive mode for CLI
    if not os.environ.get("QUANTUM_INTERACTIVE"):
        os.environ["QUANTUM_INTERACTIVE"] = "true"

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
        get_experiment_manager, ExperimentRunner, settings, get_all_visualizers = (
            import_core_modules()
        )

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
        if hasattr(results, "get_counts"):  # Qiskit Counts object
            results = results.get_counts()
        elif isinstance(results, dict) and "counts" in results:
            results = results["counts"]

            # For now, just log success without visualization
        logger.info(f"✅ Experiment '{exp_name}' completed successfully")
        logger.info(f"📊 Results: {type(results)}")
        if isinstance(results, dict):
            logger.info(f"📊 Result keys: {list(results.keys())}")
        elif hasattr(results, "get_counts"):
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
                exp_name = exp_config.get("id", "Unknown")
                difficulty = exp_config.get("metadata", {}).get("difficulty", "Unknown")
                description = exp_config.get("metadata", {}).get(
                    "description", "No description"
                )
                print(f"  • {exp_name} ({difficulty}) - {description}")

        print(f"\n📊 Total experiments: {len(em.list_experiments())}")

    except Exception as e:
        logger.error(f"❌ Error listing experiments: {e}")
        sys.exit(1)


def run_parameter_sweep(experiment_name: str):
    """Run a parameter sweep on the specified experiment."""
    try:
        logger.info(f"🔄 Starting parameter sweep for experiment: {experiment_name}")

        # Import core modules
        get_experiment_manager, ExperimentRunner, settings, get_all_visualizers = (
            import_core_modules()
        )

        # Import parameter sweep engine
        from src.core.parameter_sweep import ParameterSweepEngine

        # Initialize sweep engine
        sweep_engine = ParameterSweepEngine()

        # For structured decoherence experiments, run noise level sweep
        if (
            "ghz_structured_decoherence" in experiment_name
            or "structured_decoherence" in experiment_name
        ):
            logger.info("🔬 Running structured decoherence noise level sweep")
            results = sweep_engine.run_noise_level_sweep(
                base_experiment_id=experiment_name,
                noise_levels=[0.01, 0.05, 0.10, 0.20],
                runs_per_level=3,
            )
        else:
            # Generic parameter sweep for other experiments
            logger.info("⚙️ Running generic parameter sweep")
            results = sweep_engine.run_parameter_sweep(
                base_experiment_id=experiment_name,
                parameter_ranges={
                    "error_rate": [0.01, 0.05, 0.10],
                    "shots": [1024, 4096],
                },
                runs_per_config=2,
            )

        logger.info("✅ Parameter sweep completed successfully!")
        logger.info(
            f"📊 Total experiments: {results['sweep_metadata']['total_experiments']}"
        )
        logger.info(
            f"📈 Success rate: {results['aggregated_analysis']['statistical_summary']['success_rate']:.2%}"
        )

        # Print key findings
        if results["aggregated_analysis"]["key_findings"]:
            logger.info("🎯 Key findings:")
            for finding in results["aggregated_analysis"]["key_findings"]:
                logger.info(f"   • {finding}")

    except Exception as e:
        logger.error(f"❌ Parameter sweep failed: {e}")
        sys.exit(1)


def show_help():
    """Show help information."""
    print(
        """
🚀 Quantum Experiment Framework - New Modular Entry Point

Usage:
    python3 main_new.py                    # Interactive CLI mode
    python3 main_new.py --list            # List available experiments
    python3 main_new.py --run <exp_name>  # Run specific experiment
    python3 main_new.py --sweep <exp_name>  # Run parameter sweep on experiment
    python3 main_new.py --viz <results.json> [--type histogram|density_matrix|hypergraph]
    QUANTUM_INTERACTIVE=false python3 main_new.py  # Non-interactive mode

Environment Variables:
    QUANTUM_INTERACTIVE=true/false        # Control interactive mode
    QUANTUM_LOG_LEVEL=INFO/DEBUG          # Set logging level

Examples:
    python3 main_new.py --list
    python3 main_new.py --run ghz_basic
    python3 main_new.py --sweep ghz_structured_decoherence_ref
    QUANTUM_INTERACTIVE=false python3 main_new.py --run w_phase_flip
    python3 main_new.py --viz results/.../structured_decoherence_xyz.json --type histogram
    """
    )


def visualize_from_json(json_path: str, viz_type: str = "histogram") -> None:
    """Visualize results from a saved JSON analysis file.

    Args:
        json_path: Path to results JSON saved by ResearchHandler
        viz_type: histogram | density_matrix | hypergraph
    """
    import json as _json

    try:
        with open(json_path, "r") as f:
            analysis = _json.load(f)
    except Exception as e:
        logger.error(f"❌ Failed to load JSON: {e}")
        sys.exit(1)

    params = analysis.get("experiment_parameters", {})
    counts = analysis.get("measurement_results", {}).get("raw_counts", {})

    # Prepare visualization
    try:
        if viz_type == "histogram":
            from src.visualization import get_histogram_visualizer

            plot_fn = get_histogram_visualizer()
            plot_fn(
                counts=counts,
                state_type=params.get("state_type", "GHZ"),
                noise_type=params.get("noise_type", "DEPOLARIZING"),
                noise_enabled=params.get("noise_enabled", True),
                num_qubits=int(params.get("num_qubits", 3)),
                research_metrics=analysis.get("research_metrics"),
                save_path=None,
            )
        elif viz_type == "hypergraph":
            from src.visualization import get_hypergraph_visualizer

            plot_fn = get_hypergraph_visualizer()
            plot_fn(
                correlation_data=counts,
                state_type=params.get("state_type", "GHZ"),
                noise_type=params.get("noise_type", "DEPOLARIZING"),
                config={},
            )
        elif viz_type == "density_matrix":
            logger.error(
                "❌ Cannot reconstruct density matrix from saved counts; use during density runs."
            )
            sys.exit(2)
        else:
            logger.error(f"❌ Unsupported visualization type: {viz_type}")
            sys.exit(2)
    except Exception as e:
        logger.error(f"❌ Visualization failed: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    # Set up environment
    setup_environment()

    # Parse command line arguments
    args = sys.argv[1:]

    if not args:
        # No arguments - run interactive mode
        run_interactive_mode()
    elif args[0] == "--help" or args[0] == "-h":
        show_help()
    elif args[0] == "--list":
        list_experiments()
    elif args[0] == "--run" and len(args) > 1:
        # Support `--run <exp_name>` as preset name
        run_experiment_by_name(args[1])
    elif args[0] == "run" and len(args) > 2 and args[1] == "--preset":
        # New subcommand style: run --preset <id>
        run_experiment_by_name(args[2])
    elif args[0] == "--sweep" and len(args) > 1:
        run_parameter_sweep(args[1])
    elif args[0] == "--viz" and len(args) > 1:
        viz_type = "histogram"
        if "--type" in args:
            try:
                viz_type = args[args.index("--type") + 1]
            except Exception:
                pass
        visualize_from_json(args[1], viz_type)
    elif args[0] == "viz" and len(args) > 2 and args[1] == "--from":
        # New subcommand: viz --from <file> [--type ...]
        viz_type = "histogram"
        if "--type" in args:
            try:
                viz_type = args[args.index("--type") + 1]
            except Exception:
                pass
        visualize_from_json(args[2], viz_type)
    else:
        print("❌ Invalid arguments. Use --help for usage information.")
        sys.exit(1)


if __name__ == "__main__":
    main()
