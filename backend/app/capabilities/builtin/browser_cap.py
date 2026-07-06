"""
Web Intelligence capabilities — Sprint 13.6 (Objective 2).

Browser capabilities (navigate, interact, extract/scrape, capture) executed
through the standard pipeline via the pluggable BrowserDriver. Live use needs
`playwright install` for browser binaries; the driver is injectable for tests.
"""

from app.browser.driver import browser_manager
from app.capabilities.core.base import BaseCapability
from app.capabilities.core.models import (
    CapabilityCategory,
    CapabilityConfig,
    CapabilityContext,
    CapabilityDiagnostics,
    CapabilityManifest,
    CapabilityResult,
)


class _BrowserBase(BaseCapability):
    def initialize(self, context): ...
    def validate(self, context): ...
    def cleanup(self, context): ...
    def health_check(self):
        try:
            return "healthy" if browser_manager.driver().available() else "degraded"
        except Exception:
            return "degraded"
    def estimate_cost(self, context): return 0.0
    def estimate_latency(self, context): return 800.0

    def _sid(self, context):
        return (context.runtime_state or {}).get("session_id") or context.mission_id or "default"


class BrowserNavigateCapability(_BrowserBase):
    def __init__(self):
        super().__init__(CapabilityManifest(
            id="browser.navigate", name="Browser Navigate", version="1.0.0", author="System",
            description="Open a URL in a browser session (per-session cookie persistence).",
            category=CapabilityCategory.BROWSER, permissions=["browser:navigate"],
            parameters={"url": {"type": "string"}, "session_id": {"type": "string"}},
        ), CapabilityConfig())

    def validate(self, context):
        if not (context.runtime_state or {}).get("url"):
            raise ValueError("browser.navigate requires 'url'")

    def execute(self, context, diagnostics):
        rs = context.runtime_state or {}
        try:
            info = browser_manager.driver().navigate(self._sid(context), rs["url"])
            return CapabilityResult(success=True, status="completed", result=info)
        except Exception as e:
            return CapabilityResult(success=False, status="failed", errors=[str(e)])


class BrowserExtractCapability(_BrowserBase):
    def __init__(self):
        super().__init__(CapabilityManifest(
            id="browser.extract", name="Browser Extract", version="1.0.0", author="System",
            description="Extract text / scrape DOM content from the current page.",
            category=CapabilityCategory.BROWSER, permissions=["browser:read"],
            parameters={"selector": {"type": "string"}, "session_id": {"type": "string"}},
        ), CapabilityConfig())

    def execute(self, context, diagnostics):
        rs = context.runtime_state or {}
        try:
            text = browser_manager.driver().extract(self._sid(context), rs.get("selector"))
            return CapabilityResult(success=True, status="completed",
                                    result={"text": text[:20000], "chars": len(text)})
        except Exception as e:
            return CapabilityResult(success=False, status="failed", errors=[str(e)])


class BrowserInteractCapability(_BrowserBase):
    def __init__(self):
        super().__init__(CapabilityManifest(
            id="browser.interact", name="Browser Interact", version="1.0.0", author="System",
            description="Click an element or fill a form field.",
            category=CapabilityCategory.BROWSER, permissions=["browser:interact"],
            parameters={"action": {"type": "string"}, "selector": {"type": "string"},
                        "value": {"type": "string"}, "session_id": {"type": "string"}},
        ), CapabilityConfig())

    def validate(self, context):
        rs = context.runtime_state or {}
        if not rs.get("selector"):
            raise ValueError("browser.interact requires 'selector'")

    def execute(self, context, diagnostics):
        rs = context.runtime_state or {}
        action = (rs.get("action") or "click").lower()
        d, sid = browser_manager.driver(), self._sid(context)
        try:
            if action == "fill":
                d.fill(sid, rs["selector"], rs.get("value", ""))
            else:
                d.click(sid, rs["selector"])
            return CapabilityResult(success=True, status="completed", result={"action": action, "selector": rs["selector"]})
        except Exception as e:
            return CapabilityResult(success=False, status="failed", errors=[str(e)])


class BrowserCaptureCapability(_BrowserBase):
    def __init__(self):
        super().__init__(CapabilityManifest(
            id="browser.capture", name="Browser Capture", version="1.0.0", author="System",
            description="Capture a screenshot or generate a PDF of the current page.",
            category=CapabilityCategory.BROWSER, permissions=["browser:read"],
            parameters={"kind": {"type": "string"}, "path": {"type": "string"}, "session_id": {"type": "string"}},
        ), CapabilityConfig())

    def validate(self, context):
        if not (context.runtime_state or {}).get("path"):
            raise ValueError("browser.capture requires 'path'")

    def execute(self, context, diagnostics):
        rs = context.runtime_state or {}
        kind = (rs.get("kind") or "screenshot").lower()
        try:
            path = browser_manager.driver().capture(self._sid(context), kind, rs["path"])
            return CapabilityResult(success=True, status="completed", result={"kind": kind, "path": path})
        except Exception as e:
            return CapabilityResult(success=False, status="failed", errors=[str(e)])
