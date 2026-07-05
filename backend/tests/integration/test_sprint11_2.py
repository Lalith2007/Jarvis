import pytest
from app.platform.models import PlatformEvent
from app.platform.publisher import EventPublisher
from app.platform.observability import TimingScope
from app.platform.errors import MissionFailed
from app.mission.context import MissionContext, AthenaDecision
import time

def test_platform_event_schema_version():
    event = PlatformEvent(subsystem="test", event_type="TestEvent")
    assert event.schema_version == "1.0"
    assert event.request_id is not None

def test_mission_context_immutability_and_wrapping():
    ctx = MissionContext(
        request_id="req-123",
        session_id="sess-456",
        athena_decision=AthenaDecision(primary_model="test-model", reason="test")
    )
    assert ctx.athena_decision.primary_model == "test-model"

def test_timing_scope_success():
    events = []
    
    # Mock publisher
    def mock_publish(*args, **kwargs):
        events.append(kwargs)
    
    EventPublisher.publish = mock_publish
    
    with TimingScope(subsystem="test", event_base="Action", session_id="123") as scope:
        time.sleep(0.01)
        scope.payload = {"result": 42}
        
    assert len(events) == 2
    assert events[0]["event_type"] == "ActionStarted"
    assert events[1]["event_type"] == "ActionCompleted"
    assert events[1]["duration_ms"] >= 10
    assert events[1]["payload"]["result"] == 42

def test_timing_scope_failure():
    events = []
    
    def mock_publish(*args, **kwargs):
        events.append(kwargs)
    
    EventPublisher.publish = mock_publish
    
    try:
        with TimingScope(subsystem="test", event_base="Action", session_id="123"):
            raise MissionFailed("Testing failure", recoverable=True)
    except MissionFailed:
        pass
        
    assert len(events) == 2
    assert events[0]["event_type"] == "ActionStarted"
    assert events[1]["event_type"] == "ActionFailed"
    assert events[1]["severity"] == "error"
    assert events[1]["payload"]["error_type"] == "MissionFailed"
    assert events[1]["payload"]["recoverable"] is True
