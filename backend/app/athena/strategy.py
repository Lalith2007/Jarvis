from enum import Enum

from pydantic import BaseModel

from app.athena.models import ModelType


class ExecutionMode(str, Enum):
    """
    Overall execution mode selected by Athena.
    """

    SINGLE = "single"

    MULTI = "multi"


class ExecutionStrategy(BaseModel):
    """
    High-level execution plan produced by Athena.

    Hermes follows this strategy instead of making
    orchestration decisions itself.
    """

    mode: ExecutionMode

    primary: ModelType

    planner: ModelType | None = None

    researcher: ModelType | None = None

    implementer: ModelType | None = None

    writer: ModelType | None = None

    fallback: ModelType | None = None

    reason: str

