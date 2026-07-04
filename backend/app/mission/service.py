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

    def update_status(
        self,
        mission: Mission,
        status: MissionStatus,
    ) -> None:

        mission.status = status
        mission.updated_at = datetime.now()

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

    def fail(
        self,
        mission: Mission,
        response: str,
    ) -> None:

        mission.status = MissionStatus.FAILED
        mission.updated_at = datetime.now()

        mission.result.success = False
        mission.result.response = response

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
