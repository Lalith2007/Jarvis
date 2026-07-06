"""
Athena CapabilityEngine — Sprint 12.9 Semantic Intent Mapping
=============================================================

Replaces brittle phrase matching with a structured intent-group table.

Architecture contract:
  - Returns (List[CapabilityRecommendation], confidence) ordered for execution.
  - runtime.generate is always appended last (terminal node).
  - Grounding capabilities (registry.models, registry.capabilities,
    memory.retrieve) are marked required=True when their group triggers so
    runtime.generate refuses to hallucinate if they fail.
  - planner/executor are only added for genuinely complex, multi-step tasks.

Intent groups are checked in priority order. The first matching group wins for
grounding; additional groups can co-fire for multi-capability queries.
"""

import re
from typing import List, Tuple

from app.athena.models import CapabilityRecommendation, IntentClass


# ---------------------------------------------------------------------------
# Semantic intent groups
# ---------------------------------------------------------------------------
# Each group: (name, patterns, capability_id, confidence, reason)
# Patterns are OR-ed against goal_lower. First match adds the capability.
#
# Ordering: more specific patterns first to prevent short-circuit mis-fires.
# ---------------------------------------------------------------------------

_GROUNDING_GROUPS: list[tuple[str, list[str], str, float, str]] = [
    # ── Model / Provider information ─────────────────────────────────────────
    (
        "model_information",
        [
            # Active model identity
            r"which model are you",
            r"what model are you",
            r"what model is (this|active|running|selected|used|being used)",
            r"which model is (this|active|running|selected|used|being used)",
            r"which llm (are you|is|do you use)",
            r"what llm (are you|is|do you use)",
            r"which (ai|language model) are you",
            r"are you (gpt|claude|gemini|llama|deepseek|minimax|nemotron)",
            # Available models
            r"what models (are available|do you have|exist|can i use|are there)",
            r"which models (are available|do you have|exist|can i use|are there)",
            r"available models",
            r"list (the |all |available )?models",
            r"show (the |all |available )?models",
            r"(what|which) models",
            r"model list",
            r"model registry",
            # Provider information
            r"how many providers",
            r"which providers",
            r"what providers",
            r"list providers",
            r"available providers",
            r"provider(s)? (are |is |that are |that is )?(configured|available|registered|installed|set up)",
            r"(configured|available|registered|installed) providers",
        ],
        "registry.models",
        0.98,
        "Query requires authoritative model/provider data from ProviderRegistry.",
    ),
    # ── Capability / Tool information ────────────────────────────────────────
    (
        "capability_information",
        [
            r"what (tools|capabilities|functions|abilities|features|skills) (do you have|exist|are available|are there|are installed|are registered)",
            r"which (tools|capabilities|functions|abilities|features|skills) (do you have|exist|are available|are there|are installed|are registered)",
            r"what can you do",
            r"what are you capable of",
            r"what are your (capabilities|tools|functions|abilities|features|skills)",
            r"list (the |all |available |your )?(tools|capabilities|functions|abilities|features|skills)",
            r"show (the |all |available |your )?(tools|capabilities|functions|abilities|features|skills)",
            r"available (tools|capabilities|functions|abilities|features|skills)",
            r"(tools|capabilities|functions|abilities|features|skills) (available|installed|registered|configured|exist)",
            r"capability registry",
            r"(what|which) (tools|capabilities|functions|abilities|features|skills)",
            r"installed capabilities",
            r"registered capabilities",
            # bare capability nouns that appear alongside other query terms
            r"\bcapabilities exist\b",
            r"\btools exist\b",
        ],
        "registry.capabilities",
        0.98,
        "Query requires authoritative capability data from CapabilityRegistry.",
    ),
    # ── Memory / History information ─────────────────────────────────────────
    (
        "memory_information",
        [
            r"what (do you remember|memories do you have|have you (learned|stored|saved))",
            r"what('s| is) in (your )?(memory|memories|knowledge base|knowledge)",
            r"(recall|retrieve|find|search|show|list) (my |previous |stored |your )?(memories|information|context|history|knowledge)",
            r"what memories",
            r"memory (contents|list|search|retrieval)",
            r"search (my |your |the )?(memory|memories|knowledge|knowledge base)",
            r"what have you (learned|stored|remembered|saved)",
            r"previous (information|context|knowledge|history)",
            r"show (me |what you |all )?(remember|know|have learned|have stored)",
        ],
        "memory.retrieve",
        0.95,
        "Query requires memory retrieval from MemoryEngine.",
    ),
    # ── Repository / File information ────────────────────────────────────────
    (
        "repository_information",
        [
            # Explicit README / doc-file references
            r"\breadme\b",
            r"\blicense\b",
            r"\bchangelog\b",
            r"\bcontributing\b",
            # Verb + repository/file object
            r"(search|find|open|show|read|view|display|cat|get|fetch|summar(y|ize|ise)|explain|describe) (the |my |a |this )?(repo|repository|codebase|source|project) ?(file|readme|docs?)?",
            r"(search|find|open|show|read|view|display) (the |my |a |this )?file",
            r"(what|whats|what's) (in|inside) (the |my |this )?(repo|repository|readme|codebase|project)",
            r"(repo|repository|codebase|project) (structure|contents|files|readme|documentation)",
        ],
        "repository.read",
        0.95,
        "Query requires reading authoritative repository files (README/docs).",
    ),
]

# ---------------------------------------------------------------------------
# Non-grounding capability groups (supplemental)
# ---------------------------------------------------------------------------

_SUPPLEMENTAL_GROUPS: list[tuple[str, list[str], str, float, str]] = [
    (
        "web_search",
        [
            # Require an explicit web signal — bare "find"/"search" alone match
            # local queries ("find the bug", "search this list") and must NOT
            # imply a web search.
            r"\b(the )?(web|internet|online)\b",
            r"\b(google|bing|duckduckgo)\b",
            r"https?://|www\.",
            r"\b(url|website|web page|webpage)\b",
            r"\b(search|look up|lookup|browse|fetch|download)\b.*\b(web|internet|online|url|website|site|page)\b",
        ],
        "web.search",
        0.90,
        "Query implies searching the web.",
    ),
    (
        "code_execution",
        [
            r"\b(run|execute|evaluate)\b.*(code|script|python|program)",
            r"\b(python|script)\b.*(run|execute|eval)",
        ],
        "python.execute",
        0.88,
        "Query implies executing code.",
    ),
]

# Queries that should NOT trigger planner/executor (lightweight routing)
_CONVERSATIONAL_INTENTS = {
    IntentClass.conversation,
    IntentClass.unknown,
    IntentClass.retrieval,
    IntentClass.summarization,
}

# Grounding capabilities — never need planner/executor.
# Single source of truth in app/capabilities/core/grounding.py.
from app.capabilities.core.grounding import GROUNDING_CAPABILITY_IDS as _GROUNDING_CAP_IDS


def _matches_any(goal_lower: str, patterns: list[str]) -> bool:
    return any(re.search(p, goal_lower) for p in patterns)


class CapabilityEngine:
    """
    Semantic intent-driven capability planner.

    Priority order:
    1. Check all grounding groups — any that match produce a required
       grounding capability node.
    2. Check supplemental groups (web search, code execution).
    3. Only add planner/executor for complex non-grounding tasks.
    4. Always append runtime.generate as the terminal node.
    """

    def evaluate(
        self, goal: str, intent: IntentClass
    ) -> Tuple[List[CapabilityRecommendation], float]:
        recommendations: list[CapabilityRecommendation] = []
        goal_lower = goal.lower()
        triggered_grounding: list[str] = []

        # ── 1. Grounding groups ───────────────────────────────────────────────
        for group_name, patterns, cap_id, conf, reason in _GROUNDING_GROUPS:
            if _matches_any(goal_lower, patterns):
                triggered_grounding.append(cap_id)
                recommendations.append(
                    CapabilityRecommendation(
                        capability=cap_id,
                        confidence=conf,
                        priority="high",
                        reason=reason,
                        estimated_latency=5.0,
                        estimated_cost=0.0,
                        required=True,       # grounding is required — no hallucination fallback
                        parallelizable=True, # grounding nodes can run in parallel
                    )
                )

        # ── 2. Supplemental groups (only when no grounding triggered) ─────────
        if not triggered_grounding:
            for group_name, patterns, cap_id, conf, reason in _SUPPLEMENTAL_GROUPS:
                if _matches_any(goal_lower, patterns):
                    recommendations.append(
                        CapabilityRecommendation(
                            capability=cap_id,
                            confidence=conf,
                            priority="medium",
                            reason=reason,
                            estimated_latency=800.0,
                            estimated_cost=0.005,
                            required=False,
                            parallelizable=True,
                        )
                    )

        # ── 3. Planner/executor for genuinely complex non-grounding tasks ─────
        # Do NOT add planner/executor when:
        #   a) Grounding capabilities are present (short, fast registry lookups).
        #   b) Intent is conversational/unknown (simple Q&A doesn't need a plan).
        needs_planner = (
            not triggered_grounding
            and intent not in _CONVERSATIONAL_INTENTS
        )
        if needs_planner:
            recommendations.insert(
                0,
                CapabilityRecommendation(
                    capability="planner.plan",
                    confidence=1.0,
                    priority="critical",
                    reason="Required to orchestrate complex task execution.",
                    estimated_latency=1500.0,
                    estimated_cost=0.01,
                    required=True,
                    parallelizable=False,
                ),
            )
            recommendations.insert(
                1,
                CapabilityRecommendation(
                    capability="executor.execute",
                    confidence=1.0,
                    priority="critical",
                    reason="Required to execute the generated plan.",
                    estimated_latency=2000.0,
                    estimated_cost=0.0,
                    required=True,
                    parallelizable=False,
                ),
            )

        # ── 4. Terminal generation node ───────────────────────────────────────
        recommendations.append(
            CapabilityRecommendation(
                capability="runtime.generate",
                confidence=1.0,
                priority="critical",
                reason="Required to generate the final response.",
                estimated_latency=1000.0,
                estimated_cost=0.1,
                required=True,
                parallelizable=False,
            )
        )

        # Confidence: high when grounding triggered (deterministic),
        # moderate when supplemental, low when pure generation.
        if triggered_grounding:
            confidence = 0.97
        elif any(c.capability not in {"runtime.generate"} for c in recommendations):
            confidence = 0.85
        else:
            confidence = 0.70

        return recommendations, confidence
