from app.providers.models import ProviderCapability


class ProviderPolicy:
    """
    Converts high-level execution requirements
    into provider capabilities.

    Athena should eventually emit abstract
    requirements instead of concrete model names.
    """

    def coding(self) -> list[ProviderCapability]:
        return [
            ProviderCapability.CODING,
            ProviderCapability.TOOLS,
            ProviderCapability.CHAT,
        ]

    def planning(self) -> list[ProviderCapability]:
        return [
            ProviderCapability.REASONING,
            ProviderCapability.CHAT,
        ]

    def research(self) -> list[ProviderCapability]:
        return [
            ProviderCapability.REASONING,
            ProviderCapability.LONG_CONTEXT,
            ProviderCapability.CHAT,
        ]

    def conversation(self) -> list[ProviderCapability]:
        return [
            ProviderCapability.CHAT,
        ]

    def vision(self) -> list[ProviderCapability]:
        return [
            ProviderCapability.VISION,
            ProviderCapability.CHAT,
        ]


provider_policy = ProviderPolicy()
