"""
Social Automation capability — Sprint 13.10 (Objective 7).

`social.post` dispatches drafting/posting/replying/scheduling to the registered
SocialConnector for the requested platform (Instagram, LinkedIn, Twitter/X,
GitHub, Discord, Slack, Telegram, WhatsApp, Email). Executes through the
MissionGraph pipeline; connectors are injected/registered with real API tokens
for live use.
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
from app.social.connector import SUPPORTED_PLATFORMS, social_registry


class SocialPostCapability(BaseCapability):
    def __init__(self):
        super().__init__(
            CapabilityManifest(
                id="social.post",
                name="Social Post",
                version="1.0.0",
                author="System",
                description="Draft/post/reply/schedule to a social platform via its connector.",
                category=CapabilityCategory.NETWORK,
                permissions=["social:post"],
                parameters={
                    "platform": {"type": "string", "description": "|".join(SUPPORTED_PLATFORMS)},
                    "action": {"type": "string", "description": "post|reply|schedule"},
                    "content": {"type": "string"},
                    "target": {"type": "string"},
                    "when": {"type": "string"},
                },
            ),
            CapabilityConfig(),
        )

    def initialize(self, context): ...
    def validate(self, context):
        rs = context.runtime_state or {}
        if not rs.get("platform"):
            raise ValueError("social.post requires 'platform'")
        if not rs.get("content"):
            raise ValueError("social.post requires 'content'")
    def cleanup(self, context): ...
    def health_check(self):
        return "healthy" if social_registry.platforms() else "degraded"
    def estimate_cost(self, context): return 0.0
    def estimate_latency(self, context): return 700.0

    def execute(self, context, diagnostics):
        rs = context.runtime_state or {}
        platform = (rs.get("platform") or "").lower()
        action = (rs.get("action") or "post").lower()
        content = rs.get("content", "")

        if platform not in SUPPORTED_PLATFORMS:
            return CapabilityResult(success=False, status="failed",
                                    errors=[f"unsupported platform '{platform}'"])
        connector = social_registry.get(platform)
        if connector is None:
            return CapabilityResult(
                success=False, status="failed",
                errors=[f"no connector configured for '{platform}' (needs API token/setup)"],
            )
        try:
            if action == "reply":
                out = connector.reply(rs.get("target", ""), content)
            elif action == "schedule":
                out = connector.schedule(content, rs.get("when", ""))
            else:
                out = connector.post(content, attachments=rs.get("attachments"))
            return CapabilityResult(success=True, status="completed",
                                    result={"platform": platform, "action": action, "result": out})
        except Exception as e:
            return CapabilityResult(success=False, status="failed", errors=[str(e)])
