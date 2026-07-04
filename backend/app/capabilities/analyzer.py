from typing import TYPE_CHECKING

from app.capabilities.models import (
    CapabilityDecision,
    CapabilityPriority,
    CapabilityRequirement,
    CapabilityType,
)

if TYPE_CHECKING:
    from app.execution.models import ExecutionContext
    from app.mission.models import Mission


class CapabilityAnalyzer:
    """
    Analyzes missions to detect required capabilities.
    Produces a CapabilityDecision.
    """

    def analyze(
        self,
        mission: "Mission",
        execution: "ExecutionContext",
    ) -> CapabilityDecision:
        """
        Detect capability requirements using existing contexts.
        """
        required = []

        # Default capabilities for every mission
        required.append(
            CapabilityRequirement(
                capability=CapabilityType.REASONING,
                priority=CapabilityPriority.CRITICAL,
                reason="All missions require reasoning capability.",
            )
        )
        required.append(
            CapabilityRequirement(
                capability=CapabilityType.PLANNING,
                priority=CapabilityPriority.CRITICAL,
                reason="All missions require planning capability.",
            )
        )

        goal = mission.goal.lower()

        # Coding capability
        if "code" in goal or "program" in goal or "script" in goal or "python" in goal:
            required.append(
                CapabilityRequirement(
                    capability=CapabilityType.CODING,
                    priority=CapabilityPriority.HIGH,
                    reason="Detected coding task in mission goal.",
                )
            )
            required.append(
                CapabilityRequirement(
                    capability=CapabilityType.PYTHON_RUNTIME,
                    priority=CapabilityPriority.HIGH,
                    reason="Coding tasks may require python runtime.",
                )
            )

        # Web / Browser capability
        if "browser" in goal or "web" in goal or "search" in goal or "http" in goal:
            required.append(
                CapabilityRequirement(
                    capability=CapabilityType.BROWSER,
                    priority=CapabilityPriority.HIGH,
                    reason="Detected web interaction in mission goal.",
                )
            )

        # Filesystem capability
        if "file" in goal or "directory" in goal or "folder" in goal or "save" in goal or "read" in goal:
            required.append(
                CapabilityRequirement(
                    capability=CapabilityType.FILESYSTEM,
                    priority=CapabilityPriority.HIGH,
                    reason="Detected filesystem interaction in mission goal.",
                )
            )

        # Memory capability
        if "remember" in goal or "memory" in goal or "recall" in goal:
            required.append(
                CapabilityRequirement(
                    capability=CapabilityType.MEMORY,
                    priority=CapabilityPriority.MEDIUM,
                    reason="Detected memory access request in mission goal.",
                )
            )
            
        # Tool Usage capability
        if "tool" in goal or "use" in goal:
            required.append(
                CapabilityRequirement(
                    capability=CapabilityType.TOOL_USAGE,
                    priority=CapabilityPriority.MEDIUM,
                    reason="Detected tool usage in mission goal.",
                )
            )

        return CapabilityDecision(
            mission_id=mission.id,
            required=required,
            approved=True,
            reasoning="Analyzed mission goal to determine required capabilities.",
        )


capability_analyzer = CapabilityAnalyzer()
