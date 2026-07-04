from app.mcp.registry import mcp_registry
def test_mcp_registry():
    mcp_registry.register("test")
    assert "test" in mcp_registry.servers
