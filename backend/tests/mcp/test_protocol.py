from app.mcp.protocol import mcp_protocol
from app.mcp.models import MCPRequest

def test_mcp_serialization():
    req = MCPRequest(method="execute", params={"arg": 1}, id="req-1")
    serialized = mcp_protocol.serialize_request(req)
    assert '"execute"' in serialized
    
    resp = mcp_protocol.parse_response('{"id": "req-1", "result": "success"}')
    assert resp.result == "success"
