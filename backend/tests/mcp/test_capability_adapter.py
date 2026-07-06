"""
Sprint 13.2 — MCP tool -> BaseCapability adapter (hermetic, fake transport).

Verifies discovered MCP tools become registered capabilities executable through
the same lifecycle as built-ins, and are hot-unloaded on server removal.
"""
import json

from app.mcp.transport import MCPTransport
from app.mcp.manager import mcp_manager
from app.mcp.models import MCPServerConfig, MCPConnectionStatus
from app.capabilities.registry import capability_registry
from app.capabilities.executor import capability_lifecycle
from app.capabilities.core.models import CapabilityContext, CapabilityDiagnostics


class FakeMCPTransport(MCPTransport):
    """In-process fake MCP server speaking JSON-RPC."""

    def __init__(self):
        super().__init__(endpoint="fake")

    def connect(self):
        self.status = MCPConnectionStatus.CONNECTED
        return True

    def send(self, data: str) -> str:
        req = json.loads(data)
        method, rid = req.get("method"), req.get("id")
        if method == "initialize":
            return json.dumps({"id": rid, "result": {"protocolVersion": "1.0"}})
        if method == "tools/list":
            return json.dumps({"id": rid, "result": {"tools": [
                {"name": "echo", "description": "Echo text", "inputSchema": {"text": {"type": "string"}}},
                {"name": "add", "description": "Add numbers", "inputSchema": {"a": {"type": "number"}, "b": {"type": "number"}}},
            ]}})
        if method == "tools/call":
            p = req.get("params", {})
            return json.dumps({"id": rid, "result": {"echoed": p.get("arguments"), "tool": p.get("name")}})
        if method == "ping":
            return json.dumps({"id": rid, "result": "pong"})
        return json.dumps({"id": rid, "error": {"message": f"unknown method {method}"}})


def _ctx(state):
    return CapabilityContext(
        mission_id="m", graph_id="g", execution_id="e", node_id="n", runtime_state=state
    )


def test_mcp_tools_register_as_capabilities_and_execute_and_unload():
    cfg = MCPServerConfig(name="fakemcp", transport="stdio", command="unused")
    cap_ids = mcp_manager.connect(cfg, transport=FakeMCPTransport())

    # Both tools became capabilities with the mcp.<server>.<tool> convention.
    assert set(cap_ids) == {"mcp.fakemcp.echo", "mcp.fakemcp.add"}
    for cid in cap_ids:
        assert cid in capability_registry.ids()

    # Execute one through the SAME lifecycle as built-ins.
    cap = capability_registry.get("mcp.fakemcp.echo")
    result = capability_lifecycle.execute(cap, _ctx({"echo": {"text": "hi"}}))
    assert result.success
    assert result.result["tool"] == "echo"
    assert result.result["output"]["echoed"] == {"text": "hi"}

    # Metrics were recorded for the MCP capability (observability applies).
    assert capability_registry.metrics()["mcp.fakemcp.echo"].execution_count >= 1

    # Health probe works.
    assert cap.health_check() == "healthy"

    # Hot unload: removing the server unregisters its capabilities.
    mcp_manager.remove_server("fakemcp")
    assert "mcp.fakemcp.echo" not in capability_registry.ids()
    assert "mcp.fakemcp.add" not in capability_registry.ids()


def test_legacy_register_server_still_works():
    mcp_manager.register_server("LegacyMCP", "http://localhost:9999", ["tool_usage"])
    client = mcp_manager.get_client("LegacyMCP")
    assert client is not None
    assert client.get_status() == "connected"
    mcp_manager.remove_server("LegacyMCP")
    assert mcp_manager.get_client("LegacyMCP") is None
