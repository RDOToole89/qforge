from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Optional
import json

from src.visualization.save_manager import set_save_manager_base_dir


def read_analysis_json(json_path: str | Path) -> Mapping[str, Any]:
    p = Path(json_path)
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"Failed to read analysis JSON at '{p}': {exc}") from exc


def configure_output_base_dir(base_dir: Optional[str]) -> None:
    if not base_dir:
        return
    try:
        set_save_manager_base_dir(base_dir)
    except Exception:
        # Non-fatal; default base dir will be used
        pass
