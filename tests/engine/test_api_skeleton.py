from importlib import import_module
import pytest

def test_engine_api_skeleton_imports():
    api = import_module('src.engine.api')
    assert hasattr(api, 'run') and hasattr(api, 'sweep')
    with pytest.raises(NotImplementedError):
        api.run({})
