"""Thin CLI wrapper for the quantum experiment framework.

Parser + caller + printer. Domain logic stays in the engine and experiments.
"""

from __future__ import annotations

import json
import os
import sys
from difflib import get_close_matches
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any

import typer
from rich.console import Console
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

if TYPE_CHECKING:
    from qforge.engine.execution.context import AppContext
    from qforge.engine.models import ExperimentConfig, ExperimentResult

# Descriptions contain quantum notation (kets like |0⟩). On Windows, piped or
# legacy consoles default to a cp125x encoding that cannot represent them, so
# force UTF-8 on the output streams when possible.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure") and (_stream.encoding or "").lower() not in (
        "utf-8",
        "utf8",
    ):
        _stream.reconfigure(encoding="utf-8", errors="replace")

_EXAMPLES = (
    "  qforge list\n"
    "  qforge run 01_superposition\n"
    "  qforge run 05_bell_states\n"
    "  qforge sweep 06_ghz_states -p num_qubits=2,3,4"
)

app = typer.Typer(
    name="qforge",
    help=(
        "Quantum experiment engine. "
        "Start with [bold]qforge list[/bold], then "
        "[bold]qforge run 01_superposition[/bold]."
    ),
    epilog=f"Examples:\n{_EXAMPLES}",
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]},
)

console = Console()

# Shared state populated by the callback, readable by subcommands.
app_state: dict[str, Any] = {}

ResultsDirOpt = Annotated[
    str | None,
    typer.Option("--results-dir", help="Directory for histograms and analysis JSON"),
]


def _version_callback(value: bool) -> None:
    if value:
        import qforge

        console.print(qforge.__version__)
        raise typer.Exit()


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
    results_dir: ResultsDirOpt = os.getenv("QEF_RESULTS_DIR"),
    version: Annotated[
        bool,
        typer.Option("--version", callback=_version_callback, is_eager=True, help="Print version"),
    ] = False,
) -> None:
    """QForge."""
    from qforge.engine.infrastructure.logging import setup_logging

    effective_level = "ERROR" if quiet else log_level.upper()
    setup_logging(level=effective_level, mode="human")

    app_state["log_level"] = effective_level
    app_state["results_dir"] = results_dir


def _section_for(name: str) -> str:
    """Presentation grouping for `qforge list` — not experiment semantics."""
    if len(name) >= 3 and name[0].isdigit() and name[1].isdigit() and name[2] == "_":
        return "Basics — start here"
    if name.startswith("adv_"):
        return "Advanced"
    if name.startswith("dec_"):
        return "Decoherence"
    if name.startswith("hw_"):
        return "Hardware"
    return "Deep dives"


@app.command("list")
def list_experiments() -> None:
    """Show experiments, grouped by learning track."""
    from qforge.experiments import list_experiments as get_experiments

    grouped: dict[str, list[tuple[str, str]]] = {}
    for name, description in get_experiments():
        grouped.setdefault(_section_for(name), []).append((name, description))

    order = (
        "Basics — start here",
        "Advanced",
        "Decoherence",
        "Hardware",
        "Deep dives",
    )
    for section in order:
        rows = grouped.get(section)
        if not rows:
            continue
        console.print()
        console.print(Rule(section, style="cyan"))
        table = Table(show_header=False, box=None, pad_edge=False, padding=(0, 2, 0, 0))
        table.add_column("name", style="bold cyan", no_wrap=True)
        table.add_column("description", style="dim")
        for name, description in rows:
            table.add_row(name, description)
        console.print(table)

    console.print()
    console.print("[dim]Try[/dim]  [bold]qforge run 01_superposition[/bold]")
    console.print("[dim]     [/dim]  [bold]qforge sweep 06_ghz_states -p num_qubits=2,3,4[/bold]")


@app.command("run")
def run_experiment(
    name: Annotated[str, typer.Argument(help="Name from [bold]qforge list[/bold]")],
    override: Annotated[
        list[str] | None,
        typer.Option(
            "--set",
            "-s",
            help="Override one config field, e.g. [bold]-s shots=1024[/bold]",
        ),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", "-j", help="Print the full result as JSON"),
    ] = False,
    results_dir: ResultsDirOpt = None,
) -> None:
    """Run one experiment (its default setup, unless you pass -s)."""
    _maybe_results_dir(results_dir)
    overrides = _parse_overrides(override) if override else None
    experiment = _experiment_or_exit(name)

    if not json_output:
        console.print(f"[bold]{name}[/bold]")
        if overrides:
            console.print(f"[dim]{_format_pairs(overrides)}[/dim]")

    try:
        result = experiment.run(overrides, ctx=_app_context())
    except Exception as e:
        console.print(f"[red]Failed:[/red] {e}")
        raise typer.Exit(code=1) from None

    hint = getattr(experiment, "metrics_hint", None)
    _print_result(result, json_output, title=name, metrics_hint=hint)


@app.command("sweep")
def sweep_experiment(
    name: Annotated[str, typer.Argument(help="Name from [bold]qforge list[/bold]")],
    param: Annotated[
        list[str] | None,
        typer.Option(
            "--param",
            "-p",
            help="Values to sweep, e.g. [bold]-p num_qubits=2,3,4[/bold] (repeatable)",
        ),
    ] = None,
    override: Annotated[
        list[str] | None,
        typer.Option(
            "--set",
            "-s",
            help="Applied to every point, e.g. [bold]-s metrics=quick[/bold]",
        ),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", "-j", help="Print the full results as JSON"),
    ] = False,
    results_dir: ResultsDirOpt = None,
) -> None:
    """Run one experiment across a range of values."""
    from qforge.engine.api import sweep
    from qforge.engine.models import SweepManifest

    if not param:
        console.print("[red]Sweep needs a range.[/red]")
        console.print()
        console.print("  qforge sweep 06_ghz_states -p num_qubits=2,3,4")
        console.print(
            "  qforge sweep 06_ghz_states -p error_rate=0.01,0.05,0.1 "
            "-s noise_enabled=true -s noise_type=depolarizing"
        )
        raise typer.Exit(code=1)

    _maybe_results_dir(results_dir)
    ranges = _parse_ranges(param)
    overrides = _parse_overrides(override) if override else None
    base_config = _config_from_experiment(name, overrides)

    if not json_output:
        console.print(f"[bold]Sweep[/bold]  {name}")
        console.print(f"[dim]{_format_pairs(ranges)}[/dim]")
        if overrides:
            console.print(f"[dim]{_format_pairs(overrides)}[/dim]")

    try:
        results = sweep(
            SweepManifest(base_config=base_config, parameter_ranges=ranges),
            _app_context(),
        )
    except Exception as e:
        console.print(f"[red]Failed:[/red] {e}")
        raise typer.Exit(code=1) from None

    _print_sweep(results, list(ranges), json_output)


@app.command("run-config")
def run_from_config(
    config_path: Annotated[
        Path,
        typer.Argument(help="JSON ExperimentConfig file", exists=True, readable=True),
    ],
    json_output: Annotated[
        bool,
        typer.Option("--json", "-j", help="Print the full result as JSON"),
    ] = False,
    results_dir: ResultsDirOpt = None,
) -> None:
    """Run from a JSON config file (same fields as -s)."""
    from qforge.engine.api import run
    from qforge.engine.models import ExperimentConfig

    _maybe_results_dir(results_dir)
    try:
        config = ExperimentConfig(**json.loads(config_path.read_text()))
    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON:[/red] {e}")
        raise typer.Exit(code=1) from None
    except Exception as e:
        console.print(f"[red]Invalid config:[/red] {e}")
        raise typer.Exit(code=1) from None

    if not json_output:
        console.print(f"[bold]{config_path}[/bold]")

    try:
        result = run(config, _app_context())
    except Exception as e:
        console.print(f"[red]Failed:[/red] {e}")
        raise typer.Exit(code=1) from None

    _print_result(result, json_output)


@app.command("sweep-config")
def sweep_from_config(
    config_path: Annotated[
        Path,
        typer.Argument(help="JSON SweepManifest file", exists=True, readable=True),
    ],
    json_output: Annotated[
        bool,
        typer.Option("--json", "-j", help="Print the full results as JSON"),
    ] = False,
    results_dir: ResultsDirOpt = None,
) -> None:
    """Sweep from a JSON file (base_config + parameter_ranges)."""
    from qforge.engine.api import sweep
    from qforge.engine.models import SweepManifest

    _maybe_results_dir(results_dir)
    try:
        manifest = SweepManifest(**json.loads(config_path.read_text()))
    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON:[/red] {e}")
        raise typer.Exit(code=1) from None
    except Exception as e:
        console.print(f"[red]Invalid sweep manifest:[/red] {e}")
        raise typer.Exit(code=1) from None

    if not json_output:
        console.print(f"[bold]Sweep[/bold]  {config_path}")
        console.print(f"[dim]{_format_pairs(manifest.parameter_ranges)}[/dim]")

    try:
        results = sweep(manifest, _app_context())
    except Exception as e:
        console.print(f"[red]Failed:[/red] {e}")
        raise typer.Exit(code=1) from None

    _print_sweep(results, list(manifest.parameter_ranges), json_output)


def _maybe_results_dir(results_dir: str | None) -> None:
    if results_dir:
        app_state["results_dir"] = results_dir


def _app_context() -> AppContext | None:
    """Build an AppContext when --results-dir / QEF_RESULTS_DIR is set."""
    results_dir = app_state.get("results_dir")
    if not results_dir:
        return None
    from qforge.engine.execution.context import AppContext

    return AppContext(base_results_dir=str(results_dir))


def _experiment_or_exit(name: str) -> Any:
    """Load a registered experiment or print a hint and exit."""
    from qforge.experiments import get_experiment
    from qforge.experiments import list_experiments as registry_list

    try:
        return get_experiment(name)
    except KeyError:
        names = [item[0] for item in registry_list()]
        hint = get_close_matches(name, names, n=3, cutoff=0.5)
        console.print(f"[red]Unknown experiment:[/red] {name}")
        if hint:
            console.print("[dim]Did you mean[/dim] " + ", ".join(f"[bold]{h}[/bold]" for h in hint))
        console.print("[dim]See[/dim]  qforge list")
        raise typer.Exit(code=1) from None


def _config_from_experiment(
    name: str,
    overrides: dict[str, Any] | None,
) -> ExperimentConfig:
    """Load a registered experiment's default config and apply CLI overrides."""
    from qforge.engine.models import ExperimentConfig

    experiment = _experiment_or_exit(name)
    config = experiment.default_config()
    if not overrides:
        return config
    data = config.model_dump()
    data.update(overrides)
    return ExperimentConfig(**data)


def _coerce_scalar(value: str) -> Any:
    """Parse a single override/range token into a Python value."""
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        pass
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def _parse_overrides(overrides: list[str]) -> dict[str, Any]:
    """Parse key=value override strings into a dictionary."""
    result: dict[str, Any] = {}
    for item in overrides:
        if "=" not in item:
            console.print(f"[yellow]Ignoring[/yellow] {item}  (use key=value)")
            continue
        key, value = item.split("=", 1)
        result[key.strip()] = _coerce_scalar(value)
    return result


def _parse_ranges(items: list[str]) -> dict[str, list[Any]]:
    """Parse -p key=v1,v2,v3 (or JSON list) strings into parameter_ranges."""
    ranges: dict[str, list[Any]] = {}
    for item in items:
        if "=" not in item:
            console.print(f"[yellow]Ignoring[/yellow] {item}  (use key=v1,v2)")
            continue
        key, value = item.split("=", 1)
        key = key.strip()
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, list):
            ranges[key] = parsed
            continue
        if parsed is not None:
            ranges[key] = [parsed]
            continue
        values = [_coerce_scalar(part.strip()) for part in value.split(",") if part.strip()]
        if not values:
            console.print(f"[yellow]Empty range[/yellow] {key}")
            continue
        ranges[key] = values
    if not ranges:
        console.print("[red]No valid -p ranges.[/red]")
        raise typer.Exit(code=1)
    return ranges


def _format_pairs(data: dict[str, Any]) -> str:
    """Human summary of overrides or sweep ranges — not a Python repr."""
    parts: list[str] = []
    for key, value in data.items():
        if isinstance(value, list):
            parts.append(f"{key}={', '.join(str(v) for v in value)}")
        else:
            parts.append(f"{key}={value}")
    return "  ".join(parts)


def _display_path(path: str) -> str:
    """Prefer a cwd-relative path when the artifact lives in this tree."""
    raw = Path(path)
    try:
        return str(raw.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(raw)


def _print_path(label: str, path: str) -> None:
    line = Text.assemble((f"  {label:<11}", "dim"), (_display_path(path), "green"))
    line.no_wrap = True
    console.print(line, overflow="ignore", crop=False)


def _print_gate_explainers(result: ExperimentResult) -> None:
    """Print unique-gate explainers when circuit visualization ran."""
    rows: list[dict[str, str]] = []
    for artifact in result.artifacts:
        if artifact.kind != "circuit":
            continue
        extra = artifact.metadata.get("gate_explainers") if artifact.metadata else None
        if extra:
            rows = list(extra)
            break
    if not rows:
        return
    console.print()
    console.print("[bold]Circuit[/bold]  [dim]Qiskit draw · unique gates[/dim]")
    table = Table(show_header=False, box=None, pad_edge=False, padding=(0, 2, 0, 0))
    table.add_column("gate", style="cyan", no_wrap=True)
    table.add_column("explainer")
    for row in rows:
        table.add_row(row.get("label", row.get("name", "")), row.get("explainer", ""))
    console.print(table)


def _print_artifacts(result: ExperimentResult) -> None:
    """Print saved files so a CLI run is not a silent write to results/."""
    if not result.artifacts:
        return
    console.print()
    console.print("[bold]Saved[/bold]")
    preferred = ("histogram", "analysis", "metrics_summary", "circuit")
    ordered = sorted(
        result.artifacts,
        key=lambda a: preferred.index(a.kind) if a.kind in preferred else len(preferred),
    )
    for artifact in ordered:
        _print_path(artifact.kind, artifact.path)


def _bar(fraction: float, width: int = 22) -> str:
    filled = int(round(max(0.0, min(1.0, fraction)) * width))
    return "█" * filled + "░" * (width - filled)


def _print_counts(result: ExperimentResult) -> None:
    if not (result.analysis and result.analysis.measurement_results):
        return
    meas = result.analysis.measurement_results
    total = meas.total_shots or 1
    ranked = sorted(meas.raw_counts.items(), key=lambda kv: kv[1], reverse=True)
    shown = ranked[:8]
    console.print()
    console.print(f"[bold]Outcomes[/bold]  [dim]{meas.total_shots} shots[/dim]")
    table = Table(show_header=False, box=None, pad_edge=False, padding=(0, 1, 0, 0))
    table.add_column("bitstring", style="cyan", no_wrap=True)
    table.add_column("bar", no_wrap=True)
    table.add_column("pct", justify="right", style="dim")
    for bitstring, count in shown:
        frac = count / total
        table.add_row(str(bitstring), _bar(frac), f"{100 * frac:5.1f}%")
    console.print(table)
    extra = len(ranked) - len(shown)
    if extra > 0:
        console.print(f"[dim]  … {extra} more in the histogram[/dim]")


def _print_metrics(result: ExperimentResult) -> None:
    if not result.metrics_bundle:
        return
    bundle = result.metrics_bundle
    console.print()
    label = f"Metrics · {bundle.profile}" if bundle.profile else "Metrics"
    console.print(f"[bold]{label}[/bold]")
    table = Table(show_header=False, box=None, pad_edge=False, padding=(0, 2, 0, 0))
    table.add_column("name", style="cyan")
    table.add_column("value", justify="right")
    for name, entry in sorted(bundle.metrics.items()):
        table.add_row(name, f"{entry.value:.4f}")
    console.print(table)


def _print_observables(result: ExperimentResult) -> None:
    measurements = result.analysis.measurement_results if result.analysis else None
    estimates = measurements.observables if measurements is not None else None
    if not estimates:
        return
    console.print()
    console.print("[bold]Observables[/bold]")
    table = Table(show_header=False, box=None, pad_edge=False, padding=(0, 2, 0, 0))
    table.add_column("pauli", style="cyan")
    table.add_column("value", justify="right")
    table.add_column("stderr", justify="right", style="dim")
    for pauli, entry in estimates.items():
        stderr = f"±{entry.stderr:.4f}" if entry.stderr is not None else "exact"
        table.add_row(pauli, f"{entry.value:.4f}", stderr)
    console.print(table)


def _print_extras(result: ExperimentResult) -> None:
    """Print experiment-program extras (VQE energy, QAOA MaxCut) that are not engine fields."""
    extras = {
        key: value for key, value in (result.__pydantic_extra__ or {}).items() if value is not None
    }
    if not extras:
        return
    console.print()
    console.print("[bold]Interpretation[/bold]")
    table = Table(show_header=False, box=None, pad_edge=False, padding=(0, 2, 0, 0))
    table.add_column("name", style="cyan")
    table.add_column("value", justify="right")
    for key, value in extras.items():
        if isinstance(value, float):
            table.add_row(key, f"{value:.6f}")
        else:
            table.add_row(key, str(value))
    console.print(table)


def _print_result(
    result: ExperimentResult,
    json_output: bool,
    title: str | None = None,
    metrics_hint: str | None = None,
) -> None:
    """Print experiment result in the requested format."""
    if json_output:
        console.print(result.model_dump_json(indent=2))
        return

    params = result.analysis.experiment_parameters if result.analysis else {}
    n = params.get("num_qubits")
    state = params.get("state_type")
    bits = f"{n} qubit" + ("" if n == 1 else "s") if n is not None else None
    headline = "  ·  ".join(str(p) for p in (title, bits, state) if p)
    if headline and title:
        pass  # title already printed by the command
    if bits or state:
        console.print(f"[dim]{bits}  ·  {state}[/dim]")

    _print_counts(result)
    _print_metrics(result)
    _print_observables(result)
    _print_extras(result)
    if metrics_hint:
        console.print(f"[dim]{metrics_hint}[/dim]")
    _print_gate_explainers(result)
    _print_artifacts(result)


def _print_sweep(
    results: list[ExperimentResult],
    range_keys: list[str],
    json_output: bool,
) -> None:
    """Print a one-row-per-point sweep summary."""
    if json_output:
        payload = [json.loads(r.model_dump_json()) for r in results]
        console.print(json.dumps(payload, indent=2))
        return

    console.print()
    console.print(f"[bold]{len(results)} run(s)[/bold]")

    has_ss = any(
        result.metrics_bundle is not None and "structure_score" in result.metrics_bundle.metrics
        for result in results
    )
    has_hist = any(any(a.kind == "histogram" for a in result.artifacts) for result in results)

    table = Table(show_header=True, header_style="bold", box=None, pad_edge=False)
    for key in range_keys:
        table.add_column(key, style="cyan")
    if has_ss:
        table.add_column("structure_score", justify="right")
    table.add_column("top", style="dim")
    if has_hist:
        table.add_column("histogram", overflow="fold", no_wrap=True)

    for result in results:
        params = result.analysis.experiment_parameters if result.analysis else {}
        row = [str(params.get(key, "")) for key in range_keys]
        if has_ss:
            ss = ""
            if result.metrics_bundle and "structure_score" in result.metrics_bundle.metrics:
                ss = f"{result.metrics_bundle.metrics['structure_score'].value:.4f}"
            row.append(ss)
        top = ""
        if result.analysis and result.analysis.measurement_results:
            counts = result.analysis.measurement_results.raw_counts
            if counts:
                bitstring, _n = max(counts.items(), key=lambda kv: kv[1])
                top = str(bitstring)
        row.append(top)
        if has_hist:
            hist = next(
                (_display_path(a.path) for a in result.artifacts if a.kind == "histogram"),
                "",
            )
            row.append(hist)
        table.add_row(*row)

    console.print(table)
    if results and not has_hist:
        _print_artifacts(results[-1])
        if len(results) > 1:
            console.print("[dim]Each point has its own folder under results/.[/dim]")


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
