import uuid
from datetime import datetime
import time

from app.agent.service import agent
from app.formatters.markdown import markdown
from app.llm.service import llm
from app.memory.conversation.service import conversation
from app.platform.publisher import EventPublisher
from app.storage.service import storage


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

        # ── Execute agent (Mission → Planner → Executor → Runtime) ────
        # Agent.run() internally calls MissionController which emits
        # MissionCreated, MissionStarted, and MissionCompleted events.
        agent_result = agent.run(user_query, session_id=session_id)

        response = "Mission completed."
        if agent_result.tool_used and agent_result.tool_result is not None:
            if hasattr(agent_result.tool_result, "result"):
                response = str(agent_result.tool_result.result)
            elif hasattr(agent_result.tool_result, "output"):
                response = str(agent_result.tool_result.output)

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

        # Execute mission pipeline (blocking but fast — stream runs in background)
        agent_result = agent.run(user_query, session_id=session_id, stream=True)
        
        stream_id = None
        if agent_result.tool_used and agent_result.tool_result is not None:
            # metadata should be a dict matching StreamResult schema
            res = agent_result.tool_result.metadata
            if isinstance(res, dict) and res.get("is_stream"):
                stream_id = res.get("stream_id")
        
        full_response_parts: list[str] = []
        
        if stream_id:
            from app.runtime.stream import stream_registry
            stream_handle = stream_registry.get_stream(stream_id)
            if stream_handle:
                for chunk in stream_handle:
                    if cancel_event and cancel_event.is_set():
                        break
                    full_response_parts.append(chunk)
                    yield chunk
                stream_registry.remove_stream(stream_id)
            else:
                yield "Streaming failed: handle not found."
        else:
            # Fallback if the capability didn't return a stream
            response = "Mission completed without stream."
            if agent_result.tool_used and agent_result.tool_result is not None:
                if hasattr(agent_result.tool_result, "result"):
                    response = str(agent_result.tool_result.result)
                elif hasattr(agent_result.tool_result, "output"):
                    response = str(agent_result.tool_result.output)
            full_response_parts.append(response)
            yield response

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
