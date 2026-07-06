"""
Computer Control capabilities — Sprint 13.5 (Objective 3).

Native OS operations exposed as permission-gated BaseCapabilities that run
through the standard pipeline (events/metrics/health apply). Filesystem access
reuses the hardened resolve-then-validate permission gate from Sprint 12.9;
terminal runs without a shell (arg list) under a timeout.

Implemented + tested here: filesystem, terminal, process, clipboard.
GUI automation (keyboard/mouse/window/app-launch) is scaffolded separately and
requires OS accessibility permissions + pyautogui — see ADR-013.
"""

import shlex
import subprocess

from app.capabilities.core.base import BaseCapability
from app.capabilities.core.models import (
    CapabilityCategory,
    CapabilityConfig,
    CapabilityContext,
    CapabilityDiagnostics,
    CapabilityManifest,
    CapabilityResult,
)
from app.tools import tool_registry
from app.tools.models import ToolCall


class _Base(BaseCapability):
    def initialize(self, context: CapabilityContext) -> None: ...
    def validate(self, context: CapabilityContext) -> None: ...
    def cleanup(self, context: CapabilityContext) -> None: ...
    def health_check(self) -> str: return "healthy"
    def estimate_cost(self, context: CapabilityContext) -> float: return 0.0
    def estimate_latency(self, context: CapabilityContext) -> float: return 50.0


class ComputerFilesystemCapability(_Base):
    """Filesystem read/write/list/search via the permission-gated tool registry."""

    _ACTION_TOOL = {
        "read": "read_file",
        "write": "write_file",
        "list": "list_directory",
        "search": "search_files",
    }

    def __init__(self):
        super().__init__(
            CapabilityManifest(
                id="computer.filesystem", name="Filesystem", version="1.0.0", author="System",
                description="Read, write, list, and search files (sandbox-gated).",
                category=CapabilityCategory.FILESYSTEM, permissions=["fs:read", "fs:write"],
                parameters={"action": {"type": "string"}, "path": {"type": "string"},
                            "content": {"type": "string"}, "pattern": {"type": "string"}},
            ),
            CapabilityConfig(),
        )

    def execute(self, context, diagnostics):
        rs = context.runtime_state or {}
        action = (rs.get("action") or "read").lower()
        tool = self._ACTION_TOOL.get(action)
        if not tool:
            return CapabilityResult(success=False, status="failed", errors=[f"unknown action {action}"])
        args = {"path": rs.get("path")}
        if action == "write":
            args["content"] = rs.get("content", "")
        if action == "search":
            args["pattern"] = rs.get("pattern", "")
        result = tool_registry.execute(ToolCall(name=tool, arguments=args))
        return CapabilityResult(
            success=result.success,
            status="completed" if result.success else "failed",
            result={"action": action, "output": result.output},
            errors=[] if result.success else [result.output],
        )


class ComputerTerminalCapability(_Base):
    """Run a shell command WITHOUT a shell (arg list), bounded by a timeout."""

    def __init__(self):
        super().__init__(
            CapabilityManifest(
                id="computer.terminal", name="Terminal", version="1.0.0", author="System",
                description="Execute a command with no shell interpolation, under a timeout.",
                category=CapabilityCategory.SYSTEM, permissions=["terminal:execute"],
                parameters={"command": {"type": "string"}, "timeout": {"type": "number"}},
            ),
            CapabilityConfig(),
        )

    def validate(self, context):
        if not (context.runtime_state or {}).get("command"):
            raise ValueError("computer.terminal requires a 'command'")

    def execute(self, context, diagnostics):
        rs = context.runtime_state or {}
        command = rs.get("command")
        timeout = float(rs.get("timeout", 15))
        argv = command if isinstance(command, list) else shlex.split(command)
        try:
            proc = subprocess.run(
                argv, capture_output=True, text=True, timeout=timeout, shell=False
            )
            return CapabilityResult(
                success=proc.returncode == 0,
                status="completed",
                result={
                    "returncode": proc.returncode,
                    "stdout": proc.stdout[:8000],
                    "stderr": proc.stderr[:4000],
                },
            )
        except subprocess.TimeoutExpired:
            return CapabilityResult(success=False, status="failed", errors=[f"timeout after {timeout}s"])
        except Exception as e:
            return CapabilityResult(success=False, status="failed", errors=[str(e)])


class ComputerProcessCapability(_Base):
    """List running processes (read-only)."""

    def __init__(self):
        super().__init__(
            CapabilityManifest(
                id="computer.process", name="Processes", version="1.0.0", author="System",
                description="List running processes (read-only).",
                category=CapabilityCategory.SYSTEM, permissions=["process:read"],
                parameters={"limit": {"type": "integer"}},
            ),
            CapabilityConfig(),
        )

    def execute(self, context, diagnostics):
        limit = int((context.runtime_state or {}).get("limit", 20))
        try:
            import psutil
            procs = []
            for p in psutil.process_iter(["pid", "name", "cpu_percent"]):
                procs.append(p.info)
            procs = sorted(procs, key=lambda x: x.get("cpu_percent") or 0, reverse=True)[:limit]
            return CapabilityResult(success=True, status="completed", result={"processes": procs, "count": len(procs)})
        except Exception as e:
            return CapabilityResult(success=False, status="failed", errors=[str(e)])


class ComputerClipboardCapability(_Base):
    """Get/set the macOS clipboard via pbpaste/pbcopy."""

    def __init__(self):
        super().__init__(
            CapabilityManifest(
                id="computer.clipboard", name="Clipboard", version="1.0.0", author="System",
                description="Read or write the system clipboard (macOS).",
                category=CapabilityCategory.SYSTEM, permissions=["clipboard:read", "clipboard:write"],
                parameters={"action": {"type": "string"}, "text": {"type": "string"}},
            ),
            CapabilityConfig(),
        )

    def execute(self, context, diagnostics):
        rs = context.runtime_state or {}
        action = (rs.get("action") or "get").lower()
        try:
            if action == "set":
                subprocess.run(["pbcopy"], input=rs.get("text", ""), text=True, timeout=5, check=True)
                return CapabilityResult(success=True, status="completed", result={"action": "set"})
            out = subprocess.run(["pbpaste"], capture_output=True, text=True, timeout=5).stdout
            return CapabilityResult(success=True, status="completed", result={"action": "get", "text": out})
        except Exception as e:
            return CapabilityResult(success=False, status="failed", errors=[str(e)])
