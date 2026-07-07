"""
python.execute — native code-execution capability (architecture "Python").

Runs Python source in a subprocess (no shell) under a timeout, returning
stdout/stderr/returncode. Permission-gated (python:execute) and executed through
the standard pipeline. For untrusted/autonomous use, a sandboxed provider should
back this; today it is timeout- and output-bounded.
"""
import subprocess
import sys

from app.capabilities.core.base import BaseCapability
from app.capabilities.core.models import (
    CapabilityCategory, CapabilityConfig, CapabilityContext,
    CapabilityDiagnostics, CapabilityManifest, CapabilityResult,
)


class PythonExecuteCapability(BaseCapability):
    def __init__(self):
        super().__init__(CapabilityManifest(
            id="python.execute", name="Python Execute", version="1.0.0", author="System",
            description="Execute Python source in a subprocess under a timeout.",
            category=CapabilityCategory.PYTHON, permissions=["python:execute"],
            parameters={"code": {"type": "string"}, "timeout": {"type": "number"}},
        ), CapabilityConfig())

    def initialize(self, context): ...
    def validate(self, context):
        if not (context.runtime_state or {}).get("code"):
            raise ValueError("python.execute requires 'code'")
    def cleanup(self, context): ...
    def health_check(self): return "healthy"
    def estimate_cost(self, context): return 0.0
    def estimate_latency(self, context): return 300.0

    def execute(self, context, diagnostics):
        rs = context.runtime_state or {}
        code = rs.get("code", "")
        timeout = float(rs.get("timeout", 15))
        try:
            proc = subprocess.run([sys.executable, "-I", "-c", code],
                                  capture_output=True, text=True, timeout=timeout, shell=False)
            return CapabilityResult(success=proc.returncode == 0, status="completed",
                result={"returncode": proc.returncode, "stdout": proc.stdout[:8000], "stderr": proc.stderr[:4000]})
        except subprocess.TimeoutExpired:
            return CapabilityResult(success=False, status="failed", errors=[f"timeout after {timeout}s"])
        except Exception as e:
            return CapabilityResult(success=False, status="failed", errors=[str(e)])
