from datetime import datetime

from pydantic import BaseModel, Field


class ConversationArtifact(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)

    user: str

    assistant: str
