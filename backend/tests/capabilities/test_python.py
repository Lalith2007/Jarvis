from app.mission.capabilities import capability_manager  # noqa: F401
from app.capabilities.registry import capability_registry
from app.capabilities.executor import capability_lifecycle
from app.capabilities.core.models import CapabilityContext, CapabilityDiagnostics


def _run(state):
    cap = capability_registry.get("python.execute")
    return capability_lifecycle.execute(cap, CapabilityContext(
        mission_id="m", graph_id="g", execution_id="e", node_id="n", runtime_state=state))


def test_registered():
    assert "python.execute" in capability_registry.ids()


def test_executes_code():
    r = _run({"code": "print(6*7)"})
    assert r.success and r.result["stdout"].strip() == "42"


def test_nonzero_exit_captured():
    r = _run({"code": "import sys; sys.stderr.write('boom'); sys.exit(3)"})
    assert not r.success and r.result["returncode"] == 3 and "boom" in r.result["stderr"]


def test_timeout():
    r = _run({"code": "import time; time.sleep(5)", "timeout": 0.5})
    assert not r.success


def test_requires_code():
    r = _run({})
    assert not r.success
