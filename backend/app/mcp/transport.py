from app.mcp.models import MCPConnectionStatus

class MCPTransport:
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self.status = MCPConnectionStatus.DISCONNECTED

    def connect(self) -> bool:
        self.status = MCPConnectionStatus.CONNECTED
        return True

    def disconnect(self) -> None:
        self.status = MCPConnectionStatus.DISCONNECTED

    def send(self, data: str) -> str:
        if self.status != MCPConnectionStatus.CONNECTED:
            raise ConnectionError("Not connected")
        return '{"result": "success"}'
