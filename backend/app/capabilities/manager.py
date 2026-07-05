from typing import TYPE_CHECKING

from app.capabilities.analyzer import capability_analyzer
from app.capabilities.models import CapabilityDecision
from app.capabilities.registry import capability_registry

if TYPE_CHECKING:
    from app.execution.models import ExecutionContext
    from app.mission.models import Mission


class CapabilityManager:
    """
    Central decision engine of JARVIS.
    Determines WHICH capabilities are required to complete a mission.
    """

    def evaluate(
        self,
        mission: "Mission",
        execution: "ExecutionContext",
    ) -> CapabilityDecision:
        """
        Run analyzer, consult registry, return decision,
        and store it inside ExecutionContext.
        """
        from app.platform.publisher import EventPublisher

        EventPublisher.publish(
            subsystem="capabilities",
            event_type="CapabilityEvaluationStarted",
            mission_id=mission.id,
            execution_id=execution.mission_id
        )

        decision = capability_analyzer.analyze(
            mission,
            execution,
        )

        execution.capability_decision = decision
        execution.required_capabilities = decision.required
        
        # We store just the CapabilityType for execution capabilities
        execution.capabilities = [req.capability for req in decision.required]
        execution.available_capabilities = capability_registry.get_all()

        EventPublisher.publish(
            subsystem="capabilities",
            event_type="CapabilityEvaluationCompleted",
            mission_id=mission.id,
            execution_id=execution.mission_id,
            payload={"decision": decision.model_dump() if hasattr(decision, "model_dump") else {}}
        )

        return decision


capability_manager = CapabilityManager()
