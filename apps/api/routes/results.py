"""Result endpoints: list and retrieve stored experiment results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

# Default results directory (matches engine storage conventions)
RESULTS_DIR = Path("results")


@router.get("")
def list_results(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[dict[str, Any]]:
    """List stored result JSON files, newest first."""
    if not RESULTS_DIR.exists():
        return []

    json_files = sorted(RESULTS_DIR.rglob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    page = json_files[offset : offset + limit]

    entries = []
    for path in page:
        try:
            data = json.loads(path.read_text())
            entries.append(
                {
                    "filename": str(path.relative_to(RESULTS_DIR)),
                    "size_bytes": path.stat().st_size,
                    "modified": path.stat().st_mtime,
                    "experiment_id": _safe_get(data, "experiment_metadata", "experiment_id"),
                    "num_qubits": _safe_get(data, "experiment_parameters", "num_qubits"),
                    "state_type": _safe_get(data, "experiment_parameters", "state_type"),
                }
            )
        except (json.JSONDecodeError, OSError):
            entries.append({"filename": str(path.relative_to(RESULTS_DIR)), "error": "unreadable"})

    return entries


@router.get("/{filename:path}")
def get_result(filename: str) -> dict[str, Any]:
    """Retrieve a specific result JSON by filename."""
    path = RESULTS_DIR / filename
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail=f"Result not found: {filename}")

    # Prevent path traversal
    try:
        path.resolve().relative_to(RESULTS_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Result file is not valid JSON")


def _safe_get(data: dict, *keys: str) -> Any:
    """Safely traverse nested dicts."""
    for k in keys:
        if isinstance(data, dict):
            data = data.get(k)
        else:
            return None
    return data
