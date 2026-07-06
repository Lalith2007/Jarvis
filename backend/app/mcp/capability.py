"""
MCP → Capability adapter (Sprint 13.2).

Wraps a single MCP tool as a first-class BaseCapability so it registers in the
CapabilityRegistry and executes through the exact same pipeline as built-in
capabilities (CapabilityManager → lifecycle → runtime), with the same events,
metrics, health, and permissions. No bypass, no duplicate execution path.

Capability id convention: ``mcp.<server>.<tool>``.
"""

from app.capabilities.core.base import BaseCapability
from app.capabilities.core.models import (
    CapabilityCategory,
    CapabilityConfig,
    CapabilityContext,
    CapabilityDiagnostics,
    CapabilityManifest,
    CapabilityResult,
)
from app.mcp.client import MCPClient
from app.mcp.models import MCPTool


class MCPToolCapability(BaseCapability):
    def __init__(self, client: MCPClient, tool: MCPTool, permissions: list[str] | None = None):
        self._client = client
        self._tool = tool
        manifest = CapabilityManifest(
            id=f"mcp.{tool.server}.{tool.name}",
            name=f"{tool.server}: {tool.name}",
            version="1.0.0",
            author=f"mcp:{tool.server}",
            description=tool.description or f"MCP tool '{tool.name}' from '{tool.server}'.",
            category=CapabilityCategory.CUSTOM,
            permissions=permissions or [f"mcp:{tool.server}"],
            parameters=tool.input_schema or {},
            tags=["mcp", tool.server],
        )
        super().__init__(manifest, CapabilityConfig())

    def initialize(self, context: CapabilityContext) -> None:
        pass

    def validate(self, context: CapabilityContext) -> None:
        pass

    def execute(
        self, context: CapabilityContext, diagnostics: CapabilityDiagnostics
    ) -> CapabilityResult:
        # Arguments come from the mission runtime_state under the tool name, or
        # fall back to an "arguments" dict, or the whole non-internal state.
        rs = context.runtime_state or {}
        args = rs.get(self._tool.name) or rs.get("arguments") or {}
        if not isinstance(args, dict):
            args = {"input": args}

        resp = self._client.call_tool(self._tool.name, args)
        if resp.error:
            return CapabilityResult(
                success=False,
                status="failed",
                errors=[str(resp.error)],
            )
        return CapabilityResult(
            success=True,
            status="completed",
            result={"tool": self._tool.name, "server": self._tool.server, "output": resp.result},
        )

    def cleanup(self, context: CapabilityContext) -> None:
        pass

    def health_check(self) -> str:
        try:
            return "healthy" if self._client.health() else "degraded"
        except Exception:
            return "failed"

    def estimate_cost(self, context: CapabilityContext) -> float:
        return 0.0

    def estimate_latency(self, context: CapabilityContext) -> float:
        return 500.0
