"""
Social connector framework (Sprint 13.10).

One `SocialConnector` interface; per-platform connectors register into
`social_registry`. The social capability dispatches to the connector for the
requested platform. Connectors are injectable so the framework is hermetically
testable without real API tokens.
"""
from abc import ABC, abstractmethod
from typing import Dict

SUPPORTED_PLATFORMS = [
    "instagram", "linkedin", "twitter", "github", "discord",
    "slack", "telegram", "whatsapp", "email",
]


class SocialConnector(ABC):
    platform: str = ""

    @abstractmethod
    def post(self, content: str, **kwargs) -> dict: ...

    def reply(self, target: str, content: str, **kwargs) -> dict:
        return self.post(content, reply_to=target, **kwargs)

    def schedule(self, content: str, when: str, **kwargs) -> dict:
        return {"scheduled": True, "when": when, "platform": self.platform}

    def available(self) -> bool:
        return True


class SocialRegistry:
    def __init__(self):
        self._connectors: Dict[str, SocialConnector] = {}

    def register(self, connector: SocialConnector) -> None:
        self._connectors[connector.platform] = connector

    def get(self, platform: str) -> SocialConnector | None:
        return self._connectors.get(platform)

    def platforms(self) -> list[str]:
        return sorted(self._connectors.keys())


social_registry = SocialRegistry()
