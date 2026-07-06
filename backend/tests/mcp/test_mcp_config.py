"""Sprint 13.2 completion — config-driven MCP auto-connect."""
import json

from app.mission.capabilities import capability_manager  # noqa: F401 register builtins
from app.capabilities.registry import capability_registry
from app.mcp.config import load_configs
from app.mcp import manager as mgr


def test_load_configs(tmp_path):
    cfg = tmp_path / "mcp.json"
    cfg.write_text(json.dumps({"mcpServers": {
        "omnivoice": {"command": "python", "args": ["-m", "backend.mcp_shim"], "permissions": ["voice:speak"]},
        "remote": {"transport": "http", "endpoint": "http://x/mcp"},
    }}))
    configs = load_configs(cfg)
    names = {c.name for c in configs}
    assert names == {"omnivoice", "remote"}
    ov = next(c for c in configs if c.name == "omnivoice")
    assert ov.command == "python" and "voice:speak" in ov.permissions


def test_autoconnect_registers_tools(tmp_path, monkeypatch):
    # Fake the manager.connect so we test the loader->connect wiring without a
    # real MCP process, and assert capabilities would be registered.
    from app.mcp.config import autoconnect
    cfg = tmp_path / "mcp.json"
    cfg.write_text(json.dumps({"mcpServers": {"svc": {"command": "x"}}}))

    seen = {}
    def fake_connect(config, transport=None):
        seen["name"] = config.name
        return [f"mcp.{config.name}.tool1", f"mcp.{config.name}.tool2"]
    monkeypatch.setattr(mgr.mcp_manager, "connect", fake_connect)

    result = autoconnect(cfg)
    assert result == {"svc": 2}
    assert seen["name"] == "svc"


def test_no_config_is_noop(tmp_path):
    from app.mcp.config import autoconnect
    assert autoconnect(tmp_path / "does-not-exist.json") == {}
