from app.capabilities.core.base import BaseCapability
from app.capabilities.core.models import (
    CapabilityManifest, CapabilityCategory, CapabilityConfig,
    CapabilityContext, CapabilityDiagnostics, CapabilityResult
)
from app.providers.registry import provider_registry

class RegistryCapability(BaseCapability):
    def __init__(self):
        manifest = CapabilityManifest(
            id="registry.models",
            name="Model Registry Reader",
            version="1.0.0",
            author="System",
            description="Lists all available AI models registered in JARVIS.",
            category=CapabilityCategory.TOOL,
            permissions=["read:models"],
        )
        config = CapabilityConfig()
        super().__init__(manifest, config)

    def initialize(self, context: CapabilityContext) -> None:
        pass

    def validate(self, context: CapabilityContext) -> None:
        pass

    def execute(self, context: CapabilityContext, diagnostics: CapabilityDiagnostics) -> CapabilityResult:
        models = provider_registry.all()
        model_list = [
            {
                "id": m.id,
                "display_name": m.display_name,
                "provider": m.provider.value,
                "context_window": m.context_window,
                "enabled": m.enabled,
                "healthy": m.healthy,
                "capabilities": [cap.value for cap in m.capabilities],
            }
            for m in models
        ]
        return CapabilityResult(
            success=True,
            status="completed",
            result={"models": model_list, "count": len(model_list)},
        )

    def cleanup(self, context: CapabilityContext) -> None:
        pass

    def health_check(self) -> str:
        return "healthy"

    def estimate_cost(self, context: CapabilityContext) -> float:
        return 0.0

    def estimate_latency(self, context: CapabilityContext) -> float:
        return 1.0
