from datetime import datetime
from uuid import uuid4
from pydantic import BaseModel, Field
from app.runtime.models import RuntimeStatus, RuntimeResult

class RuntimeSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    status: RuntimeStatus = RuntimeStatus.CREATED
    active_runtime: str | None = None
    opened_resources: list[str] = Field(default_factory=list)
    history: list[RuntimeResult] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def transition_to(self, new_status: RuntimeStatus) -> None:
        self.status = new_status
        self.updated_at = datetime.now()

    def add_result(self, result: RuntimeResult) -> None:
        self.history.append(result)
        self.updated_at = datetime.now()
        
    def cleanup(self) -> None:
        self.opened_resources.clear()
        self.transition_to(RuntimeStatus.CLEANED_UP)
