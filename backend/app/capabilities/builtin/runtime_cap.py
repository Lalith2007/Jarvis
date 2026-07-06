import logging
import threading
from app.capabilities.core.base import BaseCapability
from app.capabilities.core.models import (
    CapabilityManifest,
    CapabilityCategory,
    CapabilityConfig,
    CapabilityContext,
    CapabilityDiagnostics,
    CapabilityResult,
)
from app.llm.service import llm
from app.runtime.stream import stream_registry, StreamResult

logger = logging.getLogger(__name__)

# Keys that are execution bookkeeping, not tool output.
_INTERNAL_STATE_KEYS = frozenset(
    {"goal", "query", "session_id", "mission_id", "execution_id", "stream"}
)

# Grounding capability IDs — their outputs must be present before generation
# when they were declared required in the AthenaDecision.
from app.capabilities.core.grounding import GROUNDING_CAPABILITY_IDS as _GROUNDING_CAP_IDS


class RuntimeGenerateCapability(BaseCapability):
    """
    Executes generative AI models (LLMs) as the terminal node of every
    Mission Graph.

    Sprint 12.8 change — Unified Athena Authority:
    When an AthenaDecision is available on the CapabilityContext (forwarded
    by MissionGraphBuilder), this capability builds a RouteDecision directly
    from the pre-computed recommended_models instead of triggering a second
    independent Athena routing pass.  The second Athena instance
    (athena/router.py) is only called as a fallback when no decision is
    present.
    """

    def __init__(self):
        manifest = CapabilityManifest(
            id="runtime.generate",
            name="Runtime Generative Engine",
            version="1.0.0",
            author="System",
            description="Executes generative AI models (LLMs).",
            category=CapabilityCategory.TOOL,
            permissions=["execute:generation"],
        )
        super().__init__(manifest, CapabilityConfig())

    def initialize(self, context: CapabilityContext) -> None:
        pass

    def validate(self, context: CapabilityContext) -> None:
        pass

    # ──────────────────────────────────────────────────────────────────────────
    # Grounding validation
    # ──────────────────────────────────────────────────────────────────────────

    def _validate_grounding(self, context: CapabilityContext) -> list[str]:
        """
        Verify that every grounding capability that was declared *required* in
        the AthenaDecision has produced output in runtime_state.

        Returns a list of missing capability IDs.  Empty list = all present.
        """
        decision = context.athena_decision
        if decision is None:
            return []

        missing: list[str] = []
        for cap in decision.recommended_capabilities:
            if cap.capability in _GROUNDING_CAP_IDS and cap.required:
                if cap.capability not in context.runtime_state:
                    missing.append(cap.capability)

        if missing:
            logger.warning(
                "Grounding validation FAILED — missing required capability outputs: %s",
                missing,
            )
        else:
            grounding_present = [
                cap.capability
                for cap in decision.recommended_capabilities
                if cap.capability in _GROUNDING_CAP_IDS and cap.required
            ]
            if grounding_present:
                logger.info(
                    "Grounding validation PASSED — required outputs present: %s",
                    grounding_present,
                )

        return missing

    def execute(
        self, context: CapabilityContext, diagnostics: CapabilityDiagnostics
    ) -> CapabilityResult:
        from app.agents.hermes.context_builder import context_builder

        query = (
            context.runtime_state.get("goal")
            or context.runtime_state.get("query")
            or ""
        )
        session_id = context.runtime_state.get("session_id") or (
            context.execution_id.split("-")[0] if context.execution_id else None
        )
        mission_id = context.runtime_state.get("mission_id")

        # ── Policy rejection (Sprint 12.9) ────────────────────────────────────
        # If Athena's PolicyEngine rejected the request, report the rejection
        # instead of generating an ungrounded answer from prior knowledge.
        decision = context.athena_decision
        if decision is not None and getattr(decision, "policy_rejection", None):
            logger.warning("Policy rejection surfaced to user: %s", decision.policy_rejection)
            return CapabilityResult(
                success=True,
                status="policy_rejected",
                result=decision.policy_rejection,
            )

        # ── Grounding validation (Sprint 12.9) ────────────────────────────────
        # Before building the prompt, verify all required grounding capability
        # outputs are present.  If any are missing, return a structured refusal
        # instead of generating from prior knowledge.
        missing_grounding = self._validate_grounding(context)
        if missing_grounding:
            refusal = (
                "I was unable to retrieve the authoritative system information "
                f"required to answer this question. "
                f"The following data sources did not return results: "
                f"{', '.join(missing_grounding)}. "
                "I will not fabricate this information from prior knowledge."
            )
            logger.error(
                "Grounding refusal triggered for missing capabilities: %s",
                missing_grounding,
            )
            return CapabilityResult(
                success=True,
                status="grounding_refused",
                result=refusal,
            )

        # Collect structured tool outputs from prior nodes.
        # Only forward keys that look like capability IDs (contain a dot) to
        # avoid flooding the prompt with dict-spread sub-keys (e.g. "models",
        # "count") that were already included in the capability-keyed entry.
        tool_results = []
        for key, value in context.runtime_state.items():
            if key not in _INTERNAL_STATE_KEYS and "." in key:
                tool_results.append(
                    {"tool_name": key, "success": True, "output": value}
                )

        _memory_raw = context.runtime_state.get("memory.retrieve")
        if isinstance(_memory_raw, dict):
            injected_knowledge = _memory_raw.get("results") or []
        elif isinstance(_memory_raw, list):
            injected_knowledge = _memory_raw
        else:
            injected_knowledge = []

        # ── Build RouteDecision from the AthenaDecision carried by this node ──
        # This eliminates the redundant second Athena routing pass.
        route_decision = self._build_route_decision(context)

        prompt_ctx = context_builder.build(
            user_query=query,
            tool_results=tool_results,
            session_id=session_id,
            mission_id=mission_id,
            injected_knowledge=injected_knowledge,
            selected_model=(
                route_decision.primary.value if route_decision else None
            ),
        )

        stream_flag = context.runtime_state.get("stream", False)

        if stream_flag:
            stream_handle = stream_registry.create_stream()

            def _stream_worker():
                try:
                    for chunk in llm.stream(prompt_ctx, route_decision=route_decision):
                        stream_handle.push(chunk)
                except Exception as exc:
                    import traceback
                    print(f"Streaming error: {exc}\n{traceback.format_exc()}")
                finally:
                    stream_handle.finish()

            threading.Thread(target=_stream_worker, daemon=True).start()

            return CapabilityResult(
                success=True,
                status="streaming",
                result=StreamResult(stream_id=stream_handle.stream_id).model_dump(),
            )
        else:
            response = llm.chat(prompt_ctx, route_decision=route_decision)
            return CapabilityResult(
                success=True,
                status="completed",
                result=response,
            )

    # ──────────────────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _build_route_decision(self, context: CapabilityContext):
        """
        Constructs a RouteDecision from the AthenaDecision embedded in the
        CapabilityContext.  Returns None when no decision is available so the
        caller can fall back to the legacy routing path.
        """
        decision = context.athena_decision
        if decision is None or not decision.recommended_models:
            return None

        from app.athena.models import RouteDecision

        return RouteDecision(
            primary=decision.recommended_models[0].model,
            recommendations=decision.recommended_models,
            reason="Pre-computed by AthenaOrchestrator (Sprint 12.8 unified Athena authority).",
        )

    def cleanup(self, context: CapabilityContext) -> None:
        pass

    def health_check(self) -> str:
        return "healthy"

    def estimate_cost(self, context: CapabilityContext) -> float:
        return 0.1

    def estimate_latency(self, context: CapabilityContext) -> float:
        return 1000.0
