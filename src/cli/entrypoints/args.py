from __future__ import annotations

import os
import sys
from typing import List

from src.cli.headless.run import (
    run_by_name as headless_run_by_name,
    run_from_config as headless_run_from_config,
)
from src.cli.headless.sweep import run_from_manifest as headless_run_sweep
from src.cli.headless.viz import render_from_json as headless_viz
from src.cli.interactive_app import InteractiveCLI
from src.utils import logger as logger_utils
from main import apply_profile_from_args, setup_environment, show_help, list_experiments


def dispatch(argv: List[str]) -> int:
    setup_environment()

    args = list(argv)
    args = apply_profile_from_args(args)

    console_json = "-J" in args or "--json-only" in args
    if "--stream-logs" in args or "-q" in args or "--quiet" in args or console_json:
        try:
            logger_utils.setup_logger(
                log_level=os.environ.get("QUANTUM_LOG_LEVEL", "INFO"),
                log_to_file=False,
                log_to_console=True,
                structured_log_file=(
                    "logs/structured_logs.json" if "--stream-logs" in args else None
                ),
                console_json_mode=console_json,
            )
        except Exception:
            pass
        for flag in [
            "-q",
            "--quiet",
            "-J",
            "--json-only",
            "-v",
            "--verbose",
            "--stream-logs",
        ]:
            while flag in args:
                args.remove(flag)

    if not args:
        InteractiveCLI().run_interactive_session()
        return 0
    if args[0] in {"--help", "-h"}:
        show_help()
        return 0
    if args[0] == "--list":
        list_experiments()
        return 0
    if args[0] == "--run" and len(args) > 1:
        headless_run_by_name(args[1])
        return 0
    if args[0] == "run" and len(args) > 2 and args[1] == "--preset":
        headless_run_by_name(args[2])
        return 0
    if args[0] == "run" and len(args) > 2 and args[1] == "--config":
        headless_run_from_config(args[2])
        return 0
    if args[0] == "--sweep" and len(args) > 1:
        # legacy style still supported
        from main import run_parameter_sweep

        run_parameter_sweep(args[1])
        return 0
    if args[0] == "sweep" and len(args) > 2 and args[1] == "--manifest":
        headless_run_sweep(args[2])
        return 0
    if args[0] == "--viz" and len(args) > 1:
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
        headless_viz(args[1], viz_type=viz_type, backend=backend, outdir=outdir)
        return 0
    if args[0] == "viz" and len(args) > 2 and args[1] == "--from":
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
        headless_viz(args[2], viz_type=viz_type, backend=backend, outdir=outdir)
        return 0
    if args[0] == "report" and len(args) > 2 and args[1] == "--from":
        fmt = "md"
        if "--format" in args:
            try:
                fmt = args[args.index("--format") + 1]
            except Exception:
                pass
        from src.visualization.report import save_report_from_json

        out = save_report_from_json(args[2], fmt=fmt)
        from logging import getLogger

        getLogger(__name__).info(f"📝 Report saved to: {out}")
        return 0

    print("❌ Invalid arguments. Use --help for usage information.")
    return 1
