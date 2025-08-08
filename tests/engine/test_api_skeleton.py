from importlib import import_module


def test_engine_api_skeleton_imports():
    api = import_module("src.engine.api")
    assert hasattr(api, "run") and hasattr(api, "sweep")
