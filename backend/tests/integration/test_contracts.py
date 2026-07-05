from app.platform.models import PlatformEvent
from app.mission.context import MissionContext
from app.models.chat import ChatRequest, ChatResponse

def test_platform_event_contract():
    schema = PlatformEvent.model_json_schema()
    props = schema["properties"]
    
    assert "schema_version" in props
    assert "id" in props
    assert "request_id" in props
    assert "mission_id" in props
    assert "session_id" in props
    assert "timestamp" in props
    assert "subsystem" in props
    assert "event_type" in props
    assert "status" in props
    assert "payload" in props

    required = schema.get("required", [])
    assert "subsystem" in required
    assert "event_type" in required

def test_mission_context_contract():
    # MissionContext is currently implemented as a standard class, but we enforce keys
    # By ensuring we can initialize it with the required structure.
    from app.agents.hermes.context import PromptContext
    import uuid

    pc = PromptContext(
        system_prompt="sys",
        user_query="hi",
        conversation=[],
        knowledge=[],
        capabilities=[],
        tools=[],
        active_mission=None,
        execution_metadata={}
    )
    
    ctx = MissionContext(
        request_id=str(uuid.uuid4()),
        session_id=str(uuid.uuid4()),
        prompt_context=pc
    )
    
    # Assert public interface
    assert hasattr(ctx, "request_id")
    assert hasattr(ctx, "session_id")
    assert hasattr(ctx, "mission")
    assert hasattr(ctx, "prompt_context")
    assert hasattr(ctx, "execution")
    assert hasattr(ctx, "athena_decision")
    assert hasattr(ctx, "plan")
    assert hasattr(ctx, "timing")

def test_chat_contracts():
    req_schema = ChatRequest.model_json_schema()
    assert "message" in req_schema["properties"]
    assert "message" in req_schema.get("required", [])

    res_schema = ChatResponse.model_json_schema()
    assert "response" in res_schema["properties"]
    assert "session_id" in res_schema["properties"]
    assert "response" in res_schema.get("required", [])
