import re
from typing import Tuple

from app.athena.models import IntentClass, MemoryPlan, MemoryStrategy


class MemoryEngine:
    """
    Deterministically creates a memory plan based on intent and goal.
    Returns (MemoryPlan, confidence_score).
    """

    def evaluate(self, goal: str, intent: IntentClass) -> Tuple[MemoryPlan, float]:
        goal_lower = goal.lower()
        
        # Default to working memory
        plan = MemoryPlan(
            strategy=MemoryStrategy.working,
            retrieval_required=False,
            write_required=False,
            reflection_required=False,
            expected_memories=0,
            retrieval_budget=0.0
        )
        confidence = 0.90
        
        # Check for explicit memory keywords — extended to cover all Sprint 12.9 variants
        needs_retrieval = bool(re.search(
            r"\b(remember|recall|previous|last time|history|context|memories|"
            r"learned|stored|knowledge base|what do you know|what have you|"
            r"search memory|memory search|retrieve memory)\b",
            goal_lower,
        ))
        needs_storage = bool(re.search(r"\b(save|store|remember this|keep track)\b", goal_lower))
        
        if needs_retrieval and needs_storage:
            plan.strategy = MemoryStrategy.combined
            plan.retrieval_required = True
            plan.write_required = True
            plan.expected_memories = 5
            plan.retrieval_budget = 50.0
            confidence = 0.95
        elif needs_retrieval:
            plan.strategy = MemoryStrategy.semantic
            plan.retrieval_required = True
            plan.expected_memories = 3
            plan.retrieval_budget = 30.0
            confidence = 0.95
        elif needs_storage:
            plan.strategy = MemoryStrategy.episodic
            plan.write_required = True
            confidence = 0.95
        elif intent == IntentClass.conversation:
            plan.strategy = MemoryStrategy.episodic
            plan.retrieval_required = True
            plan.expected_memories = 10
            plan.retrieval_budget = 20.0
        elif intent == IntentClass.coding or intent == IntentClass.planning:
            plan.strategy = MemoryStrategy.working
            plan.reflection_required = True
            
        return plan, confidence
