from dataclasses import dataclass, field
from typing import Any, Optional

from app.agents.hermes.models import PromptContext
from app.execution.models import ExecutionContext
from app.mission.models import Mission

@dataclass
class AthenaDecision:
    primary_model: str
    reason: str
    confidence: float = 1.0


@dataclass
class MissionContext:
    """
    Immutable(ish) context object passed through the pipeline.
    Wraps existing contexts to maintain compatibility while
    enforcing a single state object.
    """
    request_id: str
    session_id: str
    
    # Core domain objects
    mission: Optional[Mission] = None
    prompt_context: Optional[PromptContext] = None
    execution: Optional[ExecutionContext] = None
    
    # Decisions & Metadata
    athena_decision: Optional[AthenaDecision] = None
    plan: Optional[Any] = None
    
    timing: dict[str, int] = field(default_factory=dict)
    
    @property
    def mission_id(self) -> str:
        return self.mission.id if self.mission else ""

