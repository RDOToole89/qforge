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
        # Determine filename per legacy policy
        meta = analysis.get("experiment_metadata", {})
        timestamp = meta.get("timestamp") or analysis.get("timestamp")
        exp_id = meta.get("experiment_id", "experiment")
        research_type = meta.get("research_type", "experiment")
        prov = analysis.get("provenance", {})
        cfg_hash = prov.get("config_hash", "")
        hash_segment = f"_{cfg_hash}" if cfg_hash else ""

        # Choose subdir
        if "sweep" in str(research_type) or "batch" in str(research_type):
            subdir = "parameter_sweeps"
        elif "convergence" in str(research_type):
            subdir = "convergence_tests"
        else:
            subdir = "structured_decoherence"

        filename = f"{research_type}_{exp_id[:8]}_{(timestamp or '').replace(':','-').replace('T','_')}{hash_segment}.json"
        # Fallback name if timestamp missing
        if not timestamp:
            from datetime import datetime

            filename = f"{research_type}_{exp_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{hash_segment}.json"

        rel_path = f"{subdir}/{filename}"
        abs_path = Path(self.save_json(rel_path, analysis))
        # Compute checksum and optionally attach (not persisted back here)
        _ = self._checksum(abs_path)
        return str(abs_path)
