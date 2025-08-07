"""
Click-based CLI commands for the Quantum Experiment Framework.

This module provides command-line interface commands using Click for
non-interactive experiment execution.
"""

import click
from typing import Optional, Dict, Any
from rich.console import Console

from src.config.constants import VALID_STATE_TYPES, VALID_NOISE_TYPES
from src.config.params import apply_defaults, validate_parameters
from src.cli.display import DisplayManager


@click.command()
@click.option("--num-qubits", type=int, help="Number of qubits for the experiment")
@click.option(
    "--state-type",
    type=click.Choice(VALID_STATE_TYPES, case_sensitive=False),
    help="Type of quantum state",
)
@click.option(
    "--noise-type",
    type=click.Choice(VALID_NOISE_TYPES, case_sensitive=False),
    help="Type of noise model",
)
@click.option(
    "--noise-enabled/--no-noise", default=True, help="Enable or disable noise"
)
@click.option("--shots", type=int, help="Number of shots for qasm simulation")
@click.option(
    "--sim-mode",
    type=click.Choice(["qasm", "density"], case_sensitive=False),
    help="Simulation mode",
)
@click.option("--error-rate", type=float, help="Custom error rate for noise models")
@click.option("--z-prob", type=float, help="Z probability for PHASE_FLIP noise")
@click.option("--i-prob", type=float, help="I probability for PHASE_FLIP noise")
@click.option(
    "--t1", type=float, help="T1 relaxation time (µs) for THERMAL_RELAXATION noise"
)
@click.option(
    "--t2", type=float, help="T2 dephasing time (µs) for THERMAL_RELAXATION noise"
)
@click.option(
    "--interactive/--no-interactive", default=True, help="Run in interactive mode"
)
def run_experiment_command(
    num_qubits: Optional[int],
    state_type: Optional[str],
    noise_type: Optional[str],
    noise_enabled: bool,
    shots: Optional[int],
    sim_mode: Optional[str],
    error_rate: Optional[float],
    z_prob: Optional[float],
    i_prob: Optional[float],
    t1: Optional[float],
    t2: Optional[float],
    interactive: bool,
) -> None:
    """
    Quantum Experiment CLI Command

    A CLI tool to run quantum experiments with configurable parameters,
    supporting interactive and non-interactive modes.
    """
    if interactive:
        from src.cli.interactive import run_interactive

        run_interactive()
    else:
        # Non-interactive mode
        args = {
            "num_qubits": num_qubits,
            "state_type": state_type,
            "noise_type": noise_type,
            "noise_enabled": noise_enabled,
            "shots": shots,
            "sim_mode": sim_mode,
            "visualization_type": "none",
            "save_plot": None,
            "min_occurrences": 0,
            "show_real": False,
            "show_imag": False,
            "error_rate": error_rate,
            "z_prob": z_prob,
            "i_prob": i_prob,
            "t1": t1,
            "t2": t2,
            "custom_params": None,
        }
        args = apply_defaults(args)

        # TODO: Run experiment with non-interactive args
        # This will be implemented when we extract the experiment running logic
        console = Console()
        display_manager = DisplayManager(console)
        display_manager.display_params_summary(args)
        display_manager.display_info_message("Non-interactive mode not yet implemented")


@click.command()
@click.option(
    "--list", "list_experiments", is_flag=True, help="List available experiments"
)
@click.option("--category", type=str, help="Filter experiments by category")
@click.option("--difficulty", type=str, help="Filter experiments by difficulty")
def list_experiments_command(
    list_experiments: bool,
    category: Optional[str],
    difficulty: Optional[str],
) -> None:
    """
    List available experiments.
    """
    from src.config.quick_experiments import QUICK_EXPERIMENTS

    console = Console()
    display_manager = DisplayManager(console)

    if list_experiments:
        # Display all experiments
        for key, experiment in QUICK_EXPERIMENTS.items():
            if category and experiment.get("category") != category:
                continue
            if difficulty and experiment.get("difficulty") != difficulty:
                continue

            display_manager.display_experiment_info({"key": key, **experiment})


@click.command()
@click.argument("experiment_key", type=str)
def run_preset_experiment_command(experiment_key: str) -> None:
    """
    Run a preset experiment by key.
    """
    from src.config.quick_experiments import QUICK_EXPERIMENTS, get_experiment_info

    if experiment_key not in QUICK_EXPERIMENTS:
        click.echo(f"❌ Experiment '{experiment_key}' not found.")
        return

    experiment_info = get_experiment_info(experiment_key)
    console = Console()
    display_manager = DisplayManager(console)

    display_manager.display_experiment_info(experiment_info)

    # TODO: Run the experiment
    # This will be implemented when we extract the experiment running logic
    display_manager.display_info_message(
        "Preset experiment execution not yet implemented"
    )
