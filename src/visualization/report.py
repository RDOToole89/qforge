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
    if fmt == "md":
        content = render_markdown(ctx)
        out = Path(json_path).with_suffix("")
        out = out.as_posix() + "_report.md"
        Path(out).write_text(content, encoding="utf-8")
        return out
    if fmt == "html":
        content = render_html(ctx)
        out = Path(json_path).with_suffix("")
        out = out.as_posix() + "_report.html"
        Path(out).write_text(content, encoding="utf-8")
        return out
    raise ValueError(f"Unsupported report format: {fmt}")
