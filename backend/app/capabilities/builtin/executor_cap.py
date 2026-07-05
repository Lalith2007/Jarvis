from app.capabilities.core.base import BaseCapability
from app.capabilities.core.models import (
    CapabilityManifest, CapabilityCategory, CapabilityConfig,
    CapabilityContext, CapabilityDiagnostics, CapabilityResult
)
from app.executor.service import executor
from app.execution.manager import execution_manager


class ExecutorCapability(BaseCapability):
    def __init__(self):
        manifest = CapabilityManifest(
            id="executor.execute",
            name="Mission Executor",
            version="1.0.0",
            author="System",
            description="Executes tools and logic.",
            category=CapabilityCategory.TOOL,
            permissions=["execute:tools"],
        )
        config = CapabilityConfig()
        super().__init__(manifest, config)

    def initialize(self, context: CapabilityContext) -> None:
        pass

    def validate(self, context: CapabilityContext) -> None:
        pass

    def execute(self, context: CapabilityContext, diagnostics: CapabilityDiagnostics) -> CapabilityResult:
        plan = context.runtime_state.get("planner.plan")
        execution_id = context.execution_id
        
        execution = execution_manager.get(execution_id) if execution_id else None
        
        if execution and plan:
            result = executor.execute(plan, execution)
            return CapabilityResult(
                success=True,
                status="completed",
                result=result
            )
            
        return CapabilityResult(success=False, status="failed", errors=["Missing plan or execution"])

    def cleanup(self, context: CapabilityContext) -> None:
        pass

    def health_check(self) -> str:
        return "healthy"

    def estimate_cost(self, context: CapabilityContext) -> float:
        return 0.05

    def estimate_latency(self, context: CapabilityContext) -> float:
        return 2000.0
