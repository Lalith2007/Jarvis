from app.capabilities.core.base import BaseCapability
from app.capabilities.core.models import (
    CapabilityManifest, CapabilityCategory, CapabilityConfig,
    CapabilityContext, CapabilityDiagnostics, CapabilityResult
)
from app.planner.service import planner


class PlannerCapability(BaseCapability):
    def __init__(self):
        manifest = CapabilityManifest(
            id="planner.plan",
            name="Mission Planner",
            version="1.0.0",
            author="System",
            description="Generates execution plans from goals.",
            category=CapabilityCategory.PLANNER,
            permissions=["plan:generate"],
        )
        config = CapabilityConfig()
        super().__init__(manifest, config)

    def initialize(self, context: CapabilityContext) -> None:
        pass

    def validate(self, context: CapabilityContext) -> None:
        pass

    def execute(self, context: CapabilityContext, diagnostics: CapabilityDiagnostics) -> CapabilityResult:
        goal = context.runtime_state.get("goal")
        if not goal:
            return CapabilityResult(success=False, status="failed", errors=["No goal found in runtime state"])

        plan = planner.plan(goal)
        
        return CapabilityResult(
            success=True,
            status="completed",
            result=plan
        )

    def cleanup(self, context: CapabilityContext) -> None:
        pass

    def health_check(self) -> str:
        return "healthy"

    def estimate_cost(self, context: CapabilityContext) -> float:
        return 0.01

    def estimate_latency(self, context: CapabilityContext) -> float:
        return 500.0
