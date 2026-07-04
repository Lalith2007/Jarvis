from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class MissionEventType(str, Enum):
    """
    Events emitted during a mission lifecycle.
    """

    CREATED = "created"

    ANALYZING = "analyzing"

    PLANNING = "planning"

    EXECUTING = "executing"

    WAITING = "waiting"

    REFLECTING = "reflecting"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"


class MissionEvent(BaseModel):
    """
    Represents a single mission event.
    """

    mission_id: str

    event: MissionEventType

    message: str = ""

    created_at: datetime = Field(default_factory=datetime.now)

    metadata: dict = Field(default_factory=dict)


class MissionEventBus:
    """
    Temporary in-memory event bus.

    Future versions may stream events over:

        • WebSocket
        • Redis
        • RabbitMQ
        • Kafka

    without changing the Mission Controller.
    """

    def __init__(self):
        self._events: list[MissionEvent] = []

    def publish(
        self,
        event: MissionEvent,
    ) -> None:

        self._events.append(event)

    def all(
        self,
    ) -> list[MissionEvent]:

        return self._events.copy()

    def clear(
        self,
    ) -> None:

        self._events.clear()


mission_events = MissionEventBus()
