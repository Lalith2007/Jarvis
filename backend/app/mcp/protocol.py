import json
from app.mcp.models import MCPRequest, MCPResponse

class MCPProtocol:
    def serialize_request(self, request: MCPRequest) -> str:
        return request.model_dump_json(exclude_none=True)

    def parse_response(self, data: str) -> MCPResponse:
        try:
            parsed = json.loads(data)
            return MCPResponse(**parsed)
        except Exception as e:
            return MCPResponse(error={"code": -32700, "message": "Parse error", "data": str(e)})

mcp_protocol = MCPProtocol()
