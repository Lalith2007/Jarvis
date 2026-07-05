from app.capabilities.core.base import BaseCapability
from app.capabilities.core.models import (
    CapabilityManifest, CapabilityCategory, CapabilityConfig,
    CapabilityContext, CapabilityDiagnostics, CapabilityResult
)
from app.capabilities.service import capability_service
from app.execution.manager import execution_manager
from app.mission.service import mission_service


class AnalyzerCapability(BaseCapability):
    def __init__(self):
        manifest = CapabilityManifest(
            id="mission.analyze",
            name="Mission Analyzer",
            version="1.0.0",
            author="System",
            description="Analyzes the mission.",
            category=CapabilityCategory.SYSTEM,
            permissions=["analyze"],
        )
        config = CapabilityConfig()
        super().__init__(manifest, config)

    def initialize(self, context: CapabilityContext) -> None:
        pass

    def validate(self, context: CapabilityContext) -> None:
        pass

    def execute(self, context: CapabilityContext, diagnostics: CapabilityDiagnostics) -> CapabilityResult:
        mission_id = context.mission_id
        execution_id = context.execution_id
        
        mission = mission_service.get(mission_id)
        execution = execution_manager.get(execution_id)
        
        if mission and execution:
            capability_service.evaluate_mission(mission, execution)
            
        return CapabilityResult(
            success=True,
            status="completed",
            result=None
        )

    def cleanup(self, context: CapabilityContext) -> None:
        pass

    def health_check(self) -> str:
        return "healthy"

    def estimate_cost(self, context: CapabilityContext) -> float:
        return 0.0

    def estimate_latency(self, context: CapabilityContext) -> float:
        return 10.0
