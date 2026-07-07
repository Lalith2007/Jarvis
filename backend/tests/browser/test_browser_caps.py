"""Sprint 13.6 — Web Intelligence capabilities (hermetic, fake driver)."""
from pathlib import Path

from app.mission.capabilities import capability_manager  # noqa: F401 register builtins
from app.capabilities.registry import capability_registry
from app.capabilities.executor import capability_lifecycle
from app.capabilities.core.models import CapabilityContext, CapabilityDiagnostics
from app.browser.driver import BrowserDriver, browser_manager


class FakeBrowserDriver(BrowserDriver):
    def __init__(self):
        self.state = {}
        self.actions = []

    def navigate(self, session_id, url):
        self.state[session_id] = {"url": url, "title": f"Title of {url}"}
        return {"url": url, "title": f"Title of {url}"}

    def extract(self, session_id, selector=None):
        return f"content[{selector or 'body'}] of {self.state.get(session_id, {}).get('url')}"

    def click(self, session_id, selector):
        self.actions.append(("click", selector))

    def fill(self, session_id, selector, value):
        self.actions.append(("fill", selector, value))

    def capture(self, session_id, kind, path):
        Path(path).write_text(f"{kind} bytes")
        return path

    def cookies(self, session_id):
        return [{"name": "sid", "value": "abc"}]


def _run(cid, state):
    cap = capability_registry.get(cid)
    return capability_lifecycle.execute(cap, CapabilityContext(
        mission_id="m", graph_id="g", execution_id="e", node_id="n", runtime_state=state))


def setup_module(_):
    browser_manager.set_driver(FakeBrowserDriver())


def test_browser_caps_registered():
    for cid in ("browser.navigate", "browser.extract", "browser.interact", "browser.capture"):
        assert cid in capability_registry.ids()


def test_navigate_and_extract():
    n = _run("browser.navigate", {"url": "https://example.com", "session_id": "s1"})
    assert n.success and n.result["title"] == "Title of https://example.com"
    e = _run("browser.extract", {"selector": "h1", "session_id": "s1"})
    assert e.success and "example.com" in e.result["text"]


def test_interact_and_capture(tmp_path):
    i = _run("browser.interact", {"action": "fill", "selector": "#q", "value": "hi", "session_id": "s1"})
    assert i.success and i.result["action"] == "fill"
    shot = tmp_path / "shot.png"
    c = _run("browser.capture", {"kind": "screenshot", "path": str(shot), "session_id": "s1"})
    assert c.success and shot.exists()


def test_navigate_requires_url():
    r = _run("browser.navigate", {"session_id": "s1"})
    assert not r.success
