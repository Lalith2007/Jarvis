"""
MCP server auto-connect from config (Sprint 13.2 completion).

Reads a Claude-Desktop-style JSON config listing MCP servers and connects each
at startup, so their tools auto-register as capabilities. This is how Voice
(OmniVoice), Social (Slack/GitHub/etc.), and any future service are added — by
config, never bespoke code. No hardcoded paths: the config location comes from
the JARVIS_MCP_CONFIG env var (falls back to <repo>/mcp_servers.json if present).

Config format:
  {"mcpServers": {"omnivoice": {"command": "python", "args": ["-m","backend.mcp_shim"],
                                 "cwd": "...", "env": {...}}}}
"""
import json
import logging
import os
from pathlib import Path

from app.config.settings import BASE_DIR
from app.mcp.models import MCPServerConfig

logger = logging.getLogger(__name__)


def _config_path() -> Path | None:
    env = os.getenv("JARVIS_MCP_CONFIG")
    if env:
        return Path(env).expanduser()
    default = BASE_DIR / "mcp_servers.json"
    return default if default.exists() else None


def load_configs(path: Path | None = None) -> list[MCPServerConfig]:
    p = path or _config_path()
    if not p or not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("Failed to read MCP config %s: %s", p, exc)
        return []
    out: list[MCPServerConfig] = []
    for name, spec in (data.get("mcpServers") or {}).items():
        out.append(
            MCPServerConfig(
                name=name,
                transport=spec.get("transport", "stdio"),
                command=spec.get("command"),
                args=spec.get("args", []),
                cwd=spec.get("cwd"),
                env=spec.get("env", {}),
                endpoint=spec.get("endpoint"),
                auth_token=spec.get("auth_token"),
                headers=spec.get("headers", {}),
                permissions=spec.get("permissions", []),
            )
        )
    return out


def autoconnect(path: Path | None = None) -> dict[str, int]:
    """Connect every configured MCP server; returns {server: n_capabilities}."""
    from app.mcp.manager import mcp_manager

    results: dict[str, int] = {}
    for cfg in load_configs(path):
        try:
            cap_ids = mcp_manager.connect(cfg)
            results[cfg.name] = len(cap_ids)
            logger.info("MCP '%s' connected: %d tool capabilities", cfg.name, len(cap_ids))
        except Exception as exc:
            logger.warning("MCP '%s' connect failed: %s", cfg.name, exc)
            results[cfg.name] = 0
    return results
