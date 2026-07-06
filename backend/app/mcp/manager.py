import logging
from typing import Dict, List

from app.mcp.client import MCPClient
from app.mcp.registry import mcp_registry
from app.mcp.models import MCPServerConfig, MCPServerMetadata
from app.mcp.transport import MCPTransport, StdioMCPTransport

logger = logging.getLogger(__name__)


class MCPManager:
    """
    Manages MCP server connections and turns every discovered MCP tool into a
    registered BaseCapability (via MCPToolCapability) so Athena/CapabilityManager
    can use them exactly like built-in capabilities. Supports hot load/unload.
    """

    def __init__(self):
        self._clients: Dict[str, MCPClient] = {}
        # server name -> registered capability ids (for hot unload)
        self._tool_caps: Dict[str, List[str]] = {}

    # ── Legacy lightweight registration (kept for backward compatibility) ────
    def register_server(self, name: str, endpoint: str, capabilities: list[str]) -> None:
        mcp_registry.register(
            MCPServerMetadata(name=name, version="1.0.0", capabilities=capabilities)
        )
        client = MCPClient(name, endpoint)
        self._clients[name] = client
        client.connect()
        self._discover_and_register_tools(name, client, permissions=None)
        self._publish("MCPConnected", {"name": name, "endpoint": endpoint, "capabilities": capabilities})

    # ── Full connect path (stdio/http/injected transport) ───────────────────
    def connect(self, config: MCPServerConfig, transport: MCPTransport | None = None) -> List[str]:
        """
        Connect to an MCP server and register its tools as capabilities.
        Returns the list of registered capability ids. Hot-loadable.
        """
        if transport is None and config.transport == "stdio" and config.command:
            transport = StdioMCPTransport(config.command, config.args)

        client = MCPClient(config.name, config.endpoint or config.name, transport=transport)
        if not client.connect():
            self._publish("MCPConnectionFailed", {"name": config.name})
            return []
        client.initialize()
        self._clients[config.name] = client

        tools = client.list_tools()
        mcp_registry.register(
            MCPServerMetadata(
                name=config.name,
                version="1.0.0",
                capabilities=config.permissions,
                tools=[t.name for t in tools],
            )
        )
        cap_ids = self._register_tool_capabilities(config.name, client, tools, config.permissions)
        self._publish("MCPConnected", {"name": config.name, "tools": [t.name for t in tools]})
        return cap_ids

    # ── Discovery + capability registration ─────────────────────────────────
    def _discover_and_register_tools(self, name: str, client: MCPClient, permissions):
        try:
            tools = client.list_tools()
        except Exception as exc:
            logger.warning("MCP tool discovery failed for %s: %s", name, exc)
            tools = []
        if tools:
            self._register_tool_capabilities(name, client, tools, permissions)

    def _register_tool_capabilities(self, name, client, tools, permissions) -> List[str]:
        from app.capabilities.registry import capability_registry
        from app.mcp.capability import MCPToolCapability

        registered: List[str] = []
        for tool in tools:
            cap = MCPToolCapability(client, tool, permissions=permissions)
            capability_registry.register(cap)
            registered.append(cap.id)
            self._publish("MCPToolRegistered", {"server": name, "tool": tool.name, "capability": cap.id})
        self._tool_caps[name] = registered
        return registered

    def get_client(self, name: str) -> MCPClient | None:
        return self._clients.get(name)

    def remove_server(self, name: str) -> None:
        # Hot-unload: unregister this server's tool capabilities first.
        from app.capabilities.registry import capability_registry

        for cap_id in self._tool_caps.pop(name, []):
            try:
                capability_registry.unregister(cap_id)
            except Exception:
                pass
        mcp_registry.unregister(name)
        client = self._clients.pop(name, None)
        if client:
            client.disconnect()
            self._publish("MCPDisconnected", {"name": name})

    def health(self) -> Dict[str, bool]:
        out: Dict[str, bool] = {}
        for name, client in self._clients.items():
            try:
                out[name] = client.health()
            except Exception:
                out[name] = False
        return out

    @staticmethod
    def _publish(event_type: str, payload: dict) -> None:
        from app.platform.publisher import EventPublisher

        EventPublisher.publish(subsystem="mcp", event_type=event_type, payload=payload)


mcp_manager = MCPManager()
