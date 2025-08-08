from __future__ import annotations

import json
from pathlib import Path

from src.visualization.reporting import (
    build_report_context,
    render_markdown,
    render_html,
)


def save_report_from_json(json_path: str, fmt: str = "md") -> str:
    analysis = json.loads(Path(json_path).read_text(encoding="utf-8"))
    ctx = build_report_context(analysis)
    path_obj = Path(json_path)
    # Default to run_dir/reports when analysis path follows run_dir pattern
    run_reports = None
    try:
        if path_obj.parent.name == "analysis":
            run_reports = path_obj.parent.parent / "reports"
            run_reports.mkdir(parents=True, exist_ok=True)
    except Exception:
        run_reports = None

    reports_dir = run_reports or Path("results/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    # Determine a meaningful stem. If under run_dir, use YYYYMMDD_HHMMSS_slug
    if run_reports:
        date_dir = path_obj.parents[2].name  # YYYYMMDD
        run_name = path_obj.parent.parent.name  # HHMMSS_slug
        stem = f"{date_dir}_{run_name}"
    else:
        stem = path_obj.stem
    if fmt == "md":
        content = render_markdown(ctx)
        out = reports_dir / f"{stem}.md"
        out.write_text(content, encoding="utf-8")
        return str(out)
    if fmt == "html":
        content = render_html(ctx)
        out = reports_dir / f"{stem}.html"
        out.write_text(content, encoding="utf-8")
        return str(out)
    raise ValueError(f"Unsupported report format: {fmt}")
