import sys
import threading
import time
from pathlib import Path
from app.mcp.protocol import mcp_protocol
from app.mcp.models import MCPRequest, MCPConnectionStatus
from app.mcp.transport import StdioMCPTransport

def test_mcp_serialization():
    req = MCPRequest(method="execute", params={"arg": 1}, id="req-1")
    serialized = mcp_protocol.serialize_request(req)
    assert '"execute"' in serialized
    assert '"jsonrpc"' in serialized
    
    resp = mcp_protocol.parse_response('{"jsonrpc": "2.0", "id": "req-1", "result": "success"}')
    assert resp.result == "success"

def test_mcp_transport_integration():
    """Test full integration with a mock FastMCP server (background thread + notifications)."""
    mock_server_path = Path(__file__).parent / "mock_server.py"
    transport = StdioMCPTransport(sys.executable, [str(mock_server_path)])
    
    notifications = []
    def on_notif(n):
        notifications.append(n)
        
    transport.on_notification = on_notif
    
    connected = transport.connect()
    assert connected
    assert transport.status == MCPConnectionStatus.CONNECTING
    
    # Send initialize handshake
    init_req = MCPRequest(
        method="initialize",
        params={"protocolVersion": "2024-11-05"},
        id="init-1"
    )
    
    resp_str = transport.send(mcp_protocol.serialize_request(init_req), message_id="init-1")
    resp = mcp_protocol.parse_response(resp_str)
    assert resp.result is not None
    assert resp.result.get("protocolVersion") == "2024-11-05"
    
    # Send initialized notification
    notif = MCPRequest(method="notifications/initialized")
    transport.send(mcp_protocol.serialize_request(notif), wait_for_response=False)
    
    # Wait for the async notification sent by the mock server
    time.sleep(0.3)
    assert len(notifications) > 0
    assert notifications[0].get("method") == "notifications/message"
    
    transport.disconnect()
    assert transport.status == MCPConnectionStatus.DISCONNECTED
