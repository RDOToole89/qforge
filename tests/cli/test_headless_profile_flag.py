def test_apply_profile_from_args(monkeypatch, tmp_path):
    # Prepare a temporary profile
    from src.config import profiles

    monkeypatch.setattr(profiles, "PROFILES_DIR", tmp_path)
    # Create simple profile
    prof = {
        "experiment_defaults": {"shots": 33},
        "logging": {"results_dir": str(tmp_path / "r")},
        "visualization": {
            "backend": "matplotlib",
            "save_base_dir": str(tmp_path / "v"),
        },
    }
    (tmp_path / "unit.json").write_text("{}")
    profiles.save_profile("unit", prof)

    # Now apply via main helper
    from main import apply_profile_from_args
    from src.config.settings import settings
    from src.visualization.save_manager import (
        get_save_manager,
        set_save_manager_base_dir,
    )

    # Snapshot and ensure cleanup
    prev_base = get_save_manager().base_dir
    try:
        args = ["run", "--preset", "ghz_basic", "--profile", "unit"]
        new_args = apply_profile_from_args(args)

        # Flag and name removed
        assert "--profile" not in new_args and "unit" not in new_args
        # Settings applied
        assert settings.DEFAULT_SHOTS == 33
    finally:
        # Restore save manager base dir
        set_save_manager_base_dir(str(prev_base))
