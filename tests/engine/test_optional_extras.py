"""Install extras: engine must not require FastAPI."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _pyproject() -> dict:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def test_fastapi_is_an_optional_api_extra() -> None:
    project = _pyproject()["project"]
    required = " ".join(project["dependencies"]).lower()
    assert "fastapi" not in required
    assert "uvicorn" not in required
    api = project["optional-dependencies"]["api"]
    joined = " ".join(api).lower()
    assert "fastapi" in joined
    assert "uvicorn" in joined
