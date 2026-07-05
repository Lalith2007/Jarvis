from app.capabilities.core.base import BaseCapability
from app.capabilities.core.models import (
    CapabilityManifest, CapabilityCategory, CapabilityConfig,
    CapabilityContext, CapabilityDiagnostics, CapabilityResult
)
from app.athena.router import athena
from app.llm.prompts.loader import prompt_loader
from app.agents.hermes.models import PromptContext
from app.execution.manager import execution_manager


class RouterCapability(BaseCapability):
    def __init__(self):
        manifest = CapabilityManifest(
            id="athena.route",
            name="Athena Router",
            version="1.0.0",
            author="System",
            description="Routes the mission.",
            category=CapabilityCategory.LLM,
            permissions=["route"],
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
        goal = context.runtime_state.get("goal")
        
        prompt_context = PromptContext(
            system_prompt=prompt_loader.load("system.md"),
            user_query=goal,
            metadata={
                "mission_id": mission_id,
                "stage": "routing",
            },
        )
        
        decision = athena.route(prompt_context)
        
        execution = execution_manager.get(execution_id) if execution_id else None
        if execution:
            execution.metadata["athena_primary"] = decision.primary.value
            execution.metadata["athena_reason"] = decision.reason
            
        return CapabilityResult(
            success=True,
            status="completed",
            result={
                "primary_model": decision.primary.value,
                "reason": decision.reason
            }
        )

    def cleanup(self, context: CapabilityContext) -> None:
        pass

    def health_check(self) -> str:
        return "healthy"

    def estimate_cost(self, context: CapabilityContext) -> float:
        return 0.0

    def estimate_latency(self, context: CapabilityContext) -> float:
        return 10.0
