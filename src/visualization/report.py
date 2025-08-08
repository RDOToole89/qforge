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
    reports_dir = Path("results/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    stem = Path(json_path).stem
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
