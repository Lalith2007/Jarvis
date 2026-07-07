import logging
import threading
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
    can use them exactly like built-in capabilities. Supports hot load/unload
    and automatic reconnect.
    """

    def __init__(self):
        self._clients: Dict[str, MCPClient] = {}
        # server name -> registered capability ids (for hot unload)
        self._tool_caps: Dict[str, List[str]] = {}
        self._reconnect_threads: Dict[str, threading.Thread] = {}
        self._stop_events: Dict[str, threading.Event] = {}

    # ── Legacy lightweight registration (kept for backward compatibility) ────
    def register_server(self, name: str, endpoint: str, capabilities: list[str]) -> None:
        mcp_registry.register(
            MCPServerMetadata(name=name, version="1.0.0", capabilities=capabilities)
        )
        client = MCPClient(name, endpoint)
        self._clients[name] = client
        client.connect()
        # legacy paths do not do async tool discovery out of the box unless asked
        self._publish("MCPConnected", {"name": name, "endpoint": endpoint, "capabilities": capabilities})

    def connect(self, config: MCPServerConfig, transport: MCPTransport | None = None) -> List[str]:
        """
        Launches connection in a background thread. Non-blocking.
        Returns empty list immediately. Tools will be registered asynchronously.
        """
        if config.name in self._reconnect_threads:
            return []

        stop_event = threading.Event()
        self._stop_events[config.name] = stop_event
        t = threading.Thread(
            target=self._connection_loop, 
            args=(config, transport, stop_event), 
            daemon=True,
            name=f"mcp-conn-{config.name}"
        )
        self._reconnect_threads[config.name] = t
        t.start()
        return []

    def _connection_loop(self, config: MCPServerConfig, transport: MCPTransport | None, stop_event: threading.Event) -> None:
        import time
        from app.mcp.models import MCPConnectionStatus

        backoff = 1.0
        max_backoff = 30.0

        while not stop_event.is_set():
            t_port = transport
            if t_port is None and config.transport == "stdio" and config.command:
                t_port = StdioMCPTransport(config.command, config.args, config.env, config.cwd)

            if t_port is None:
                logger.error("No valid transport for MCP %s", config.name)
                break

            client = MCPClient(config.name, config.endpoint or config.name, transport=t_port)
            
            def on_notif(payload):
                self._publish("MCPNotification", {"name": config.name, "payload": payload})
            
            t_port.on_notification = on_notif

            if client.connect():
                resp = client.initialize()
                if resp.error:
                    logger.error("MCP %s initialize failed: %s", config.name, resp.error)
                    client.disconnect()
                else:
                    self._clients[config.name] = client
                    backoff = 1.0
                    
                    try:
                        t_port.status = MCPConnectionStatus.DISCOVERING_TOOLS
                        tools = client.list_tools()
                        mcp_registry.register(
                            MCPServerMetadata(
                                name=config.name,
                                version="1.0.0",
                                capabilities=config.permissions,
                                tools=[t.name for t in tools],
                            )
                        )
                        self._register_tool_capabilities(config.name, client, tools, config.permissions)
                        t_port.status = MCPConnectionStatus.READY
                        self._publish("MCPConnected", {"name": config.name, "tools": [t.name for t in tools]})
                        logger.info("MCP %s connected and READY.", config.name)
                        
                        while not stop_event.is_set() and client.get_status() == MCPConnectionStatus.READY:
                            time.sleep(1.0)
                            
                    except Exception as e:
                        logger.error("Error during MCP %s operation: %s", config.name, e)
                        
                    self._unregister_tool_capabilities(config.name)
                    client.disconnect()
                    if config.name in self._clients:
                        del self._clients[config.name]
            else:
                logger.warning("MCP %s connect failed.", config.name)

            if stop_event.is_set():
                break

            logger.info("MCP %s reconnecting in %.1fs...", config.name, backoff)
            time.sleep(backoff)
            backoff = min(backoff * 2, max_backoff)

    def _register_tool_capabilities(self, name, client, tools, permissions) -> List[str]:
        from app.capabilities.registry import capability_registry
        from app.mcp.capability import MCPToolCapability

        registered: List[str] = []
        for tool in tools:
            cap = MCPToolCapability(name, tool, permissions=permissions)
            capability_registry.register(cap)
            registered.append(cap.id)
            self._publish("MCPToolRegistered", {"server": name, "tool": tool.name, "capability": cap.id})
        self._tool_caps[name] = registered
        return registered

    def _unregister_tool_capabilities(self, name: str) -> None:
        from app.capabilities.registry import capability_registry
        for cap_id in self._tool_caps.pop(name, []):
            try:
                capability_registry.unregister(cap_id)
            except Exception:
                pass
        mcp_registry.unregister(name)

    def get_client(self, name: str) -> MCPClient | None:
        return self._clients.get(name)

    def remove_server(self, name: str) -> None:
        if name in self._stop_events:
            self._stop_events[name].set()
            del self._stop_events[name]
        
        self._unregister_tool_capabilities(name)
        
        client = self._clients.pop(name, None)
        if client:
            client.disconnect()
            self._publish("MCPDisconnected", {"name": name})
            
        if name in self._reconnect_threads:
            del self._reconnect_threads[name]

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
