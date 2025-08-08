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
from src.cli.interactive_app import InteractiveCLI
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

        # Feature-flagged engine path
        use_engine = os.environ.get("QEXP_USE_ENGINE_API", "0").lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        if use_engine:
            try:
                em = get_experiment_manager()
                exp = em.get_experiment(exp_name)
                if not exp:
                    logger.error(f"❌ Experiment '{exp_name}' not found")
                    sys.exit(1)

                cfg = dict(exp.get("config", {}))
                # Normalize config for engine model (extra=forbid)
                allowed = {
                    "num_qubits",
                    "state_type",
                    "noise_type",
                    "noise_enabled",
                    "shots",
                    "sim_mode",
                    "error_rate",
                    "rng_seed",
                    "custom_params",
                }
                cfg = {k: v for k, v in cfg.items() if k in allowed}
                # Normalize values
                if isinstance(cfg.get("noise_type"), str):
                    cfg["noise_type"] = cfg["noise_type"].lower()
                if isinstance(cfg.get("sim_mode"), str):
                    cfg["sim_mode"] = cfg["sim_mode"].lower()
                if isinstance(cfg.get("state_type"), str):
                    cfg["state_type"] = cfg["state_type"].upper()

                from src.engine.api import run as engine_run
                from src.engine.context import AppContext

                ctx = AppContext(
                    base_results_dir=getattr(settings, "DEFAULT_RESULTS_DIR", "results")
                )
                res = engine_run(cfg, ctx)
                # Log saved artifact path
                if res.artifacts:
                    logger.info(
                        f"✅ Engine run completed. Saved analysis: {res.artifacts[0].path}"
                    )
                else:
                    logger.info("✅ Engine run completed (no artifacts recorded)")
                return
            except Exception as e:
                logger.warning(f"Engine path failed, falling back to legacy: {e}")

        # Legacy path
        em = get_experiment_manager()
        experiment_config = em.get_experiment(exp_name)
        if not experiment_config:
            logger.error(f"❌ Experiment '{exp_name}' not found")
            sys.exit(1)

        logger.info(f"🧪 Running experiment: {exp_name}")

        experiment_result = em.run_experiment(exp_name)
        if experiment_result is None:
            logger.error(f"❌ Experiment '{exp_name}' failed to run")
            sys.exit(1)

        logger.info(f"✅ Experiment '{exp_name}' completed successfully")
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


def run_from_config(config_path: str) -> None:
    """Run an experiment from a JSON/YAML config file."""
    import json as _json

    try:
        if config_path.endswith((".yaml", ".yml")):
            import yaml  # type: ignore

            with open(config_path, "r") as f:
                data = yaml.safe_load(f)
        else:
            with open(config_path, "r") as f:
                data = _json.load(f)
    except Exception as e:
        logger.error(f"❌ Failed to load config: {e}")
        sys.exit(1)

    try:
        get_experiment_manager, _, _, _ = import_core_modules()
        em = get_experiment_manager()

        preset = data.get("preset")
        params_override = {k: v for k, v in data.items() if k != "preset"}
        if preset:
            result = em.run_experiment(preset, custom_params=params_override)
        else:
            result = em.run_experiment("ghz_basic", custom_params=data)

        if result is None:
            logger.error("❌ Experiment failed to run from config")
            sys.exit(1)
        logger.info("✅ Experiment from config completed")
    except Exception as e:
        logger.error(f"❌ Error running from config: {e}")
        sys.exit(1)


def run_sweep_from_manifest(manifest_path: str) -> None:
    """Run a parameter sweep described by a JSON/YAML manifest."""
    import json as _json

    try:
        if manifest_path.endswith((".yaml", ".yml")):
            import yaml  # type: ignore

            with open(manifest_path, "r") as f:
                data = yaml.safe_load(f)
        else:
            with open(manifest_path, "r") as f:
                data = _json.load(f)
    except Exception as e:
        logger.error(f"❌ Failed to load manifest: {e}")
        sys.exit(1)

    # Validate manifest
    try:
        from src.utils.schema import validate_manifest_schema

        validate_manifest_schema(data)
    except Exception as e:
        logger.error(f"❌ Invalid manifest: {e}")
        sys.exit(2)

    base_preset = data["base_preset"]
    parameter_ranges = dict(data["parameter_ranges"])  # shallow copy
    runs_per_config = int(data.get("runs_per_config", 1))
    rng_seed = data.get("rng_seed")

    # Feature-flagged engine path
    use_engine = os.environ.get("QEXP_USE_ENGINE_API", "0").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    if use_engine:
        try:
            from src.experiments import get_experiment_manager
            from src.engine.api import sweep as engine_sweep, run as engine_run
            from src.engine.context import AppContext

            em = get_experiment_manager()
            exp = em.get_experiment(base_preset)
            if not exp:
                logger.error(f"❌ Base preset '{base_preset}' not found")
                sys.exit(1)
            base_cfg = dict(exp.get("config", {}))
            # Sanitize/normalize for engine
            allowed = {
                "num_qubits",
                "state_type",
                "noise_type",
                "noise_enabled",
                "shots",
                "sim_mode",
                "error_rate",
                "rng_seed",
                "custom_params",
            }
            base_cfg = {k: v for k, v in base_cfg.items() if k in allowed}
            if isinstance(base_cfg.get("noise_type"), str):
                base_cfg["noise_type"] = base_cfg["noise_type"].lower()
            if isinstance(base_cfg.get("sim_mode"), str):
                base_cfg["sim_mode"] = base_cfg["sim_mode"].lower()
            if isinstance(base_cfg.get("state_type"), str):
                base_cfg["state_type"] = base_cfg["state_type"].upper()
            if rng_seed is not None:
                base_cfg["rng_seed"] = int(rng_seed)

            # Normalize parameter_ranges values
            norm_ranges = {}
            for k, vals in parameter_ranges.items():
                if k == "noise_type":
                    norm_ranges[k] = [str(v).lower() for v in vals]
                elif k == "state_type":
                    norm_ranges[k] = [str(v).upper() for v in vals]
                elif k == "sim_mode":
                    norm_ranges[k] = [str(v).lower() for v in vals]
                else:
                    norm_ranges[k] = vals

            ctx = AppContext(
                base_results_dir=getattr(settings, "DEFAULT_RESULTS_DIR", "results")
            )

            # Honor runs_per_config by repeating sweeps with optional rng offset
            total_results = []
            for i in range(max(1, runs_per_config)):
                cfg_for_iter = dict(base_cfg)
                if cfg_for_iter.get("rng_seed") is not None:
                    cfg_for_iter["rng_seed"] = int(cfg_for_iter["rng_seed"]) + i
                manifest_payload = {
                    "base_config": cfg_for_iter,
                    "parameter_ranges": norm_ranges,
                    "runs_per_config": 1,
                }
                iter_results = engine_sweep(manifest_payload, ctx)
                total_results.extend(iter_results)

            logger.info(f"✅ Engine sweep completed: {len(total_results)} runs")
            return
        except Exception as e:
            logger.warning(f"Engine sweep path failed, falling back to legacy: {e}")

    # Legacy path
    try:
        from src.core.parameter_sweep import ParameterSweepEngine

        engine = ParameterSweepEngine()
        engine.run_parameter_sweep(
            base_experiment_id=base_preset,
            parameter_ranges=parameter_ranges,
            runs_per_config=runs_per_config,
            sweep_name=f"{base_preset}_manifest",
        )
        logger.info("✅ Sweep from manifest completed")
    except Exception as e:
        logger.error(f"❌ Sweep failed: {e}")
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


def visualize_from_json(
    json_path: str,
    viz_type: str = "histogram",
    *,
    backend: str | None = None,
    outdir: str | None = None,
) -> None:
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

    # Engine-first path for visualization when enabled
    try:
        use_engine = os.environ.get("QEXP_USE_ENGINE_API", "0").lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        if use_engine and viz_type in {"histogram", "density_matrix", "hypergraph"}:
            from src.engine.viz_service import (
                VisualizationService,
                VisualizationRequest,
            )

            svc = VisualizationService(default_backend=(backend or "matplotlib"))
            req = VisualizationRequest(
                viz_type=viz_type,
                backend=(backend or "matplotlib"),
                output_base_dir=outdir,
            )
            artifact = svc.render_from_json(json_path, req)
            logger.info(f"🖼️  Saved {viz_type} visualization to: {artifact.path}")
            return
    except Exception as e:
        logger.warning(f"Engine visualization path failed, falling back to legacy: {e}")

    params = analysis.get("experiment_parameters", {})
    counts = analysis.get("measurement_results", {}).get("raw_counts", {})

    # Prepare visualization (legacy)
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


def apply_profile_from_args(args: list) -> list:
    """Apply `--profile <name>` if present and return args with it removed."""
    if "--profile" in args:
        try:
            idx = args.index("--profile")
            name = args[idx + 1]
        except Exception:
            logger.error("❌ --profile flag requires a name")
            sys.exit(2)
        try:
            from src.config import profiles as _profiles

            prof = _profiles.load_profile(name)
            _profiles.apply_profile(prof)
            logger.info(f"👤 Applied profile: {name}")
        except Exception as e:
            logger.error(f"❌ Failed to apply profile '{name}': {e}")
            sys.exit(2)
        # remove flag and name from args
        args = args[:idx] + args[idx + 2 :]
    return args


def main():
    """Main entry point."""
    # Set up environment
    setup_environment()

    # Parse command line arguments
    args = sys.argv[1:]

    # Optional: apply profile early if provided
    args = apply_profile_from_args(args)

    # Streaming structured logs for headless/server mode and quiet/JSON/verbose flags
    console_json = "-J" in args or "--json-only" in args
    if "--stream-logs" in args or "-q" in args or "--quiet" in args or console_json:
        try:
            from src.utils import logger as logger_utils

            logger_utils.setup_logger(
                log_level=os.environ.get("QUANTUM_LOG_LEVEL", "INFO"),
                log_to_file=False,
                log_to_console=True,
                structured_log_file=(
                    "logs/structured_logs.json" if "--stream-logs" in args else None
                ),
                console_json_mode=console_json,
            )
            logger.info(
                "📡 Headless logging configured (stream=%s, json_console=%s)",
                "on" if "--stream-logs" in args else "off",
                str(console_json),
            )
        except Exception as _e:
            logger.warning(f"Failed to configure headless logging: {_e}")
        # Remove flags from args for further parsing
        for flag in [
            "-q",
            "--quiet",
            "-J",
            "--json-only",
            "-v",
            "--verbose",
            "--stream-logs",
        ]:
            try:
                while flag in args:
                    args.remove(flag)
            except ValueError:
                pass

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
    elif args[0] == "run" and len(args) > 2 and args[1] == "--config":
        run_from_config(args[2])
    elif args[0] == "--sweep" and len(args) > 1:
        run_parameter_sweep(args[1])
    elif args[0] == "sweep" and len(args) > 2 and args[1] == "--manifest":
        run_sweep_from_manifest(args[2])
    elif args[0] == "--viz" and len(args) > 1:
        viz_type = "histogram"
        if "--type" in args:
            try:
                viz_type = args[args.index("--type") + 1]
            except Exception:
                pass
        # Optional backend and outdir flags
        backend = None
        outdir = None
        if "--backend" in args:
            try:
                backend = args[args.index("--backend") + 1]
            except Exception:
                pass
        if "--outdir" in args:
            try:
                outdir = args[args.index("--outdir") + 1]
            except Exception:
                pass
        visualize_from_json(args[1], viz_type, backend=backend, outdir=outdir)
    elif args[0] == "viz" and len(args) > 2 and args[1] == "--from":
        # New subcommand: viz --from <file> [--type ...]
        viz_type = "histogram"
        if "--type" in args:
            try:
                viz_type = args[args.index("--type") + 1]
            except Exception:
                pass
        backend = None
        outdir = None
        if "--backend" in args:
            try:
                backend = args[args.index("--backend") + 1]
            except Exception:
                pass
        if "--outdir" in args:
            try:
                outdir = args[args.index("--outdir") + 1]
            except Exception:
                pass
        visualize_from_json(args[2], viz_type, backend=backend, outdir=outdir)
    elif args[0] == "report" and len(args) > 2 and args[1] == "--from":
        # New subcommand: report --from <results.json> [--format md]
        fmt = "md"
        if "--format" in args:
            try:
                fmt = args[args.index("--format") + 1]
            except Exception:
                pass
        try:
            from src.visualization.report import save_report_from_json

            out = save_report_from_json(args[2], fmt=fmt)
            logger.info(f"📝 Report saved to: {out}")
        except Exception as e:
            logger.error(f"❌ Report generation failed: {e}")
            sys.exit(2)
    else:
        print("❌ Invalid arguments. Use --help for usage information.")
        sys.exit(1)


if __name__ == "__main__":
    main()
