"""Sprint 13.11 — Athena dynamic tool planning over the capability registry."""
import json

from app.mission.capabilities import capability_manager  # noqa: F401 register builtins
from app.athena.engines.capability import CapabilityEngine
from app.athena.engines.intent import IntentEngine
from app.mcp.transport import MCPTransport
from app.mcp.manager import mcp_manager
from app.mcp.models import MCPServerConfig, MCPConnectionStatus

ie, ce = IntentEngine(), CapabilityEngine()


def _caps(q):
    intent, _ = ie.evaluate(q)
    return [r.capability for r in ce.evaluate(q, intent)[0]]


def test_dynamic_selects_action_capabilities():
    assert "computer.terminal" in _caps("run a terminal command")
    assert "computer.process" in _caps("list the running process list")
    # greetings / simple queries stay clean
    assert _caps("Hello") == ["runtime.generate"]


def test_dynamic_does_not_fire_for_grounding_queries():
    # grounding queries route via static groups, not dynamic selection
    assert "vault.search" in _caps("review my north star")
    caps = _caps("what tools do you have?")
    assert "registry.capabilities" in caps


class _FakeT(MCPTransport):
    def __init__(self): super().__init__("fake")
    def connect(self):
        self.status = MCPConnectionStatus.READY; return True
    def send(self, data: str, message_id: str | None = None, wait_for_response: bool = True, timeout: float = 10.0) -> str:
        req = json.loads(data); m, rid = req.get("method"), req.get("id")
        if m == "initialize":
            return json.dumps({"id": rid, "result": {"protocolVersion": "1.0"}})
        if m == "tools/list":
            return json.dumps({"id": rid, "result": {"tools": [
                {"name": "translate", "description": "Translate text"}]}})
        return json.dumps({"id": rid, "result": {}})


def test_mcp_tool_is_dynamically_selectable():
    import time
    # An MCP tool, once registered, becomes selectable by Athena like a builtin.
    mcp_manager.connect(MCPServerConfig(name="lingo", command="x"), transport=_FakeT())
    
    # Wait for background thread to register tools
    for _ in range(20):
        if len(mcp_manager._tool_caps.get("lingo", [])) > 0:
            break
        time.sleep(0.05)
        
    try:
        assert "mcp.lingo.translate" in _caps("please translate this paragraph")
    finally:
        mcp_manager.remove_server("lingo")
