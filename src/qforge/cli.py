"""Thin CLI wrapper for the quantum experiment framework.

This CLI follows the principle: parser + caller + printer.
All domain logic lives in the engine and experiments modules.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import typer
from rich.console import Console
from rich.table import Table

if TYPE_CHECKING:
    from qforge.engine.models import ExperimentResult

# Descriptions contain quantum notation (kets like |0⟩). On Windows, piped or
# legacy consoles default to a cp125x encoding that cannot represent them, so
# force UTF-8 on the output streams when possible.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure") and (_stream.encoding or "").lower() not in (
        "utf-8",
        "utf8",
    ):
        _stream.reconfigure(encoding="utf-8", errors="replace")

app = typer.Typer(
    name="qforge",
    help="QForge — quantum experiment engine",
    add_completion=False,
)

console = Console()

# Shared state populated by the callback, readable by subcommands.
app_state: dict = {}


@app.callback()
def main_callback(
    log_level: Annotated[
        str,
        typer.Option("--log-level", "-l", help="Log level: DEBUG, INFO, WARNING, ERROR"),
    ] = os.getenv("QEF_LOG_LEVEL", "WARNING"),
    quiet: Annotated[
        bool,
        typer.Option("--quiet", "-q", help="Suppress non-error log output"),
    ] = False,
    results_dir: Annotated[
        str | None,
        typer.Option("--results-dir", help="Override results directory"),
    ] = os.getenv("QEF_RESULTS_DIR"),
) -> None:
    """QForge."""
    from qforge.engine.infrastructure.logging import setup_logging

    effective_level = "ERROR" if quiet else log_level.upper()
    setup_logging(level=effective_level, mode="human")

    app_state["log_level"] = effective_level
    if results_dir:
        app_state["results_dir"] = results_dir


@app.command("list")
def list_experiments() -> None:
    """List all available experiment programs."""
    from qforge.experiments import list_experiments as get_experiments

    experiments = get_experiments()

    table = Table(title="Available Experiments")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Description", style="green")

    for name, description in experiments:
        table.add_row(name, description)

    console.print(table)


@app.command("run")
def run_experiment(
    name: Annotated[str, typer.Argument(help="Experiment name from registry")],
    override: Annotated[
        list[str] | None,
        typer.Option(
            "--set",
            "-s",
            help="Override config values as key=value pairs "
            "(e.g., -s num_qubits=3 -s error_rate=0.1)",
        ),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", "-j", help="Output result as JSON"),
    ] = False,
) -> None:
    """Run a registered experiment by name."""
    from qforge.experiments import get_experiment

    try:
        experiment = get_experiment(name)
    except KeyError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from None

    # Parse overrides
    overrides = _parse_overrides(override) if override else None

    console.print(f"[cyan]Running experiment:[/cyan] {name}")
    if overrides:
        console.print(f"[dim]Overrides: {overrides}[/dim]")

    try:
        result = experiment.run(overrides)
    except Exception as e:
        console.print(f"[red]Experiment failed:[/red] {e}")
        raise typer.Exit(code=1) from None

    _print_result(result, json_output)


@app.command("run-config")
def run_from_config(
    config_path: Annotated[
        Path,
        typer.Argument(
            help="Path to JSON config file",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ],
    json_output: Annotated[
        bool,
        typer.Option("--json", "-j", help="Output result as JSON"),
    ] = False,
) -> None:
    """Run experiment from a JSON configuration file."""
    from qforge.engine.api import run
    from qforge.engine.models import ExperimentConfig

    try:
        config_data = json.loads(config_path.read_text())
        config = ExperimentConfig(**config_data)
    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON:[/red] {e}")
        raise typer.Exit(code=1) from None
    except Exception as e:
        console.print(f"[red]Invalid config:[/red] {e}")
        raise typer.Exit(code=1) from None

    console.print(f"[cyan]Running from config:[/cyan] {config_path}")

    try:
        result = run(config)
    except Exception as e:
        console.print(f"[red]Experiment failed:[/red] {e}")
        raise typer.Exit(code=1) from None

    _print_result(result, json_output)


def _parse_overrides(overrides: list[str]) -> dict:
    """Parse key=value override strings into a dictionary."""
    result = {}
    for item in overrides:
        if "=" not in item:
            console.print(f"[yellow]Warning:[/yellow] Ignoring invalid override: {item}")
            continue

        key, value = item.split("=", 1)
        key = key.strip()

        # Try to parse as JSON for complex types, fall back to string
        try:
            result[key] = json.loads(value)
        except json.JSONDecodeError:
            # Try common type conversions
            if value.lower() == "true":
                result[key] = True
            elif value.lower() == "false":
                result[key] = False
            else:
                try:
                    result[key] = int(value)
                except ValueError:
                    try:
                        result[key] = float(value)
                    except ValueError:
                        result[key] = value

    return result


def _print_result(result: ExperimentResult, json_output: bool) -> None:
    """Print experiment result in the requested format."""
    if json_output:
        console.print(result.model_dump_json(indent=2))
        return

    # Pretty print summary
    console.print()
    console.print(f"[green]Status:[/green] {result.status}")
    console.print(f"[green]Timestamp:[/green] {result.timestamp}")

    # Show metrics bundle if available
    if result.metrics_bundle:
        bundle = result.metrics_bundle
        console.print()
        label = f"Metrics ({bundle.profile})" if bundle.profile else "Metrics"
        console.print(f"[bold]{label}:[/bold]")

        metrics_table = Table(show_header=True, header_style="bold")
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Value", justify="right")
        metrics_table.add_column("Status", style="dim")

        for name, entry in sorted(bundle.metrics.items()):
            metrics_table.add_row(name, f"{entry.value:.4f}", entry.status)

        console.print(metrics_table)

    # Show measurement results summary if available
    if result.analysis and result.analysis.measurement_results:
        meas = result.analysis.measurement_results
        console.print()
        console.print(f"[bold]Measurements:[/bold] {meas.total_shots} shots")
        top_outcomes = sorted(meas.raw_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        if top_outcomes:
            console.print("[dim]Top outcomes:[/dim]")
            for outcome, count in top_outcomes:
                pct = 100 * count / meas.total_shots
                console.print(f"  {outcome}: {count} ({pct:.1f}%)")


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
