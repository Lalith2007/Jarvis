from typing import Dict
from app.mcp.models import MCPServerMetadata

class MCPRegistry:
    def __init__(self):
        self._servers: Dict[str, MCPServerMetadata] = {}

    def register(self, metadata: MCPServerMetadata) -> None:
        self._servers[metadata.name] = metadata

    def unregister(self, name: str) -> None:
        self._servers.pop(name, None)

    def get_server(self, name: str) -> MCPServerMetadata | None:
        return self._servers.get(name)

    def list_servers(self) -> list[MCPServerMetadata]:
        return list(self._servers.values())

mcp_registry = MCPRegistry()
