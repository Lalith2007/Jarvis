import re

from pydantic import BaseModel, Field

from app.agents.hermes.models import PromptContext
from app.athena.capabilities import Capability


class IntentScore(BaseModel):
    """
    Represents a single detected user intent.
    """

    capability: Capability

    score: int

    confidence: float

    matched_keywords: list[str] = Field(default_factory=list)


class IntentResult(BaseModel):
    """
    Complete result from the intent engine.
    """

    intents: list[IntentScore] = Field(default_factory=list)

    reasons: list[str] = Field(default_factory=list)


class AthenaIntentEngine:
    """
    Rule-based intent detector.

    Future versions may use an LLM classifier while
    keeping the same interface.
    """

    KEYWORDS = {
        Capability.CODING: {
            "python": 40,
            "java": 35,
            "javascript": 35,
            "typescript": 35,
            "c": 25,
            "c++": 30,
            "c#": 30,
            "go": 30,
            "rust": 30,
            "swift": 30,
            "kotlin": 30,
            "php": 25,
            "ruby": 25,
            "sql": 30,
            "fastapi": 35,
            "django": 35,
            "flask": 30,
            "react": 30,
            "docker": 30,
            "backend": 20,
            "frontend": 20,
            "api": 20,
            "code": 15,
            "coding": 15,
            "bug": 25,
            "debug": 30,
            "error": 20,
            "fix": 20,
        },

        Capability.PLANNING: {
            "plan": 30,
            "planning": 35,
            "roadmap": 35,
            "strategy": 35,
            "architecture": 30,
            "design": 25,
            "workflow": 25,
            "decision": 25,
            "compare": 20,
        },

        Capability.RESEARCH: {
            "research": 40,
            "paper": 35,
            "study": 35,
            "literature": 40,
            "survey": 30,
            "analyse": 25,
            "analyze": 25,
        },

        Capability.DOCUMENTS: {
            "pdf": 40,
            "document": 30,
            "report": 30,
            "summary": 25,
            "summarize": 25,
            "notes": 20,
            "book": 20,
            "chapter": 20,
        },

        Capability.KNOWLEDGE: {
            "obsidian": 40,
            "vault": 35,
            "memory": 30,
            "knowledge": 25,
        },

        Capability.BUSINESS: {
            "business": 40,
            "startup": 40,
            "company": 30,
            "marketing": 25,
            "sales": 25,
            "product": 25,
            "pricing": 25,
            "growth": 25,
        },

        Capability.FINANCE: {
            "finance": 40,
            "investment": 35,
            "invest": 30,
            "budget": 25,
            "portfolio": 30,
            "cashflow": 30,
        },

        Capability.TRADING: {
            "trading": 40,
            "stocks": 35,
            "crypto": 35,
            "forex": 35,
            "options": 30,
            "swing": 25,
            "intraday": 25,
        },

        Capability.MONEY: {
            "money": 40,
            "income": 35,
            "earn": 35,
            "earning": 35,
            "profit": 30,
            "revenue": 30,
            "freelance": 25,
            "youtube": 25,
            "saas": 30,
        },

        Capability.EXECUTION: {
            "build": 35,
            "implement": 35,
            "develop": 30,
            "deploy": 30,
            "execute": 25,
            "run": 20,
            "create": 20,
            "automate": 30,
        },

        Capability.WRITING: {
            "write": 35,
            "email": 30,
            "essay": 30,
            "article": 30,
            "blog": 30,
            "proposal": 30,
            "rewrite": 25,
        },

        Capability.CONVERSATION: {
            "hello": 20,
            "hi": 20,
            "hey": 20,
            "chat": 20,
            "talk": 20,
            "thanks": 20,
        },

        Capability.TOOL_USAGE: {
            "terminal": 35,
            "bash": 30,
            "shell": 30,
            "git": 25,
            "github": 25,
            "command": 20,
            "tool": 20,
            "file": 15,
        },
    }

    def detect(
        self,
        context: PromptContext,
    ) -> IntentResult:

        query = context.user_query.lower()

        words = set(
            re.findall(
                r"\b[\w#+]+\b",
                query,
            )
        )

        result = IntentResult()

        for capability, keyword_map in self.KEYWORDS.items():

            score = 0
            matched = []

            for keyword, weight in keyword_map.items():

                if keyword in words:
                    score += weight
                    matched.append(keyword)

            if score == 0:
                continue

            score = min(score, 100)

            confidence = min(score / 100.0, 1.0)

            result.intents.append(
                IntentScore(
                    capability=capability,
                    score=score,
                    confidence=confidence,
                    matched_keywords=sorted(matched),
                )
            )

            result.reasons.append(
                f"{capability.value}: {', '.join(sorted(matched))}"
            )

        # -------------------------------------------------
        # Default intent
        #
        # If nothing matches, assume a general conversation.
        # -------------------------------------------------

        if not result.intents:
            result.intents.append(
                IntentScore(
                    capability=Capability.CONVERSATION,
                    score=100,
                    confidence=1.0,
                    matched_keywords=[],
                )
            )

            result.reasons.append(
                "Defaulted to conversation."
            )

        result.intents.sort(
            key=lambda intent: intent.score,
            reverse=True,
        )

        return result


intent_engine = AthenaIntentEngine()
