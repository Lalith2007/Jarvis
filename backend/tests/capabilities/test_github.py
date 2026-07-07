import subprocess
from app.mission.capabilities import capability_manager  # noqa: F401
from app.capabilities.registry import capability_registry
from app.capabilities.executor import capability_lifecycle
from app.capabilities.core.models import CapabilityContext, CapabilityDiagnostics


def test_registered():
    assert "github.commit" in capability_registry.ids()


def test_local_commit(tmp_path):
    # tmp is a permission-allowed root; init a real repo and commit live.
    repo = tmp_path
    subprocess.run(["git", "init", str(repo)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "j@x.com"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "JARVIS"], check=True, capture_output=True)
    (repo / "note.txt").write_text("hello")
    cap = capability_registry.get("github.commit")
    r = capability_lifecycle.execute(cap, CapabilityContext(
        mission_id="m", graph_id="g", execution_id="e", node_id="n",
        runtime_state={"repo": str(repo), "message": "jarvis: add note"}))
    assert r.success, r.errors
    log = subprocess.run(["git", "-C", str(repo), "log", "--oneline"], capture_output=True, text=True).stdout
    assert "jarvis: add note" in log


def test_denied_repo():
    cap = capability_registry.get("github.commit")
    r = capability_lifecycle.execute(cap, CapabilityContext(
        mission_id="m", graph_id="g", execution_id="e", node_id="n",
        runtime_state={"repo": "/etc", "message": "x"}))
    assert not r.success
