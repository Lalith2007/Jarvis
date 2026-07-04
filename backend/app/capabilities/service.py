from typing import TYPE_CHECKING

from app.capabilities.manager import capability_manager
from app.capabilities.models import CapabilityDecision, CapabilityType
from app.capabilities.registry import capability_registry

if TYPE_CHECKING:
    from app.execution.models import ExecutionContext
    from app.mission.models import Mission


class CapabilityService:
    """
    Clean public API for the Capability Manager subsystem.
    Other subsystems must communicate only through this service.
    """

    def evaluate_mission(
        self,
        mission: "Mission",
        execution: "ExecutionContext",
    ) -> CapabilityDecision:
        """
        Evaluate the required capabilities for a mission.
        """
        return capability_manager.evaluate(
            mission,
            execution,
        )

    def register_capability(
        self,
        capability: CapabilityType,
    ) -> None:
        """
        Register a new capability in the system.
        """
        capability_registry.register(
            capability,
        )

    def get_available_capabilities(self) -> list[CapabilityType]:
        """
        List all available capabilities.
        """
        return capability_registry.get_all()


capability_service = CapabilityService()
