from src.experiments.presets import load_preset_experiments


def test_presets_registry_sane():
    presets = load_preset_experiments()
    assert isinstance(presets, dict)
    assert len(presets) > 0
    # Spot-check a few required fields
    for key, cfg in list(presets.items())[:5]:
        assert "config" in cfg
        c = cfg["config"]
        assert "num_qubits" in c
        assert "state_type" in c
        assert "sim_mode" in c
