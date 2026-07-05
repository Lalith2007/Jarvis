from app.platform.models import PlatformEvent
from app.mission.context import MissionContext
from app.agents.hermes.context import PromptContext
import uuid
from datetime import datetime
import json
import dataclasses

ctx = MissionContext(
    request_id="req-123",
    session_id="session-456",
    prompt_context=PromptContext(
        system_prompt="You are Jarvis",
        user_query="Hello",
        conversation=[],
        knowledge=[],
        capabilities=[],
        tools=[],
        active_mission=None,
        execution_metadata={}
    )
)
print("--- 7. MISSIONCONTEXT ---")
def default_serializer(obj):
    if dataclasses.is_dataclass(obj):
        return dataclasses.asdict(obj)
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    return str(obj)

print(json.dumps(dataclasses.asdict(ctx), indent=2, default=default_serializer))

evt = PlatformEvent(
    schema_version="1.0",
    request_id="req-123",
    mission_id="miss-789",
    session_id="session-456",
    timestamp=datetime.utcnow().isoformat() + "Z",
    subsystem="athena",
    event_type="AthenaRouted",
    status="success",
    duration_ms=120,
    payload={"model": "gemini-pro"}
)
print("--- 6. EVENT VALIDATION ---")
print(evt.model_dump_json(indent=2))
