from app.mcp.manager import mcp_manager
from app.mcp.registry import mcp_registry

def test_mcp_registration_discovery():
    mcp_manager.register_server("TestMCP", "http://localhost:8000", ["tool_usage"])
    
    server = mcp_registry.get_server("TestMCP")
    assert server is not None
    assert "tool_usage" in server.capabilities
    
    client = mcp_manager.get_client("TestMCP")
    assert client is not None
    assert client.get_status() == "connected"
    
    mcp_manager.remove_server("TestMCP")
    assert mcp_registry.get_server("TestMCP") is None
