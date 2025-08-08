from __future__ import annotations

import os
from typing import Optional, Dict, Any

from src.experiments import get_experiment_manager
from src.cli.common import DisplayManager  # optional if we add status prints later


def _engine_use_flag() -> bool:
    return os.environ.get("QEXP_USE_ENGINE_API", "0").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def run_by_name(exp_name: str) -> None:
    em = get_experiment_manager()
    if _engine_use_flag():
        try:
            exp = em.get_experiment(exp_name)
            if not exp:
                raise ValueError(f"Experiment '{exp_name}' not found")
            cfg = dict(exp.get("config", {}))
            allowed = {
                "num_qubits",
                "state_type",
                "noise_type",
                "noise_enabled",
                "shots",
                "sim_mode",
                "error_rate",
                "rng_seed",
                "custom_params",
            }
            cfg = {k: v for k, v in cfg.items() if k in allowed}
            if isinstance(cfg.get("noise_type"), str):
                cfg["noise_type"] = cfg["noise_type"].lower()
            if isinstance(cfg.get("sim_mode"), str):
                cfg["sim_mode"] = cfg["sim_mode"].lower()
            if isinstance(cfg.get("state_type"), str):
                cfg["state_type"] = cfg["state_type"].upper()
            from src.engine.api import run as engine_run
            from src.engine.context import AppContext
            from src.config.settings import settings

            ctx = AppContext(
                base_results_dir=getattr(settings, "DEFAULT_RESULTS_DIR", "results")
            )
            engine_run(cfg, ctx)
            return
        except Exception:
            pass
    # Legacy fallback
    experiment_config = em.get_experiment(exp_name)
    if not experiment_config:
        raise ValueError(f"Experiment '{exp_name}' not found")
    em.run_experiment(exp_name)


def run_from_config(config_path: str) -> None:
    import json as _json

    if config_path.endswith((".yaml", ".yml")):
        import yaml  # type: ignore

        with open(config_path, "r") as f:
            data = yaml.safe_load(f)
    else:
        with open(config_path, "r") as f:
            data = _json.load(f)

    em = get_experiment_manager()
    preset = data.get("preset")
    params_override = {k: v for k, v in data.items() if k != "preset"}
    if preset:
        em.run_experiment(preset, custom_params=params_override)
    else:
        em.run_experiment("ghz_basic", custom_params=data)
