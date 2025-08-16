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
        """Persist analysis with descriptive filename for easy browsing.

        New structure:
        results/<YYYYMMDD>/<HHMMSS>_<STATE>_<QUBITS>q_<NOISE>_<SHOTS>shots_<RESEARCH>_<HASH>.json
        
        Example:
        results/20250816/185601_GHZ_3q_clean_1024shots_baseline_a1b2c3d4.json
        """
        from datetime import datetime

        # Extract timestamp
        meta = analysis.get("experiment_metadata", {})
        ts = meta.get("timestamp") or analysis.get("timestamp")
        try:
            dt = (
                datetime.fromisoformat(str(ts).replace("Z", ""))
                if ts
                else datetime.now()
            )
        except Exception:
            dt = datetime.now()
        date_str = dt.strftime("%Y%m%d")
        time_str = dt.strftime("%H%M%S")

        # Extract experiment parameters
        params = analysis.get("experiment_parameters", {})
        state = str(params.get("state_type", "UNKNOWN")).upper()
        num_qubits = params.get("num_qubits", 0)
        shots = params.get("shots", 1024)
        
        # Build noise description
        noise_enabled = params.get("noise_enabled", False)
        if not noise_enabled:
            noise_desc = "clean"
        else:
            noise_type = params.get("noise_type", "unknown")
            error_rate = params.get("error_rate")
            t1 = params.get("t1")
            t2 = params.get("t2")
            
            if noise_type == "thermal_relaxation" and t1 and t2:
                noise_desc = f"thermal_T1_{int(t1*1e6)}us_T2_{int(t2*1e6)}us"
            elif error_rate is not None:
                noise_desc = f"{noise_type}_{error_rate}"
            else:
                noise_desc = noise_type
        
        # Research type
        research_type = str(meta.get("research_type") or "baseline").lower()
        if research_type == "none" or research_type == "null":
            research_type = "baseline"
        
        # Config hash for uniqueness
        prov = analysis.get("provenance", {})
        cfg_hash = prov.get("config_hash", "")[:8] or "00000000"
        
        # Build descriptive filename
        filename = f"{time_str}_{state}_{num_qubits}q_{noise_desc}_{shots}shots_{research_type}_{cfg_hash}.json"
        
        # Save directly to date directory (no subdirectory)
        date_dir = self.base_dir / date_str
        date_dir.mkdir(parents=True, exist_ok=True)
        rel_path = date_str + "/" + filename
        
        abs_path = Path(self.save_json(rel_path, analysis))
        _ = self._checksum(abs_path)
        return str(abs_path)
