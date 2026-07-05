import uuid
from datetime import datetime
import time

from app.agent.service import agent
from app.agents.hermes.context import validate_context
from app.agents.hermes.context_builder import context_builder
from app.formatters.markdown import markdown
from app.llm.service import llm
from app.memory.conversation.service import conversation
from app.platform.publisher import EventPublisher
from app.platform.observability import TimingScope
from app.storage.service import storage
from app.mission.context import MissionContext


class Hermes:
    """
    Hermes — stateless request coordinator.

    Hermes does not own state. Conversation state is owned by MemoryService.
    Hermes receives a complete PromptContext and generates a response.
    """

    def __init__(self):
        self.llm = llm

    def chat(
        self,
        user_query: str,
        session_id: str | None = None,
    ) -> tuple[str, str]:
        """
        Execute the full Hermes pipeline synchronously.

        Returns (response, session_id).
        """

        session_id = session_id or str(uuid.uuid4())

        # ── HermesReceivedRequest ─────────────────────────────────────
        EventPublisher.publish(
            subsystem="hermes",
            event_type="HermesReceivedRequest",
            payload={"query": user_query, "session_id": session_id},
        )

        # ── Execute agent (Mission → Planner → Executor) ──────────────
        # Agent.run() internally calls MissionController which emits
        # MissionCreated, MissionStarted, and MissionCompleted events.
        agent_result = agent.run(user_query, session_id=session_id)

        tool_results = []
        if agent_result.tool_used and agent_result.tool_result is not None:
            tool_results.append(
                {
                    "tool_name": "tool",
                    "success": agent_result.tool_result.success,
                    "output": agent_result.tool_result.output,
                }
            )

        # ── Memory retrieval ──────────────────────────────────────────
        with TimingScope(
            subsystem="memory",
            event_base="MemoryRetrieval",
            session_id=session_id,
            mission_id=agent_result.mission_id,
            payload={"session_id": session_id, "query": user_query}
        ) as scope:
            context = context_builder.build(
                user_query=user_query,
                tool_results=tool_results,
                session_id=session_id,
                mission_id=agent_result.mission_id,
                execution_metadata=agent_result.metadata,
            )
            
            scope.payload = {
                "session_id": session_id,
                "knowledge_count": len(context.knowledge),
                "conversation_turns": len(context.conversation),
            }

        # Create MissionContext wrapper
        mission_ctx = MissionContext(
            request_id=str(uuid.uuid4()),
            session_id=session_id,
            prompt_context=context
        )

        # ── Validate context ─────────────────────────────────────────
        validate_context(context)

        # ── LLM (Athena routing + generation) ────────────────────────
        response = self.llm.chat(context)

        # ── Persist conversation ──────────────────────────────────────
        conversation.add_user(user_query)
        conversation.add_assistant(response)

        # ── Persist to Obsidian ───────────────────────────────────────
        now = datetime.now()
        relative_path = (
            f"jarvis/conversations/"
            f"{now.year}/"
            f"{now.month:02d}/"
            f"{now.date()}.md"
        )
        storage.append(
            relative_path,
            markdown.conversation(
                user=user_query,
                assistant=response,
            ),
        )

        return response, session_id

    def chat_stream(
        self,
        user_query: str,
        session_id: str | None = None,
        cancel_event=None,
    ):
        """
        Streaming variant.  Yields text chunks then saves the full
        response to conversation memory when done.

        This is a synchronous generator — run it in asyncio.to_thread()
        when calling from an async FastAPI endpoint.
        """

        session_id = session_id or str(uuid.uuid4())

        EventPublisher.publish(
            subsystem="hermes",
            event_type="HermesReceivedRequest",
            payload={"query": user_query, "session_id": session_id},
        )

        # Execute mission pipeline (blocking but fast — no LLM call yet)
        agent_result = agent.run(user_query, session_id=session_id)
        tool_results = []
        if agent_result.tool_used and agent_result.tool_result is not None:
            tool_results.append(
                {
                    "tool_name": "tool",
                    "success": agent_result.tool_result.success,
                    "output": agent_result.tool_result.output,
                }
            )

        with TimingScope(
            subsystem="memory",
            event_base="MemoryRetrieval",
            session_id=session_id,
            mission_id=agent_result.mission_id,
            payload={"session_id": session_id}
        ) as scope:
            context = context_builder.build(
                user_query=user_query,
                tool_results=tool_results,
                session_id=session_id,
                mission_id=agent_result.mission_id,
                execution_metadata=agent_result.metadata,
            )
            
            scope.payload = {
                "session_id": session_id,
                "knowledge_count": len(context.knowledge),
            }

        mission_ctx = MissionContext(
            request_id=str(uuid.uuid4()),
            session_id=session_id,
            prompt_context=context
        )

        validate_context(context)

        # Stream LLM response
        full_response_parts: list[str] = []
        for chunk in self.llm.stream(context):
            if cancel_event and cancel_event.is_set():
                break
            full_response_parts.append(chunk)
            yield chunk

        if cancel_event and cancel_event.is_set():
            # Abort persistence if client disconnected early
            return

        # Persist after streaming completes
        full_response = "".join(full_response_parts)
        conversation.add_user(user_query)
        conversation.add_assistant(full_response)

        now = datetime.now()
        storage.append(
            f"jarvis/conversations/{now.year}/{now.month:02d}/{now.date()}.md",
            markdown.conversation(user=user_query, assistant=full_response),
        )


hermes = Hermes()
