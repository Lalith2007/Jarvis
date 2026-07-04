from typing import Any, Callable, Dict
from pydantic import BaseModel
from app.capabilities.models import CapabilityType

class ProviderMetadata(BaseModel):
    name: str
    version: str
    description: str
    is_healthy: bool = True

class RuntimeProvider(BaseModel):
    capability: CapabilityType
    handler: Callable
    metadata: ProviderMetadata
    priority: int = 0

class RuntimeRegistry:
    def __init__(self):
        self._providers: Dict[CapabilityType, list[RuntimeProvider]] = {}

    def register(self, provider: RuntimeProvider) -> None:
        if provider.capability not in self._providers:
            self._providers[provider.capability] = []
        
        for p in self._providers[provider.capability]:
            if p.handler == provider.handler:
                return

        self._providers[provider.capability].append(provider)
        self._providers[provider.capability].sort(key=lambda p: p.priority, reverse=True)

    def unregister(self, capability: CapabilityType, handler_name: str) -> None:
        if capability in self._providers:
            self._providers[capability] = [
                p for p in self._providers[capability] 
                if p.handler.__name__ != handler_name
            ]

    def get_provider(self, capability: CapabilityType) -> RuntimeProvider | None:
        providers = self._providers.get(capability, [])
        for p in providers:
            if p.metadata.is_healthy:
                return p
        return None

runtime_registry = RuntimeRegistry()
