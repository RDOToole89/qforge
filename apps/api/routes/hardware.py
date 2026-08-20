"""Hardware feasibility endpoints.

Thin HTTP layer over the engine's hardware feasibility checks. Lets the
frontend (a) discover which real IBM Quantum backends are usable and
(b) validate a proposed experiment against a device *before* submission.

Both endpoints degrade gracefully when IBM credentials are absent or the
service is unreachable: they return HTTP 200 with an ``available: false``
payload instead of a 500, so the UI can show a calm "no hardware" state.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter

from qforge.core.state_preparation.state_factory import prepare_state
from qforge.engine.execution.hardware_validation import (
    extract_backend_capabilities,
    validate_circuit_for_backend,
)
from qforge.engine.models import ExperimentConfig

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Backend discovery ────────────────────────────────────────────────


@router.get("/backends")
def list_backends() -> dict[str, Any]:
    """List operational, non-simulator IBM Quantum backends with capabilities.

    Returns ``{"available": false, "reason": ..., "backends": []}`` when
    credentials are not configured or the service is unreachable.
    """
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService
    except Exception as exc:  # pragma: no cover - import guard
        return {
            "available": False,
            "reason": f"qiskit-ibm-runtime is not installed: {exc}",
            "backends": [],
        }

    try:
        service = QiskitRuntimeService()
    except Exception as exc:
        return {
            "available": False,
            "reason": f"IBM Quantum credentials not configured: {exc}",
            "backends": [],
        }

    try:
        backends = service.backends(operational=True, simulator=False)
    except Exception as exc:
        return {
            "available": False,
            "reason": f"Could not list backends: {exc}",
            "backends": [],
        }

    capabilities = [extract_backend_capabilities(b) for b in backends]
    return {"available": True, "backends": capabilities}


# ── Feasibility validation ───────────────────────────────────────────


@router.post("/validate")
def validate_config(config: ExperimentConfig) -> dict[str, Any]:
    """Validate an experiment config against a real backend before submission.

    Builds the circuit via the same state-prep path as ``run()``, resolves
    the requested (or least-busy) backend, and returns a
    ``HardwareFeasibility`` as JSON. Degrades to ``available: false`` when
    credentials/service are missing.
    """
    # Build the circuit exactly like the engine run() path does.
    circuit = prepare_state(config.state_type, config.num_qubits)
    circuit.measure_all()

    try:
        from qforge.engine.execution.hardware import resolve_backend
    except Exception as exc:  # pragma: no cover - import guard
        return {
            "available": False,
            "reason": f"Hardware execution unavailable: {exc}",
        }

    try:
        backend = resolve_backend(
            backend_name=config.backend_name,
            min_qubits=config.num_qubits,
        )
    except Exception as exc:
        return {
            "available": False,
            "reason": str(exc),
        }

    feasibility = validate_circuit_for_backend(circuit, backend, config.shots)
    return {
        "available": True,
        "feasible": feasibility.feasible,
        "violations": feasibility.violations,
        "warnings": feasibility.warnings,
        "backend_name": feasibility.backend_name,
        "capabilities": feasibility.capabilities,
    }
