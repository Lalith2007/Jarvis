import re
from typing import List, Tuple

from app.athena.models import CapabilityRecommendation, IntentClass


class CapabilityEngine:
    """
    Deterministically selects required capabilities based on intent and goal.
    Returns (List[CapabilityRecommendation], confidence_score).
    """

    def evaluate(self, goal: str, intent: IntentClass) -> Tuple[List[CapabilityRecommendation], float]:
        recommendations = []
        goal_lower = goal.lower()
        confidence = 0.90
        
        # Core planner is almost always required for complex tasks
        needs_planner = intent not in [IntentClass.conversation, IntentClass.unknown]
        
        if needs_planner:
            recommendations.append(
                CapabilityRecommendation(
                    capability="planner.plan",
                    confidence=1.0,
                    priority="critical",
                    reason="Required to orchestrate task execution.",
                    estimated_latency=1500.0,
                    estimated_cost=0.01,
                    required=True,
                    parallelizable=False
                )
            )
            # If there's a planner, there's usually an executor
            recommendations.append(
                CapabilityRecommendation(
                    capability="executor.execute",
                    confidence=1.0,
                    priority="critical",
                    reason="Required to execute the generated plan.",
                    estimated_latency=2000.0,
                    estimated_cost=0.0,
                    required=True,
                    parallelizable=False
                )
            )

        # File system heuristics
        if re.search(r"\b(file|directory|folder|read|write|save|open)\b", goal_lower):
            recommendations.append(
                CapabilityRecommendation(
                    capability="filesystem.read",
                    confidence=0.85,
                    priority="high",
                    reason="Goal implies reading files.",
                    estimated_latency=10.0,
                    estimated_cost=0.0,
                    required=False,
                    parallelizable=True
                )
            )
            
        # Web heuristics
        if re.search(r"\b(search|web|browser|url|http|download)\b", goal_lower):
            recommendations.append(
                CapabilityRecommendation(
                    capability="web.search",
                    confidence=0.95,
                    priority="high",
                    reason="Goal implies searching the web.",
                    estimated_latency=800.0,
                    estimated_cost=0.005,
                    required=False,
                    parallelizable=True
                )
            )

        # Python execution heuristics
        if intent == IntentClass.coding or re.search(r"\b(python|script|run|execute)\b", goal_lower):
            recommendations.append(
                CapabilityRecommendation(
                    capability="python.execute",
                    confidence=0.90,
                    priority="medium",
                    reason="Goal implies running code.",
                    estimated_latency=500.0,
                    estimated_cost=0.0,
                    required=False,
                    parallelizable=False
                )
            )

        # Adjust confidence if no specific capabilities found besides core
        if not recommendations:
            confidence = 0.50  # We don't know what to do, might need LLM

        return recommendations, confidence
