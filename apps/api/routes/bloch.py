"""Bloch sphere visualization endpoints.

Thin HTTP layer over src.engine.bloch_math. Handles file loading,
path validation, and request/response serialization.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.engine.bloch_math import compute_bloch_data

router = APIRouter()

RESULTS_DIR = Path("results")


# ── Endpoints ────────────────────────────────────────────────────────


@router.get("/{filename:path}")
def get_bloch_data(filename: str) -> dict[str, Any]:
    """Transform a stored experiment result into Bloch sphere visualization data."""
    path = RESULTS_DIR / filename
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail=f"Result not found: {filename}")

    try:
        path.resolve().relative_to(RESULTS_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Result file is not valid JSON")

    try:
        return compute_bloch_data(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Sweep ────────────────────────────────────────────────────────────


class BlochSweepRequest(BaseModel):
    """Request body for a Bloch sweep across error rates."""

    state_type: str = Field(default="GHZ", description="Quantum state type")
    num_qubits: int = Field(default=3, ge=1, le=8)
    noise_type: str = Field(default="depolarizing")
    error_rates: list[float] = Field(
        description="Error rates to sweep (e.g. [0, 0.02, 0.05, 0.1, 0.2, 0.3])"
    )
    sim_mode: str = Field(
        default="density_matrix",
        description="Simulation mode. density_matrix gives full Bloch info; qasm gives Z-only.",
    )
    shots: int = Field(default=4096, ge=100, le=100000)
    rng_seed: int | None = Field(default=42)


@router.post("/sweep")
def run_bloch_sweep(req: BlochSweepRequest) -> dict[str, Any]:
    """Run experiments at multiple error rates and return Bloch snapshots."""
    from src.engine.api import run as engine_run
    from src.engine.models import ExperimentConfig

    snapshots = []

    for error_rate in req.error_rates:
        noise_enabled = error_rate > 0
        sim_mode = req.sim_mode
        if sim_mode == "statevector" and noise_enabled:
            sim_mode = "density_matrix"

        cfg = ExperimentConfig(
            num_qubits=req.num_qubits,
            state_type=req.state_type,
            sim_mode=sim_mode,
            shots=req.shots,
            noise_enabled=noise_enabled,
            noise_type=req.noise_type if noise_enabled else None,
            error_rate=error_rate if noise_enabled else None,
            rng_seed=req.rng_seed,
            visualization_type="none",
        )

        result = engine_run(cfg)
        result_dict = result.model_dump()

        try:
            bloch = compute_bloch_data(result_dict)
            bloch["error_rate"] = error_rate
            snapshots.append(bloch)
        except ValueError as e:
            snapshots.append({
                "error_rate": error_rate,
                "error": str(e),
            })

    return {
        "state_type": req.state_type,
        "num_qubits": req.num_qubits,
        "noise_type": req.noise_type,
        "sim_mode": req.sim_mode,
        "error_rates": req.error_rates,
        "snapshots": snapshots,
    }
