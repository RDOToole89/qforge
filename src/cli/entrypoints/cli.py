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

# Pipeline removed for simplification
from pathlib import Path as _Path
import json as _json

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


# viz-pipe command removed - use viz instead


@app.command("results-clean")
def results_clean(
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be deleted"),
):
    """Remove legacy flat results and demo folders to declutter the results directory."""
    base = _Path("results")
    targets = []
    # Legacy JSONs under structured_decoherence/
    targets += list((base / "structured_decoherence").glob("*.json"))
    # Legacy reports next to analysis
    targets += list((base / "structured_decoherence").glob("*_report.*"))
    # Demo out folder
    viz_demo = base / "structured_decoherence" / "viz_demo_out"
    if viz_demo.exists():
        targets.append(viz_demo)
    # Execute
    for p in targets:
        typer.echo(f"DELETE {p}")
        if not dry_run:
            if p.is_dir():
                import shutil as _shutil

                _shutil.rmtree(p, ignore_errors=True)
            else:
                try:
                    p.unlink()
                except FileNotFoundError:
                    pass


@app.command("results-index")
def results_index():
    """Create results/index.json catalog of per-run directories."""
    base = _Path("results")
    entries = []
    for date_dir in sorted(base.glob("[0-9]" * 8)):
        if not date_dir.is_dir():
            continue
        for run_dir in sorted(date_dir.iterdir()):
            if not run_dir.is_dir():
                continue
            analysis_json = run_dir / "analysis" / "analysis.json"
            if analysis_json.exists():
                try:
                    a = _json.loads(analysis_json.read_text(encoding="utf-8"))
                except Exception:
                    a = {}
                entries.append(
                    {
                        "run_dir": str(run_dir),
                        "analysis_path": str(analysis_json),
                        "timestamp": a.get("experiment_metadata", {}).get("timestamp"),
                        "state_type": a.get("experiment_parameters", {}).get(
                            "state_type"
                        ),
                        "research_type": a.get("experiment_metadata", {}).get(
                            "research_type"
                        ),
                    }
                )
    (base / "index.json").write_text(_json.dumps(entries, indent=2), encoding="utf-8")
    typer.echo(f"Wrote {len(entries)} entries to results/index.json")


@app.command("results-latest")
def results_latest():
    """Create/refresh results/latest symlink to the newest run directory."""
    base = _Path("results")
    runs = []
    for date_dir in base.glob("[0-9]" * 8):
        if date_dir.is_dir():
            for run_dir in date_dir.iterdir():
                if (run_dir / "analysis" / "analysis.json").exists():
                    runs.append(run_dir)
    if not runs:
        typer.echo("No runs found")
        raise typer.Exit(code=1)
    newest = sorted(runs)[-1]
    link = base / "latest"
    try:
        if link.exists() or link.is_symlink():
            link.unlink()
        link.symlink_to(newest)
        typer.echo(f"latest -> {newest}")
    except Exception as e:
        typer.echo(f"Failed to create symlink: {e}", err=True)


def main() -> int:
    app()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
