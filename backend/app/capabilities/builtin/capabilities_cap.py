from app.capabilities.core.base import BaseCapability
from app.capabilities.core.models import (
    CapabilityManifest,
    CapabilityCategory,
    CapabilityConfig,
    CapabilityContext,
    CapabilityDiagnostics,
    CapabilityResult,
)


class CapabilityRegistryCapability(BaseCapability):
    """
    Returns the full list of registered capabilities from the
    CapabilityRegistry as structured data.

    Consumed by runtime.generate to answer grounding queries such as
    "What tools do you have?" or "What capabilities exist?" without
    the LLM relying on prior knowledge.
    """

    def __init__(self):
        manifest = CapabilityManifest(
            id="registry.capabilities",
            name="Capability Registry Reader",
            version="1.0.0",
            author="System",
            description="Lists all registered capabilities inside JARVIS.",
            category=CapabilityCategory.TOOL,
            permissions=["read:capabilities"],
        )
        super().__init__(manifest, CapabilityConfig())

    def initialize(self, context: CapabilityContext) -> None:
        pass

    def validate(self, context: CapabilityContext) -> None:
        pass

    def execute(
        self, context: CapabilityContext, diagnostics: CapabilityDiagnostics
    ) -> CapabilityResult:
        # Deferred import to avoid circular dependency at module load time.
        from app.capabilities.registry import capability_registry  # noqa: PLC0415

        manifests = capability_registry.list()
        cap_list = [
            {
                "id": m.id,
                "name": m.name,
                "version": m.version,
                "description": m.description,
                "category": m.category.value,
                "permissions": m.permissions,
            }
            for m in manifests
        ]
        return CapabilityResult(
            success=True,
            status="completed",
            result={"capabilities": cap_list, "count": len(cap_list)},
        )

    def cleanup(self, context: CapabilityContext) -> None:
        pass

    def health_check(self) -> str:
        return "healthy"

    def estimate_cost(self, context: CapabilityContext) -> float:
        return 0.0

    def estimate_latency(self, context: CapabilityContext) -> float:
        return 1.0
