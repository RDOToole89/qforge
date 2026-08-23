"""Skip the HTTP suite when FastAPI is not installed (engine-only extra)."""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")
