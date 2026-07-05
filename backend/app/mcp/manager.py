from typing import Dict
from app.mcp.client import MCPClient
from app.mcp.registry import mcp_registry
from app.mcp.models import MCPServerMetadata

class MCPManager:
    def __init__(self):
        self._clients: Dict[str, MCPClient] = {}

    def register_server(self, name: str, endpoint: str, capabilities: list[str]) -> None:
        metadata = MCPServerMetadata(name=name, version="1.0.0", capabilities=capabilities)
        mcp_registry.register(metadata)
        
        client = MCPClient(name, endpoint)
        self._clients[name] = client
        client.connect()
        
        from app.platform.publisher import EventPublisher
        EventPublisher.publish(
            subsystem="mcp",
            event_type="MCPConnected",
            payload={"name": name, "endpoint": endpoint, "capabilities": capabilities}
        )

    def get_client(self, name: str) -> MCPClient | None:
        return self._clients.get(name)

    def remove_server(self, name: str) -> None:
        mcp_registry.unregister(name)
        client = self._clients.pop(name, None)
        if client:
            client.disconnect()
            from app.platform.publisher import EventPublisher
            EventPublisher.publish(
                subsystem="mcp",
                event_type="MCPDisconnected",
                payload={"name": name}
            )

mcp_manager = MCPManager()
