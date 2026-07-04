from app.execution.manager import execution_manager
from app.execution.models import ExecutionContext
from app.mission.models import (
    Mission,
    MissionStatus,
)
from app.mission.pipeline import mission_pipeline
from app.mission.service import mission_service
from app.tools.models import ToolResult


class MissionController:
    """
    Operating System Kernel of JARVIS.

    Every mission enters the backend here.

    The controller owns the lifecycle.

    It does not perform planning or execution itself.
    """

    def create(
        self,
        goal: str,
    ) -> tuple[Mission, ExecutionContext]:

        mission = mission_service.create(goal)

        execution = execution_manager.create(goal)

        mission_service.add_execution(
            mission,
            execution.mission_id,
        )

        return mission, execution

    def run(
        self,
        goal: str,
    ) -> ToolResult | None:
        """
        Executes an entire mission.
        """

        mission, execution = self.create(
            goal,
        )

        self.analyzing(
            mission,
        )

        result = mission_pipeline.run(
            mission,
            execution,
        )

        if result is None:

            self.complete(
                mission,
                execution,
                response="Mission completed.",
            )

            return None

        self.complete(
            mission,
            execution,
            response=result.output,
        )

        return result

    def analyzing(
        self,
        mission: Mission,
    ) -> None:

        mission_service.update_status(
            mission,
            MissionStatus.ANALYZING,
        )

    def planning(
        self,
        mission: Mission,
    ) -> None:

        mission_service.update_status(
            mission,
            MissionStatus.PLANNING,
        )

    def executing(
        self,
        mission: Mission,
        execution: ExecutionContext,
    ) -> None:

        mission_service.update_status(
            mission,
            MissionStatus.EXECUTING,
        )

        execution_manager.start(
            execution,
        )

    def waiting(
        self,
        mission: Mission,
        execution: ExecutionContext,
    ) -> None:

        mission_service.update_status(
            mission,
            MissionStatus.WAITING,
        )

        execution_manager.waiting(
            execution,
        )

    def reflecting(
        self,
        mission: Mission,
    ) -> None:

        mission_service.update_status(
            mission,
            MissionStatus.REFLECTING,
        )

    def complete(
        self,
        mission: Mission,
        execution: ExecutionContext,
        response: str,
    ) -> None:

        execution_manager.complete(
            execution,
        )

        mission_service.complete(
            mission,
            response=response,
        )

    def fail(
        self,
        mission: Mission,
        execution: ExecutionContext,
        response: str,
    ) -> None:

        execution_manager.fail(
            execution,
        )

        mission_service.fail(
            mission,
            response=response,
        )


mission_controller = MissionController()
