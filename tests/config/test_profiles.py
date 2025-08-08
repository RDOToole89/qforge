import json
from pathlib import Path


def test_save_and_list_and_load_profile(tmp_path, monkeypatch):
    # Redirect profiles dir to temp
    from src.config import profiles

    monkeypatch.setattr(profiles, "PROFILES_DIR", tmp_path)

    # Save a simple profile
    path = profiles.save_profile("unit_test_profile")
    assert Path(path).exists()

    # List
    names = profiles.list_profiles()
    assert "unit_test_profile" in names

    # Load and basic structure
    data = profiles.load_profile("unit_test_profile")
    assert "experiment_defaults" in data and "logging" in data


def test_apply_profile_updates_settings_and_viz(monkeypatch, tmp_path):
    # Arrange a fake profile dict
    from src.config.settings import settings

    prof = {
        "experiment_defaults": {
            "shots": 77,
            "error_rate": 0.07,
            "sim_mode": "qasm",
        },
        "logging": {"results_dir": str(tmp_path / "results_root")},
        "visualization": {
            "backend": "matplotlib",
            "save_base_dir": str(tmp_path / "viz_base"),
        },
    }

    from src.config import profiles
    from src.visualization.save_manager import (
        get_save_manager,
        set_save_manager_base_dir,
    )

    # Snapshot previous state
    prev_shots = settings.DEFAULT_SHOTS
    prev_err = settings.DEFAULT_ERROR_RATE
    prev_base = Path(get_save_manager().base_dir)
    try:
        profiles.apply_profile(prof)

        assert settings.DEFAULT_SHOTS == 77
        assert abs(settings.DEFAULT_ERROR_RATE - 0.07) < 1e-12
        # ensure save manager base dir can be set without error
        sm = get_save_manager()
        assert Path(sm.base_dir).as_posix() == Path(tmp_path / "viz_base").as_posix()
    finally:
        # Restore state
        settings.DEFAULT_SHOTS = prev_shots
        settings.DEFAULT_ERROR_RATE = prev_err
        set_save_manager_base_dir(prev_base.as_posix())
