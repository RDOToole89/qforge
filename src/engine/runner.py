"""Engine runner facade.

Why this file?
- Stable import path for callers: `src.engine.runner.run_raw`
- Central place to validate/normalize config before hitting the simulator
- Easy mocking seam in tests
"""

from __future__ import annotations

import logging
from typing import Any

from .experiment_runner import run_raw as _engine_run_raw
from .models import ExperimentConfig

log = logging.getLogger(__name__)


def run_raw(config: dict[str, Any]) -> tuple[Any, Any]:
    """Validate config and delegate to the engine-native runner.

    Args:
        config: Experiment config dict (will be validated by Pydantic).

    Returns:
        (QuantumCircuit, qiskit result payload)
    """
    # Validate/normalize early so the simulator only sees good inputs
    cfg = ExperimentConfig(**config)
    log.debug(
        "engine.runner: executing run_raw with config=%s",
        cfg.model_dump(exclude_none=True),
    )
    return _engine_run_raw(cfg.model_dump(exclude_none=True))
