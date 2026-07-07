from datetime import datetime
from uuid import uuid4

from app.mission.models import (
    Mission,
    MissionPriority,
    MissionStatus,
)


class MissionService:
    """
    Public interface for creating and managing missions.

    All external components (Hermes, API, Voice,
    Scheduler, etc.) communicate with the Mission
    subsystem through this service.
    """

    def __init__(self):
        self._missions: dict[str, Mission] = {}

    def create(
        self,
        goal: str,
        priority: MissionPriority = MissionPriority.NORMAL,
    ) -> Mission:

        mission = Mission(
            id=str(uuid4()),
            goal=goal,
            priority=priority,
        )

        self._missions[mission.id] = mission

        return mission

    def get(
        self,
        mission_id: str,
    ) -> Mission | None:

        return self._missions.get(mission_id)

    def all(
        self,
    ) -> list[Mission]:

        return list(self._missions.values())

    def _checkpoint(self, mission: Mission) -> None:
        from app.mission.store import mission_store
        mission_store.checkpoint(mission)

    def update_status(
        self,
        mission: Mission,
        status: MissionStatus,
    ) -> None:

        mission.status = status
        mission.updated_at = datetime.now()
        self._checkpoint(mission)

    def pause(self, mission: Mission) -> None:
        mission.status = MissionStatus.WAITING
        mission.updated_at = datetime.now()
        mission.metadata["paused"] = True
        self._checkpoint(mission)

    def resume(self, mission: Mission) -> None:
        mission.metadata.pop("paused", None)
        mission.status = MissionStatus.EXECUTING
        mission.updated_at = datetime.now()
        self._checkpoint(mission)

    def cancel(self, mission: Mission) -> None:
        mission.status = MissionStatus.CANCELLED
        mission.updated_at = datetime.now()
        self._checkpoint(mission)

    def add_execution(
        self,
        mission: Mission,
        execution_id: str,
    ) -> None:

        mission.execution_ids.append(execution_id)
        mission.updated_at = datetime.now()

    def complete(
        self,
        mission: Mission,
        response: str,
        success: bool = True,
    ) -> None:

        mission.status = MissionStatus.COMPLETED
        mission.updated_at = datetime.now()

        mission.result.success = success
        mission.result.response = response
        self._checkpoint(mission)

    def fail(
        self,
        mission: Mission,
        response: str,
    ) -> None:

        mission.status = MissionStatus.FAILED
        mission.updated_at = datetime.now()

        mission.result.success = False
        mission.result.response = response
        self._checkpoint(mission)

    def remove(
        self,
        mission_id: str,
    ) -> None:

        self._missions.pop(
            mission_id,
            None,
        )

    def clear(
        self,
    ) -> None:

        self._missions.clear()


mission_service = MissionService()
