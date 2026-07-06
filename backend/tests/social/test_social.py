"""Sprint 13.10 — social automation (hermetic, fake connector)."""
from app.mission.capabilities import capability_manager  # noqa: F401 register builtins
from app.capabilities.registry import capability_registry
from app.capabilities.executor import capability_lifecycle
from app.capabilities.core.models import CapabilityContext, CapabilityDiagnostics
from app.social.connector import SocialConnector, social_registry


class FakeSlack(SocialConnector):
    platform = "slack"
    def post(self, content, **kwargs):
        return {"id": "msg-1", "text": content}


def _run(state):
    cap = capability_registry.get("social.post")
    return capability_lifecycle.execute(cap, CapabilityContext(
        mission_id="m", graph_id="g", execution_id="e", node_id="n", runtime_state=state))


def test_registered():
    assert "social.post" in capability_registry.ids()


def test_post_via_connector():
    social_registry.register(FakeSlack())
    r = _run({"platform": "slack", "action": "post", "content": "hello team"})
    assert r.success
    assert r.result["result"]["text"] == "hello team"


def test_unsupported_platform():
    r = _run({"platform": "myspace", "content": "x"})
    assert not r.success


def test_missing_connector():
    r = _run({"platform": "telegram", "content": "x"})  # no connector registered
    assert not r.success
    assert "no connector" in r.errors[0]


def test_requires_content():
    r = _run({"platform": "slack"})
    assert not r.success
