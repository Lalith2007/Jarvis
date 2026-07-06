from app.agents.hermes.models import PromptContext
from app.llm.prompts.loader import prompt_loader
from app.memory.conversation.service import conversation


class ContextBuilder:
    """
    Sprint 12.8 — Capability-first ContextBuilder (formatter only).

    This class formats inputs into a PromptContext.  It does NOT:
      - query the vault
      - route requests
      - retrieve memories
      - perform capability discovery at build time

    All data arrives as parameters from upstream capabilities that have
    already executed inside the Mission Graph.

    Parameters
    ----------
    user_query:
        The raw user query string.
    tool_results:
        Structured output dicts from prior capability nodes.
        Each dict: {"tool_name": str, "success": bool, "output": Any}
        "output" may be a plain str OR a structured dict/list.
    session_id:
        Session identifier forwarded from Hermes.
    mission_id:
        Active mission identifier.
    execution_metadata:
        Extra key/value pairs to include in PromptContext.metadata.
    injected_knowledge:
        Pre-fetched memory results (from memory.retrieve node).
    selected_model:
        Model ID chosen by the unified AthenaDecision.  Injected into
        metadata so the system prompt carries it as ground truth.
    """

    from app.capabilities.core.grounding import GROUNDING_CAPABILITY_IDS as _GROUNDING_CAP_IDS

    def build(
        self,
        user_query: str,
        tool_results: list[dict] | None = None,
        knowledge_limit: int = 3,
        session_id: str | None = None,
        mission_id: str | None = None,
        execution_metadata: dict | None = None,
        injected_knowledge: list | None = None,
        selected_model: str | None = None,
    ) -> PromptContext:

        knowledge = injected_knowledge or []
        resolved_tool_results = tool_results or []

        # Detect whether any grounding capability output is present.
        grounding_enforced = any(
            t.get("tool_name") in self._GROUNDING_CAP_IDS
            for t in resolved_tool_results
        )

        # Runtime metadata injected into the context so the LLM can answer
        # grounding questions using authoritative system data.
        metadata: dict = dict(execution_metadata or {})
        if session_id:
            metadata["session_id"] = session_id
        if mission_id:
            metadata["mission_id"] = mission_id
        if selected_model:
            metadata["selected_model"] = selected_model

        return PromptContext(
            system_prompt=prompt_loader.load("system.md"),
            conversation=conversation.history(),
            knowledge=knowledge,
            tool_results=resolved_tool_results,
            user_query=user_query,
            session_id=session_id,
            metadata=metadata,
            grounding_enforced=grounding_enforced,
        )


context_builder = ContextBuilder()
