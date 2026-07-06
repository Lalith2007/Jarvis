"""
Integration tests for the Hermes Intelligence Pipeline.

Tests the complete request flow:
  hermes.chat() → Mission → Memory → Athena → Planner → Executor → Events
"""

from unittest.mock import MagicMock, patch
import pytest

from app.agents.hermes.service import hermes
from app.agents.hermes.context_builder import context_builder
from app.mission.controller import mission_controller
from app.mission.service import mission_service
from app.memory.conversation.service import conversation
from app.platform.models import PlatformEvent


# ── Fixtures ──────────────────────────────────────────────────────────────────

FIXED_LLM_RESPONSE = "Hello from the mocked LLM."


@pytest.fixture(autouse=True)
def patch_llm(monkeypatch):
    """
    Patch the LLM provider at the orchestrator level so all execution paths
    (hermes.chat, hermes.chat_stream, llm_orchestrator.execute) hit the mock.
    """
    from app.llm import orchestrator as orchestrator_module
    from app.llm import provider as provider_module

    mock_provider = MagicMock()
    mock_provider.chat.return_value = FIXED_LLM_RESPONSE
    mock_provider.stream.return_value = iter(["Hello", " from", " stream."])

    # Patch in both modules to cover all import paths
    monkeypatch.setattr(provider_module, "llm_provider", mock_provider)
    monkeypatch.setattr(orchestrator_module, "llm_provider", mock_provider)
    yield mock_provider


@pytest.fixture(autouse=True)
def clear_mission_store():
    """Reset in-memory mission store between tests."""
    mission_service.clear()
    yield
    mission_service.clear()


@pytest.fixture(autouse=True)
def clear_conversation():
    """Reset conversation memory between tests."""
    conversation.clear()
    yield
    conversation.clear()


# ── Hermes.chat() ────────────────────────────────────────────────────────────

class TestHermesChatReturnValue:
    def test_returns_tuple(self):
        result = hermes.chat("What time is it?")
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_response_is_string(self):
        response, _ = hermes.chat("What time is it?")
        assert isinstance(response, str)
        assert len(response) > 0

    def test_session_id_is_string(self):
        _, session_id = hermes.chat("Hello")
        assert isinstance(session_id, str)
        assert len(session_id) > 0

    def test_session_id_propagated(self):
        given_id = "test-session-abc"
        _, returned_id = hermes.chat("Hello", session_id=given_id)
        assert returned_id == given_id

    def test_response_is_llm_output(self):
        response, _ = hermes.chat("Tell me something")
        assert response == FIXED_LLM_RESPONSE


class TestHermesChatSavesConversation:
    def test_conversation_saved(self):
        hermes.chat("What is JARVIS?")
        history = conversation.history()
        assert any(m["role"] == "user" for m in history)
        assert any(m["role"] == "assistant" for m in history)

    def test_conversation_contains_query(self):
        hermes.chat("My unique query XYZ")
        history = conversation.history()
        user_messages = [m["content"] for m in history if m["role"] == "user"]
        assert "My unique query XYZ" in user_messages


# ── Hermes Platform Events ────────────────────────────────────────────────────

class TestHermesPlatformEvents:
    def test_emits_hermes_received_request(self):
        received: list[PlatformEvent] = []

        from app.platform.event_bus import event_bus
        from app.platform.subscriber import EventSubscriber

        async def capture(event: PlatformEvent):
            received.append(event)

        sub = EventSubscriber(
            callback=capture,
            subsystems=["hermes"],
            event_types=["HermesReceivedRequest"],
        )
        event_bus.subscribe(sub)

        import time
        hermes.chat("Hello pipeline")
        time.sleep(0.2)  # allow async dispatch

        event_bus.unsubscribe(sub)

        hermes_events = [e for e in received if e.event_type == "HermesReceivedRequest"]
        assert len(hermes_events) >= 1




# ── ContextBuilder enrichment ────────────────────────────────────────────────

class TestContextBuilderEnrichment:
    def test_session_id_in_context(self):
        ctx = context_builder.build(
            user_query="hello",
            session_id="test-session-123",
        )
        assert ctx.session_id == "test-session-123"
        assert ctx.metadata.get("session_id") == "test-session-123"

    def test_context_has_system_prompt(self):
        ctx = context_builder.build(user_query="hello")
        assert ctx.system_prompt
        assert len(ctx.system_prompt) > 0

    def test_context_has_user_query(self):
        ctx = context_builder.build(user_query="test query")
        assert ctx.user_query == "test query"


# ── Mission Controller ────────────────────────────────────────────────────────

class TestMissionController:
    def test_create_returns_mission_and_execution(self):
        mission, execution = mission_controller.create("Test goal")
        assert mission.id
        assert mission.goal == "Test goal"
        assert execution.mission_id

    def test_mission_stored_after_create(self):
        mission, _ = mission_controller.create("Store this goal")
        stored = mission_service.get(mission.id)
        assert stored is not None
        assert stored.goal == "Store this goal"

    def test_run_completes_mission(self):
        result = mission_controller.run("Simple goal with no tools")
        missions = mission_service.all()
        assert len(missions) >= 1
        completed = [m for m in missions if m.status.value == "completed"]
        assert len(completed) >= 1

    def test_run_emits_mission_created(self):
        received: list[PlatformEvent] = []

        from app.platform.event_bus import event_bus
        from app.platform.subscriber import EventSubscriber

        async def capture(event: PlatformEvent):
            received.append(event)

        sub = EventSubscriber(
            callback=capture,
            subsystems=["mission"],
            event_types=["MissionCreated"],
        )
        event_bus.subscribe(sub)

        import time
        mission_controller.run("Another simple goal")
        time.sleep(0.2)

        event_bus.unsubscribe(sub)

        created_events = [e for e in received if e.event_type == "MissionCreated"]
        assert len(created_events) >= 1


# ── Streaming ─────────────────────────────────────────────────────────────────

class TestHermesChatStream:
    def test_stream_yields_chunks(self):
        chunks = list(hermes.chat_stream("Stream test"))
        assert len(chunks) > 0
        assert all(isinstance(c, str) for c in chunks)

    def test_stream_saves_conversation(self):
        before = len(conversation.history())
        list(hermes.chat_stream("Stream and save"))  # consume fully
        import time
        time.sleep(0.05)
        after = len(conversation.history())
        assert after > before
