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
        • Streaming
        • Response merging
    """

    def execute(
        self,
        *,
        decision: RouteDecision,
        messages: list[dict],
    ) -> str:

        print(
            f"[Athena] Primary: {decision.primary.value}"
        )

        failures: list[str] = []

        for recommendation in decision.recommendations:

            model = recommendation.model.value

            print(f"[LLM] Trying {model}")

            try:

                response = llm_provider.chat(
                    model=model,
                    messages=messages,
                )

                print(f"[LLM] Success: {model}")

                return response

            except Exception as exc:

                print(f"[LLM] Failed: {model}")

                print(exc)

                failures.append(model)

        raise RuntimeError(
            "All recommended models failed.\n\n"
            f"Attempted models: {', '.join(failures)}"
        )


llm_orchestrator = LLMOrchestrator()
