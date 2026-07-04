from app.runtime.registry import runtime_registry
def test_registry():
    assert runtime_registry is not None
