from __future__ import annotations

import os
from typing import Any, Dict

from src.utils.schema import validate_manifest_schema
from src.experiments import get_experiment_manager


def _engine_use_flag() -> bool:
    return os.environ.get("QEXP_USE_ENGINE_API", "0").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def run_from_manifest(manifest_path: str) -> None:
    import json as _json

    if manifest_path.endswith((".yaml", ".yml")):
        import yaml  # type: ignore

        with open(manifest_path, "r") as f:
            data = yaml.safe_load(f)
    else:
        with open(manifest_path, "r") as f:
            data = _json.load(f)

    validate_manifest_schema(data)

    # Handle either base_preset or base_config
    base_preset = data.get("base_preset")
    base_config = data.get("base_config")
    parameter_ranges = dict(data["parameter_ranges"])  # shallow copy
    runs_per_config = int(data.get("runs_per_config", 1))
    rng_seed = data.get("rng_seed")

    if _engine_use_flag():
        try:
            from src.engine.api import sweep as engine_sweep
            from src.engine.context import AppContext
            from src.config.settings import settings

            # Get base configuration from either preset or direct config
            if base_preset:
                em = get_experiment_manager()
                exp = em.get_experiment(base_preset)
                if not exp:
                    raise ValueError(f"Base preset '{base_preset}' not found")
                base_cfg = dict(exp.get("config", {}))
            elif base_config:
                base_cfg = dict(base_config)
            else:
                raise ValueError("Must have either base_preset or base_config")
            
            # Apply overrides if present
            override_params = data.get("override", {})
            if override_params:
                base_cfg.update(override_params)
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
            base_cfg = {k: v for k, v in base_cfg.items() if k in allowed}
            if isinstance(base_cfg.get("noise_type"), str):
                base_cfg["noise_type"] = base_cfg["noise_type"].lower()
            if isinstance(base_cfg.get("sim_mode"), str):
                base_cfg["sim_mode"] = base_cfg["sim_mode"].lower()
            if isinstance(base_cfg.get("state_type"), str):
                base_cfg["state_type"] = base_cfg["state_type"].upper()
            if rng_seed is not None:
                base_cfg["rng_seed"] = int(rng_seed)

            norm_ranges: Dict[str, Any] = {}
            for k, vals in parameter_ranges.items():
                if k == "noise_type":
                    norm_ranges[k] = [str(v).lower() for v in vals]
                elif k == "state_type":
                    norm_ranges[k] = [str(v).upper() for v in vals]
                elif k == "sim_mode":
                    norm_ranges[k] = [str(v).lower() for v in vals]
                else:
                    norm_ranges[k] = vals

            ctx = AppContext(
                base_results_dir=getattr(settings, "DEFAULT_RESULTS_DIR", "results")
            )
            total_results = []
            for i in range(max(1, runs_per_config)):
                cfg_for_iter = dict(base_cfg)
                if cfg_for_iter.get("rng_seed") is not None:
                    cfg_for_iter["rng_seed"] = int(cfg_for_iter["rng_seed"]) + i
                manifest_payload = {
                    "base_config": cfg_for_iter,
                    "parameter_ranges": norm_ranges,
                    "runs_per_config": 1,
                }
                iter_results = engine_sweep(manifest_payload, ctx)
                total_results.extend(iter_results)
            return
        except Exception:
            pass

    # Legacy fallback
    from src.core.parameter_sweep import ParameterSweepEngine

    if base_preset:
        # Use preset-based sweep for legacy path
        engine = ParameterSweepEngine()
        engine.run_parameter_sweep(
            base_experiment_id=base_preset,
            parameter_ranges=parameter_ranges,
            runs_per_config=runs_per_config,
            sweep_name=f"{base_preset}_manifest",
        )
    else:
        # Direct config not supported in legacy path - create temporary preset
        raise NotImplementedError(
            "Direct base_config requires engine API (set QEXP_USE_ENGINE_API=1)"
        )
