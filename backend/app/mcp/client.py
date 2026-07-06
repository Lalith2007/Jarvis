from app.mcp.transport import MCPTransport
from app.mcp.protocol import mcp_protocol
from app.mcp.models import MCPRequest, MCPResponse, MCPConnectionStatus, MCPTool


class MCPClient:
    def __init__(self, name: str, endpoint: str, transport: MCPTransport | None = None):
        self.name = name
        # A concrete transport (stdio/http/fake) may be injected; otherwise the
        # inert base stub is used (legacy behaviour).
        self.transport = transport if transport is not None else MCPTransport(endpoint)

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

    # ── MCP protocol methods ────────────────────────────────────────────────

    def initialize(self) -> MCPResponse:
        return self.send_request(MCPRequest(method="initialize", id="init"))

    def list_tools(self) -> list[MCPTool]:
        """Discover the server's tools via tools/list. Returns [] on any error."""
        resp = self.send_request(MCPRequest(method="tools/list", id="tools-list"))
        if resp.error or not isinstance(resp.result, dict):
            return []
        tools = resp.result.get("tools")
        if not isinstance(tools, list):
            return []
        out: list[MCPTool] = []
        for t in tools:
            if not isinstance(t, dict) or "name" not in t:
                continue
            out.append(
                MCPTool(
                    name=t["name"],
                    description=t.get("description", ""),
                    input_schema=t.get("inputSchema") or t.get("input_schema") or {},
                    server=self.name,
                )
            )
        return out

    def call_tool(self, tool_name: str, arguments: dict) -> MCPResponse:
        """Invoke a tool via tools/call."""
        return self.send_request(
            MCPRequest(
                method="tools/call",
                params={"name": tool_name, "arguments": arguments or {}},
                id=f"call-{tool_name}",
            )
        )

    def health(self) -> bool:
        """Lightweight liveness check."""
        if self.get_status() != MCPConnectionStatus.CONNECTED:
            return False
        resp = self.send_request(MCPRequest(method="ping", id="ping"))
        return resp.error is None
