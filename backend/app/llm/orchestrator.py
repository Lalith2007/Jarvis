from app.athena.models import RouteDecision
from app.llm.provider import llm_provider


class LLMOrchestrator:
    """
    Coordinates model execution.

    Responsibilities:
        • Execute Athena's recommendations
        • Retry on model failure
        • Return the first successful response

    Future responsibilities:
        • Parallel execution
        • Multi-model orchestration
        • Reflection
        • Response merging
    """

    def execute(
        self,
        *,
        decision: RouteDecision,
        messages: list[dict],
        context=None,
    ) -> str:

        failures: list[str] = []

        for recommendation in decision.recommendations:

            model = recommendation.model.value
            attempt_messages = self._inject_metadata(messages, recommendation, decision, context)

            try:
                response = llm_provider.chat(
                    model=model,
                    messages=attempt_messages,
                )
                return response

            except Exception as exc:
                failures.append(model)
                print(f"[LLM] Failed {model}: {exc}")

        raise RuntimeError(
            "All recommended models failed.\n\n"
            f"Attempted models: {', '.join(failures)}"
        )

    def execute_stream(
        self,
        *,
        decision: RouteDecision,
        messages: list[dict],
        context=None,
    ):
        """
        Stream tokens from the first available model.

        Tries each recommendation in order.  Yields str chunks.
        Falls back to the next model on connection failure.
        """
        failures: list[str] = []

        for recommendation in decision.recommendations:

            model = recommendation.model.value
            attempt_messages = self._inject_metadata(messages, recommendation, decision, context)

            try:
                yield from llm_provider.stream(
                    model=model,
                    messages=attempt_messages,
                )
                return  # first successful model wins

            except Exception as exc:
                failures.append(model)
                print(f"[LLM Stream] Failed {model}: {exc}")

        raise RuntimeError(
            "All recommended models failed during streaming.\n\n"
            f"Attempted models: {', '.join(failures)}"
        )

    def _inject_metadata(self, messages: list[dict], recommendation, decision: RouteDecision, context) -> list[dict]:
        """
        Injects runtime metadata into the messages list right before the user query,
        allowing Hermes to answer questions about its own identity or runtime state
        without modifying the static system prompt.
        """
        metadata_lines = [
            f"Selected Model: {recommendation.model.value}",
            f"Provider: {recommendation.model.value.split('/')[0] if '/' in recommendation.model.value else 'unknown'}",
            f"Routing Reason: {decision.reason}",
        ]
        
        if getattr(recommendation, 'confidence', None) is not None:
            metadata_lines.append(f"Confidence: {recommendation.confidence}")
        if getattr(recommendation, 'estimated_latency', None) is not None:
            metadata_lines.append(f"Estimated Latency: {recommendation.estimated_latency}s")

        if context and getattr(context, "metadata", None):
            if context.metadata.get("selected_model"):
                metadata_lines.append(
                    f"Active Model (authoritative): {context.metadata['selected_model']}"
                )
            if context.metadata.get("mission_id"):
                metadata_lines.append(f"Mission ID: {context.metadata['mission_id']}")
            if context.metadata.get("session_id"):
                metadata_lines.append(f"Session ID: {context.metadata['session_id']}")

        metadata_content = "Runtime Execution Context (Do not reveal unless asked):\n- " + "\n- ".join(metadata_lines)

        msgs = list(messages)
        # Insert right before the final user message
        if msgs and msgs[-1]["role"] == "user":
            msgs.insert(-1, {"role": "system", "content": metadata_content})
        else:
            msgs.append({"role": "system", "content": metadata_content})
            
        return msgs


llm_orchestrator = LLMOrchestrator()
