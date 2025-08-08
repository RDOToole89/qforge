def test_select_option_unique_hotkeys():
    from src.cli.common import InputHandler
    from rich.console import Console

    ih = InputHandler(Console(), {"invalid_input": "invalid {input}"})
    opts = [("a", "Alpha", "a"), ("b", "Beta", "a"), ("c", "Gamma", None)]
    # Invoke private helper to assign hotkeys
    assigned = ih._assign_unique_hotkeys(
        [(str(v), str(l), (h or "")) for v, l, h in opts]
    )
    hotkeys = [h for _v, _l, h in assigned]
    assert len(set([h for h in hotkeys if h])) == len([h for h in hotkeys if h])


def test_density_mode_disables_single_qubit_noise():
    from src.config.params import apply_defaults, validate_parameters

    args = apply_defaults(
        {
            "num_qubits": 3,
            "state_type": "GHZ",
            "shots": 1,
            "sim_mode": "density",
            "noise_enabled": True,
            "noise_type": "AMPLITUDE_DAMPING",
            "error_rate": 0.1,
        }
    )
    validated = validate_parameters(args)
    assert validated["noise_enabled"] is False
    assert validated["noise_type"] is None


def test_non_tty_auto_defaults_monkeypatch(monkeypatch):
    # Ensure get_input returns default when stdin is not a TTY
    from src.cli.common import InputHandler
    from rich.console import Console

    class FakeStdin:
        def isatty(self):
            return False

    import sys as _sys

    monkeypatch.setattr(_sys, "stdin", FakeStdin())

    ih = InputHandler(
        Console(), {"invalid_input": "invalid {input}", "any": "Prompt [{default}]"}
    )
    out = ih.get_input("any", "Default")
    assert out == "default"
