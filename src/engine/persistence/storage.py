"""Storage interfaces and local implementation (engine-native, schema-aware).

Purpose
-------
Provide a robust storage layer for experiment outputs that:
- Uses atomic JSON writes (tmp -> replace) to avoid partial files
- Derives directory layout from `DirectoryStructure`
- Derives filename policy from `StorageConfig.filename_template`
- Falls back to a sensible, descriptive default when config is absent
- Optionally compresses JSON (.json.gz) based on `StorageConfig.compress_raw_data`
- Maintains a simple JSONL "artifact ledger" per directory for later indexing

Integration
-----------
- Directory choice uses DirectoryStructure.get_path(..., category="experiments", ...)
- Filename policy uses StorageConfig.filename_template if provided, with fields:
    {research_type} {experiment_id} {timestamp} {state_type} {num_qubits}
    {shots} {noise_desc} {config_hash}
- If config is not supplied, a descriptive fallback filename is used.

Notes:
-----
- `ArtifactRef` is imported from src.engine.models to keep a single source of truth.
- This module intentionally stays small; richer policies (archival/retention)
  can be layered on top later using your models in src/engine/models/storage.py.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import os
import re
import tempfile
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any

from src.engine.models.storage import (
    ArtifactRef,  # canonical Pydantic model
    DirectoryStructure,  # optional layout
    StorageConfig,  # optional policy
)

# ---------- Interfaces ----------


class Storage(ABC):
    """Abstract storage interface."""

    @abstractmethod
    def save_json(
        self, rel_path: str, data: dict[str, Any], *, compress: bool | None = None
    ) -> str:
        """Persist JSON (atomically). Returns absolute path."""
        raise NotImplementedError

    @abstractmethod
    def register_artifact(self, artifact: ArtifactRef) -> None:
        """Record an artifact in a simple ledger (optional override)."""
        raise NotImplementedError

    @abstractmethod
    def save_analysis(self, analysis: dict[str, Any]) -> str:
        """Persist a research analysis dict and return absolute path."""
        raise NotImplementedError


# ---------- Local filesystem implementation ----------


class LocalStorage(Storage):
    """Filesystem-backed storage with schema-aware layout.

    Directory Layout
    ----------------
    If DirectoryStructure is provided:
        base/<structure.get_path(category='experiments', ...)>/<filename>
    Else (fallback):
        base/<YYYYMMDD>/<filename>

    Filename Policy
    ---------------
    If StorageConfig.filename_template is provided, it is formatted with:
        research_type, experiment_id, timestamp, state_type, num_qubits,
        shots, noise_desc, config_hash
    The result is sanitized and suffixed with .json or .json.gz

    Fallback filename (when no StorageConfig provided):
        <HHMMSS>_<STATE>_<QUBITS>q_<NOISE>_<SHOTS>shots_<RESEARCH>_<HASH>.json[.gz]
    """

    def __init__(
        self,
        base_dir: str = "results",
        *,
        structure: DirectoryStructure | None = None,
        config: StorageConfig | None = None,
    ) -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.structure = structure
        self.config = config
        self._ledger_name = "artifacts.jsonl"

    # ---- Public API ----

    def save_json(
        self, rel_path: str, data: dict[str, Any], *, compress: bool | None = None
    ) -> str:
        """Save JSON atomically at base_dir/rel_path. Returns absolute path.

        If compress is True (or rel_path ends with .gz), writes JSON GZIP.
        """
        target = self.base_dir / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)

        use_gzip = (compress is True) or str(target).endswith(".gz")

        if use_gzip and not str(target).endswith(".gz"):
            target = target.with_suffix(target.suffix + ".gz")

        # Atomic write via temp file then replace
        if use_gzip:
            with tempfile.NamedTemporaryFile("wb", delete=False, dir=target.parent) as tmp:
                with gzip.GzipFile(fileobj=tmp, mode="wb") as gz:
                    gz.write(json.dumps(data, indent=2, default=str).encode("utf-8"))
                tmp_path = Path(tmp.name)
        else:
            with tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", delete=False, dir=target.parent
            ) as tmp:
                json.dump(data, tmp, indent=2, default=str)
                tmp_path = Path(tmp.name)

        os.replace(tmp_path, target)  # atomic on POSIX
        return str(target.resolve())

    def register_artifact(self, artifact: ArtifactRef) -> None:
        """Append artifact metadata to a per-directory JSONL ledger for lightweight indexing.

        Safe to call even if the path's directory doesn't exist yet.
        """
        p = Path(artifact.path)
        # Resolve relative paths into the storage base
        dir_path = (p if p.is_absolute() else (self.base_dir / p)).parent
        dir_path.mkdir(parents=True, exist_ok=True)
        ledger = dir_path / self._ledger_name

        record = artifact.model_dump()
        with open(ledger, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=str) + "\n")

    def save_analysis(self, analysis: dict[str, Any]) -> str:
        """Persist analysis with structure-aware directory and filename policy.

        Consumed keys (best-effort):
        - experiment_metadata: {experiment_id, timestamp, research_type}
        - experiment_parameters: {state_type, num_qubits, shots,
          noise_enabled, noise_type, error_rate, t1, t2}
        - provenance: {config_hash}
        """
        dt = _extract_datetime(analysis)
        # Descriptive tokens
        meta = analysis.get("experiment_metadata", {}) or {}
        params = analysis.get("experiment_parameters", {}) or {}
        prov = analysis.get("provenance", {}) or {}

        research_type = (meta.get("research_type") or "baseline").lower()
        research_type = "baseline" if research_type in {"none", "null"} else research_type

        experiment_id = str(meta.get("experiment_id") or "exp")
        state_type = str(params.get("state_type") or "unknown").upper()
        num_qubits = int(params.get("num_qubits") or 0)
        shots = int(params.get("shots") or 0)
        noise_desc = _noise_segment(params)
        cfg_hash = (prov.get("config_hash") or "")[:8] or "00000000"

        # Choose directory
        if self.structure is not None:
            dir_path = self.structure.get_path(
                base=self.base_dir,
                category="experiments",
                timestamp=dt,
                research_type=research_type,
                state_type=state_type,
            )
        else:
            date_dir = self.base_dir / dt.strftime("%Y-%m-%d")
            experiment_dir_name = f"{state_type}_{num_qubits}q_{noise_desc}_{shots}shots_{cfg_hash}"
            dir_path = date_dir / experiment_dir_name
        dir_path.mkdir(parents=True, exist_ok=True)

        # Choose filename
        if self.config is not None and self.config.filename_template:
            # Allow both '{timestamp}' (ISO) and '{timestr}' (HHMMSS)
            fmt_kwargs = {
                "research_type": research_type,
                "experiment_id": experiment_id,
                "timestamp": dt.isoformat(),
                "timestr": dt.strftime("%H%M%S"),
                "state_type": state_type,
                "num_qubits": num_qubits,
                "shots": shots,
                "noise_desc": noise_desc,
                "config_hash": cfg_hash,
            }
            raw_name = self.config.filename_template.format(**fmt_kwargs)
            base_name = _sanitize_filename(raw_name)
        else:
            base_name = "analysis"

        # Decide extension / compression
        compress = None
        if self.config is not None and self.config.compress_raw_data:
            compress = True
        filename = base_name + (".json.gz" if compress else ".json")

        rel_path = str((dir_path / filename).relative_to(self.base_dir))
        abs_path = Path(self.save_json(rel_path, analysis, compress=compress))

        # Optionally self-register the saved analysis as an artifact
        try:
            self.register_artifact(
                ArtifactRef(
                    kind="analysis",
                    path=str(abs_path),
                    metadata={
                        "research_type": research_type,
                        "state_type": state_type,
                        "num_qubits": num_qubits,
                        "shots": shots,
                        "config_hash": cfg_hash,
                    },
                )
            )
        except Exception:
            # non-fatal
            pass

        # Precompute checksum (not stored yet; useful for future manifests)
        _ = _checksum(abs_path)
        return str(abs_path)


# ---------- Internal utilities ----------


def _extract_datetime(analysis: dict[str, Any]) -> datetime:
    """Parse ISO timestamp from analysis, falling back to now(). Accepts 'Z' suffix."""
    ts = (analysis.get("experiment_metadata", {}) or {}).get("timestamp") or analysis.get(
        "timestamp"
    )
    if isinstance(ts, datetime):
        return ts
    if isinstance(ts, str) and ts:
        try:
            return datetime.fromisoformat(ts.replace("Z", ""))
        except Exception:
            pass
    return datetime.now()


def _slug(text: str) -> str:
    """Filesystem-safe token: letters, digits, underscore only; lower-cased."""
    text = text.strip().lower()
    return re.sub(r"[^a-z0-9]+", "_", text).strip("_") or "unknown"


def _sanitize_filename(name: str) -> str:
    """Sanitize a filename template result.

    - Replace path separators
    - Collapse whitespace/punct to underscores
    - Keep dots (for extensions) but remove extra dots in the stem.
    """
    # Split stem + ext to preserve extension dots
    stem, *ext = name.split(".")
    safe_stem = _slug(stem)
    if ext:
        # preserve final extension if present in template; otherwise we'll add .json later
        return safe_stem + "." + ".".join(ext)
    return safe_stem


def _noise_segment(params: dict[str, Any]) -> str:
    """Build a short, readable noise description.

    Examples:
      - no noise        -> "clean"
      - depolarizing    -> "depolarizing_0.02"
      - thermal_relax.  -> "thermal_t1_100000us_t2_80000us" (if t1/t2 provided)
    """
    if not params.get("noise_enabled"):
        return "clean"

    ntype = str(params.get("noise_type", "unknown")).lower()
    t1 = params.get("t1")
    t2 = params.get("t2")
    err = params.get("error_rate")

    if ntype in {"thermal_relaxation", "thermal"} and (t1 is not None) and (t2 is not None):
        try:
            t1_us = int(float(t1) * 1e6)
            t2_us = int(float(t2) * 1e6)
            return f"thermal_t1_{t1_us}us_t2_{t2_us}us"
        except Exception:
            pass

    if err is not None:
        try:
            return f"{_slug(ntype)}_{float(err):g}"
        except Exception:
            return _slug(ntype)

    return _slug(ntype)


def _checksum(path: Path) -> str:
    h = hashlib.sha1()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()
