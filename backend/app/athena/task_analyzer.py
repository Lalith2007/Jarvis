from app.agents.hermes.models import PromptContext
from app.athena.intent import IntentResult
from app.athena.task_analysis import (
    ContextRequirement,
    TaskAnalysis,
    TaskComplexity,
)


class AthenaTaskAnalyzer:
    """
    Analyzes the characteristics of a task.

    This module consumes an already-computed IntentResult
    and produces a model-independent TaskAnalysis.
    """

    def analyze(
        self,
        context: PromptContext,
        intent: IntentResult,
    ) -> TaskAnalysis:

        query = context.user_query.lower()

        word_count = len(query.split())
        capability_count = len(intent.intents)

        # -----------------------------------------
        # Complexity
        # -----------------------------------------

        if capability_count >= 5 or word_count >= 60:
            complexity = TaskComplexity.EXPERT

        elif capability_count >= 4 or word_count >= 35:
            complexity = TaskComplexity.COMPLEX

        elif capability_count >= 3 or word_count >= 20:
            complexity = TaskComplexity.MODERATE

        elif capability_count >= 2 or word_count >= 8:
            complexity = TaskComplexity.SIMPLE

        else:
            complexity = TaskComplexity.TRIVIAL

        # -----------------------------------------
        # Context Requirement
        # -----------------------------------------

        if word_count >= 100:
            context = ContextRequirement.VERY_LARGE

        elif word_count >= 40:
            context = ContextRequirement.LARGE

        elif word_count >= 15:
            context = ContextRequirement.MEDIUM

        else:
            context = ContextRequirement.SMALL

        # -----------------------------------------
        # Tool Detection
        # -----------------------------------------

        requires_tools = any(
            word in query
            for word in [
                "terminal",
                "bash",
                "shell",
                "git",
                "docker",
                "file",
                "folder",
                "directory",
                "create",
                "delete",
                "rename",
                "move",
                "copy",
                "execute",
                "run",
            ]
        )

        # -----------------------------------------
        # Memory Detection
        # -----------------------------------------

        requires_memory = any(
            word in query
            for word in [
                "remember",
                "memory",
                "vault",
                "previous",
                "conversation",
                "history",
            ]
        )

        requires_reasoning = (
            complexity >= TaskComplexity.MODERATE
        )

        requires_multimodel = (
            complexity >= TaskComplexity.COMPLEX
        )

        latency_priority = (
            100
            if complexity <= TaskComplexity.SIMPLE
            else 50
        )

        cost_priority = (
            50
            if requires_multimodel
            else 100
        )

        return TaskAnalysis(
            complexity=complexity,
            context_requirement=context,
            requires_tools=requires_tools,
            requires_memory=requires_memory,
            requires_reasoning=requires_reasoning,
            requires_multimodel=requires_multimodel,
            latency_priority=latency_priority,
            cost_priority=cost_priority,
        )


task_analyzer = AthenaTaskAnalyzer()
