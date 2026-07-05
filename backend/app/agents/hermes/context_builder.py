from app.agents.hermes.models import PromptContext
from app.llm.prompts.loader import prompt_loader
from app.memory.conversation.service import conversation
from app.memory.vault.service import vault
from app.query.service import query_processor


class ContextBuilder:
    """
    Builds a complete PromptContext before Hermes invokes the LLM.

    Context includes:
      - system prompt
      - conversation history
      - vault knowledge
      - tool results
      - session_id
      - metadata (capabilities, runtime status)
    """

    def build(
        self,
        user_query: str,
        tool_results: list[dict] | None = None,
        knowledge_limit: int = 3,
        session_id: str | None = None,
        mission_id: str | None = None,
        execution_metadata: dict | None = None,
    ) -> PromptContext:

        processed_query = query_processor.process(user_query)

        try:
            knowledge = vault.search(
                processed_query,
                limit=knowledge_limit,
            )
        except Exception as exc:
            knowledge = []
            from app.platform.publisher import EventPublisher
            EventPublisher.publish(
                subsystem="memory",
                event_type="MemoryRetrievalFailed",
                session_id=session_id,
                mission_id=mission_id,
                status="error",
                severity="error",
                payload={"error": str(exc)},
            )

        # Collect runtime metadata to give the LLM situational awareness
        metadata: dict = execution_metadata or {}
        if session_id:
            metadata["session_id"] = session_id
        if mission_id:
            metadata["mission_id"] = mission_id

        try:
            from app.capabilities.registry import capability_registry
            metadata["available_capabilities"] = [
                c.value for c in capability_registry.get_all()
            ]
        except Exception:
            pass

        try:
            from app.runtime.manager import runtime_manager
            metadata["active_runtime_sessions"] = len(
                runtime_manager._active_sessions
            )
        except Exception:
            pass

        return PromptContext(
            system_prompt=prompt_loader.load("system.md"),
            conversation=conversation.history(),
            knowledge=knowledge,
            tool_results=tool_results or [],
            user_query=user_query,
            session_id=session_id,
            metadata=metadata,
        )


context_builder = ContextBuilder()
