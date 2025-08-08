from __future__ import annotations

import importlib


def test_typer_app_imports():
    mod = importlib.import_module("src.cli.entrypoints.cli")
    assert hasattr(mod, "app")
