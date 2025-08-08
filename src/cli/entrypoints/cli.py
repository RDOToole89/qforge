from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import typer

from src.cli.headless.run import (
    run_by_name as headless_run_by_name,
    run_from_config as headless_run_from_config,
)
from src.cli.headless.sweep import run_from_manifest as headless_run_sweep
from src.cli.headless.viz import render_from_json as headless_viz

app = typer.Typer(help="Quantum Experiment Framework CLI (Typer entrypoint)")


@app.callback()
def common_flags(
    use_engine: bool = typer.Option(
        False,
        "--use-engine",
        help="Route through engine API (equivalent to QEXP_USE_ENGINE_API=1)",
    ),
    profile: Optional[str] = typer.Option(
        None, "--profile", help="Apply a named profile before running"
    ),
):
    from main import apply_profile_from_args

    if use_engine:
        os.environ["QEXP_USE_ENGINE_API"] = "1"
    args: list[str] = []
    if profile:
        args = ["--profile", profile]
    if args:
        apply_profile_from_args(args)


@app.command("run")
def run(
    preset: Optional[str] = typer.Option(None, "--preset", help="Preset experiment id"),
    config: Optional[Path] = typer.Option(None, "--config", help="Path to config file"),
):
    if (preset is None) == (config is None):
        typer.echo("Specify exactly one of --preset or --config", err=True)
        raise typer.Exit(code=2)
    if preset is not None:
        headless_run_by_name(preset)
    else:
        headless_run_from_config(str(config))


@app.command("sweep")
def sweep(
    manifest: Path = typer.Option(
        ..., "--manifest", help="Path to sweep manifest file"
    ),
):
    headless_run_sweep(str(manifest))


@app.command("viz")
def viz(
    from_path: Path = typer.Option(..., "--from", help="Path to results JSON"),
    type: str = typer.Option("histogram", "--type", help="Visualization type"),
    backend: Optional[str] = typer.Option(None, "--backend", help="Backend name"),
    outdir: Optional[Path] = typer.Option(None, "--outdir", help="Output directory"),
):
    headless_viz(
        str(from_path),
        viz_type=type,
        backend=backend,
        outdir=str(outdir) if outdir else None,
    )


def main() -> int:
    app()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
