from app.mission.models import Mission, MissionStatus


class MissionState:
    """
    Tracks missions currently known to JARVIS.

    This is the runtime state store.

    Future versions may replace this with:

        • Redis
        • PostgreSQL
        • Distributed state
        • Persistent storage
    """

    def __init__(self):
        self._missions: dict[str, Mission] = {}

    def register(
        self,
        mission: Mission,
    ) -> None:

        self._missions[mission.id] = mission

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
    ) -> Mission | None:

        return self._missions.get(
            mission_id,
        )

    def all(
        self,
    ) -> list[Mission]:

        return list(
            self._missions.values()
        )

    def active(
        self,
    ) -> list[Mission]:

        return [
            mission
            for mission in self._missions.values()
            if mission.status
            not in (
                MissionStatus.COMPLETED,
                MissionStatus.FAILED,
                MissionStatus.CANCELLED,
            )
        ]

    def completed(
        self,
    ) -> list[Mission]:

        return [
            mission
            for mission in self._missions.values()
            if mission.status
            == MissionStatus.COMPLETED
        ]

    def failed(
        self,
    ) -> list[Mission]:

        return [
            mission
            for mission in self._missions.values()
            if mission.status
            == MissionStatus.FAILED
        ]

    def clear(
        self,
    ) -> None:

        self._missions.clear()


mission_state = MissionState()
