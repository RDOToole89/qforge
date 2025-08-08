# tests/cli/test_router_smoke.py

from __future__ import annotations

from rich.console import Console

from src.cli.router import Router
from src.utils.messages import MESSAGES


class FakeDisplay:
    def display_footer_hints(self, *_args, **_kwargs):
        return None

    def display_params_summary(self, *_args, **_kwargs):
        return None

    def display_info_message(self, *_args, **_kwargs):
        return None

    def display_success_message(self, *_args, **_kwargs):
        return None

    def display_error_message(self, *_args, **_kwargs):
        return None

    def display_experiment_results(self, *_args, **_kwargs):
        return None


class FakeInput:
    def __init__(self):
        self.calls = []

    def select_option(self, title, options, default_value, **_kwargs):
        # Immediately choose quit to exit the loop
        self.calls.append((title, "select_option"))
        return "q"

    def get_input(self, *args, **kwargs):
        # default yes where needed
        return "y"


def test_router_quit_immediately(monkeypatch):
    # Ensure messages are present for Router
    assert isinstance(MESSAGES, dict)
    console = Console(force_terminal=False, color_system=None)

    router = Router(console=console, input_handler=FakeInput(), display_manager=FakeDisplay())
    # Should not raise
    router.run()