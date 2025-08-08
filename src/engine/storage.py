"""Storage interfaces (Phase 0 skeleton)."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


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


class LocalStorage(Storage):
    def __init__(self, base_dir: str = "results") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_json(self, rel_path: str, data: Dict[str, Any]) -> str:
        p = self.base_dir / rel_path
        p.parent.mkdir(parents=True, exist_ok=True)
        import json
        p.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return str(p.resolve())

    def register_artifact(self, artifact: ArtifactRef) -> None:
        # Phase 0: no-op
        return
