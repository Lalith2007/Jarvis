from app.mcp.transport import MCPTransport
from app.mcp.protocol import mcp_protocol
from app.mcp.models import MCPRequest, MCPResponse, MCPConnectionStatus

class MCPClient:
    def __init__(self, name: str, endpoint: str):
        self.name = name
        self.transport = MCPTransport(endpoint)

    def connect(self) -> bool:
        return self.transport.connect()

    def disconnect(self) -> None:
        self.transport.disconnect()

    def get_status(self) -> MCPConnectionStatus:
        return self.transport.status

    def send_request(self, request: MCPRequest) -> MCPResponse:
        serialized = mcp_protocol.serialize_request(request)
        try:
            raw_response = self.transport.send(serialized)
            return mcp_protocol.parse_response(raw_response)
        except Exception as e:
            return MCPResponse(id=request.id, error={"message": str(e)})
