"""
Main entry point for the Quantum Experiment Framework CLI.

This module provides the main entry point for running quantum experiments
through the command-line interface.
"""

import click
from src.cli.interactive import run_interactive
from src.cli.commands import (
    run_experiment_command,
    list_experiments_command,
    run_preset_experiment_command,
)


@click.group()
def cli():
    """
    Quantum Experiment Framework CLI

    A research-grade quantum experiment framework for conducting
    quantum computing experiments with configurable parameters,
    noise models, and visualization capabilities.
    """
    pass


# Add commands to the CLI group
cli.add_command(run_experiment_command, name="run")
cli.add_command(list_experiments_command, name="list")
cli.add_command(run_preset_experiment_command, name="preset")


@cli.command()
def interactive():
    """
    Run the quantum experiment framework in interactive mode.

    This launches the interactive CLI where you can select experiments,
    configure parameters, and run quantum simulations with rich output.
    """
    run_interactive()


if __name__ == "__main__":
    cli()
