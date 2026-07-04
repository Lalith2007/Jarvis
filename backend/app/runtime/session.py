from uuid import uuid4
from pydantic import BaseModel, Field

class RuntimeSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    active_runtime: str | None = None
    opened_resources: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    
    def cleanup(self):
        self.opened_resources.clear()
