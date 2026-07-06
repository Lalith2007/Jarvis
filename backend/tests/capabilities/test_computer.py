"""Sprint 13.5 — Computer Control capabilities (hermetic)."""
from pathlib import Path

from app.mission.capabilities import capability_manager  # noqa: F401 register builtins
from app.capabilities.registry import capability_registry
from app.capabilities.executor import capability_lifecycle
from app.capabilities.core.models import CapabilityContext, CapabilityDiagnostics


def _run(cap_id, state):
    cap = capability_registry.get(cap_id)
    return capability_lifecycle.execute(cap, CapabilityContext(
        mission_id="m", graph_id="g", execution_id="e", node_id="n", runtime_state=state))


def test_all_computer_caps_registered():
    for cid in ("computer.filesystem", "computer.terminal", "computer.process", "computer.clipboard"):
        assert cid in capability_registry.ids()


def test_filesystem_write_then_read(tmp_path):
    f = tmp_path / "note.txt"  # tmp is an allowed root (12.9 permission gate)
    w = _run("computer.filesystem", {"action": "write", "path": str(f), "content": "hello fs"})
    assert w.success
    r = _run("computer.filesystem", {"action": "read", "path": str(f)})
    assert r.success and r.result["output"] == "hello fs"


def test_filesystem_denies_traversal():
    r = _run("computer.filesystem", {"action": "read", "path": "/etc/passwd"})
    assert not r.success


def test_terminal_echo():
    r = _run("computer.terminal", {"command": "echo hello-jarvis"})
    assert r.success
    assert "hello-jarvis" in r.result["stdout"]


def test_terminal_timeout():
    r = _run("computer.terminal", {"command": ["sleep", "5"], "timeout": 0.5})
    assert not r.success


def test_process_list():
    r = _run("computer.process", {"limit": 5})
    assert r.success
    assert r.result["count"] >= 1


def test_clipboard_roundtrip():
    import shutil
    if not shutil.which("pbcopy"):
        return  # non-macOS; skip
    s = _run("computer.clipboard", {"action": "set", "text": "jarvis-clip"})
    assert s.success
    g = _run("computer.clipboard", {"action": "get"})
    assert g.success and "jarvis-clip" in g.result["text"]
