"""Storage interfaces (Phase 0 skeleton)."""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
import hashlib
import json


@dataclass
class ArtifactRef:
    kind: str
    path: str
    metadata: Dict[str, Any]


class Storage:
    def save_json(self, rel_path: str, data: Dict[str, Any]) -> str:  # returns abs path
        raise NotImplementedError

    def register_artifact(self, artifact: ArtifactRef) -> None:
        pass

    def save_analysis(self, analysis: Dict[str, Any]) -> str:
        """Persist a research analysis dict and return absolute path.

        Mirrors the legacy path policy to maintain compatibility.
        """
        raise NotImplementedError


class LocalStorage(Storage):
    def __init__(self, base_dir: str = "results") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_json(self, rel_path: str, data: Dict[str, Any]) -> str:
        p = self.base_dir / rel_path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return str(p.resolve())

    def register_artifact(self, artifact: ArtifactRef) -> None:
        # Phase 0/4: no-op registry; callers may track artifacts in results
        return

    def _checksum(self, path: Path) -> str:
        h = hashlib.sha1()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    def save_analysis(self, analysis: Dict[str, Any]) -> str:
        """Persist analysis under a per-run directory and return absolute path.

        New structure:
        results/<YYYYMMDD>/<HHMMSS>_<slug>/analysis/analysis.json
        """
        from datetime import datetime

        meta = analysis.get("experiment_metadata", {})
        ts = meta.get("timestamp") or analysis.get("timestamp")
        try:
            # Normalize timestamps like 2025-08-08T16:34:38 to date/time
            dt = (
                datetime.fromisoformat(str(ts).replace("Z", ""))
                if ts
                else datetime.now()
            )
        except Exception:
            dt = datetime.now()
        date_str = dt.strftime("%Y%m%d")
        time_str = dt.strftime("%H%M%S")

        research_type = str(meta.get("research_type", "experiment")).lower()
        state = str(
            analysis.get("experiment_parameters", {}).get("state_type", "state")
        ).lower()
        prov = analysis.get("provenance", {})
        cfg_hash = prov.get("config_hash") or ""
        slug = f"{state}_{research_type}"
        if cfg_hash:
            slug += f"_{cfg_hash[:8]}"

        run_dir = self.base_dir / date_str / f"{time_str}_{slug}"
        analysis_dir = run_dir / "analysis"
        analysis_dir.mkdir(parents=True, exist_ok=True)
        rel_path = analysis_dir.relative_to(self.base_dir) / "analysis.json"

        abs_path = Path(self.save_json(str(rel_path), analysis))
        _ = self._checksum(abs_path)
        return str(abs_path)
