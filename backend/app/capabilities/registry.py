from app.capabilities.models import CapabilityType


class CapabilityRegistry:
    """
    Runtime registry that stores every capability.
    Capabilities must be discoverable and support future registration.
    """

    def __init__(self) -> None:
        self._capabilities: set[CapabilityType] = set()

    def register(
        self,
        capability: CapabilityType,
    ) -> None:
        """
        Register a new capability.
        """
        self._capabilities.add(capability)

    def is_available(
        self,
        capability: CapabilityType,
    ) -> bool:
        """
        Check if a capability is registered.
        """
        return capability in self._capabilities

    def get_all(self) -> list[CapabilityType]:
        """
        Get all registered capabilities.
        """
        return list(self._capabilities)


capability_registry = CapabilityRegistry()
