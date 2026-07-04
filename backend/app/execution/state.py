from app.execution.models import (
    ExecutionContext,
    ExecutionStatus,
)


class ExecutionStateManager:
    """
    Tracks all active execution contexts.

    Future responsibilities:

    • Background missions
    • Mission cancellation
    • Mission resume
    • Scheduler integration
    • Parallel execution
    """

    def __init__(self):
        self._missions: dict[str, ExecutionContext] = {}

    def register(
        self,
        context: ExecutionContext,
    ) -> None:

        self._missions[
            context.mission_id
        ] = context

    def remove(
        self,
        mission_id: str,
    ) -> None:

        self._missions.pop(
            mission_id,
            None,
        )

    def get(
        self,
        mission_id: str,
    ) -> ExecutionContext | None:

        return self._missions.get(
            mission_id,
        )

    def all(
        self,
    ) -> list[ExecutionContext]:

        return list(
            self._missions.values()
        )

    def running(
        self,
    ) -> list[ExecutionContext]:

        return [
            mission
            for mission in self._missions.values()
            if mission.status
            == ExecutionStatus.RUNNING
        ]

    def waiting(
        self,
    ) -> list[ExecutionContext]:

        return [
            mission
            for mission in self._missions.values()
            if mission.status
            == ExecutionStatus.WAITING
        ]

    def completed(
        self,
    ) -> list[ExecutionContext]:

        return [
            mission
            for mission in self._missions.values()
            if mission.status
            == ExecutionStatus.COMPLETED
        ]

    def failed(
        self,
    ) -> list[ExecutionContext]:

        return [
            mission
            for mission in self._missions.values()
            if mission.status
            == ExecutionStatus.FAILED
        ]

    def clear(
        self,
    ) -> None:

        self._missions.clear()


execution_state = ExecutionStateManager()
