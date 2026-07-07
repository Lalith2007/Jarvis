"""
github.commit — local git commit capability (architecture "github.commit").

Stages and commits changes in a permission-allowed repository via git itself —
no token required (push, which needs credentials, is a separate future step).
Runs through the standard pipeline; path is permission-gated.
"""
import subprocess

from app.capabilities.core.base import BaseCapability
from app.capabilities.core.models import (
    CapabilityCategory, CapabilityConfig, CapabilityContext,
    CapabilityDiagnostics, CapabilityManifest, CapabilityResult,
)
from app.security.permissions import permissions


class GithubCommitCapability(BaseCapability):
    def __init__(self):
        super().__init__(CapabilityManifest(
            id="github.commit", name="Git Commit", version="1.0.0", author="System",
            description="Stage and commit changes in a repository (local git, no token).",
            category=CapabilityCategory.SYSTEM, permissions=["git:write"],
            parameters={"repo": {"type": "string"}, "message": {"type": "string"},
                        "paths": {"type": "array"}},
        ), CapabilityConfig())

    def initialize(self, context): ...
    def validate(self, context):
        rs = context.runtime_state or {}
        if not rs.get("repo"):
            raise ValueError("github.commit requires 'repo'")
        if not rs.get("message"):
            raise ValueError("github.commit requires 'message'")
    def cleanup(self, context): ...
    def health_check(self): return "healthy"
    def estimate_cost(self, context): return 0.0
    def estimate_latency(self, context): return 200.0

    def execute(self, context, diagnostics):
        rs = context.runtime_state or {}
        repo = permissions.resolve_if_allowed(rs["repo"])
        if repo is None:
            return CapabilityResult(success=False, status="failed", errors=["repo path not allowed"])
        paths = rs.get("paths") or ["-A"]
        try:
            subprocess.run(["git", "-C", str(repo), "add", *paths], capture_output=True, text=True, timeout=30, check=True)
            proc = subprocess.run(["git", "-C", str(repo), "commit", "-m", rs["message"]],
                                  capture_output=True, text=True, timeout=30)
            return CapabilityResult(success=proc.returncode == 0, status="completed",
                result={"stdout": proc.stdout[:2000], "stderr": proc.stderr[:1000], "returncode": proc.returncode})
        except Exception as e:
            return CapabilityResult(success=False, status="failed", errors=[str(e)])
