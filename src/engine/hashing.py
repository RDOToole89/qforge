"""Canonical hashing helpers (Phase 0 skeleton)."""
from __future__ import annotations
import hashlib
import json
from typing import Any, Mapping


def canonical_dumps(data: Mapping[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha1_of(data: Mapping[str, Any]) -> str:
    return hashlib.sha1(canonical_dumps(data).encode("utf-8")).hexdigest()
