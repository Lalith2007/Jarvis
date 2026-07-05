import re
from typing import Tuple

from app.athena.models import IntentClass


class IntentEngine:
    """
    Deterministically classifies the intent of a mission goal.
    Returns (IntentClass, confidence_score).
    """

    def __init__(self):
        # Heuristic keywords for intent classification
        self.heuristics = {
            IntentClass.coding: [
                r"\b(code|function|script|refactor|debug|compile|build|repo|git)\b",
                r"\b(python|javascript|typescript|java|c\+\+|rust|go)\b",
            ],
            IntentClass.research: [
                r"\b(research|find|search|lookup|investigate|explore|learn about)\b",
            ],
            IntentClass.planning: [
                r"\b(plan|schedule|organize|strategy|architect|design)\b",
            ],
            IntentClass.automation: [
                r"\b(automate|workflow|trigger|cron|background task|deploy)\b",
            ],
            IntentClass.retrieval: [
                r"\b(get|fetch|download|pull|retrieve|read)\b",
            ],
            IntentClass.summarization: [
                r"\b(summarize|tldr|tl;dr|brief|recap|summary)\b",
            ],
            IntentClass.analysis: [
                r"\b(analyze|evaluate|assess|compare|metrics|statistics)\b",
            ],
            IntentClass.generation: [
                r"\b(generate|create|write|draft|compose|make)\b",
            ],
            IntentClass.multimodal: [
                r"\b(image|picture|photo|video|audio|voice|listen|see)\b",
            ],
            IntentClass.conversation: [
                r"^(hi|hello|hey|greetings|how are you|good morning|good evening)",
                r"\b(talk|chat|discuss|speak)\b",
            ],
        }

    def evaluate(self, goal: str) -> Tuple[IntentClass, float]:
        """
        Evaluate the goal against heuristics.
        Returns the intent and a confidence score.
        """
        goal_lower = goal.lower()
        
        matches = {}
        total_matches = 0
        
        for intent, patterns in self.heuristics.items():
            count = 0
            for pattern in patterns:
                if re.search(pattern, goal_lower):
                    count += 1
            if count > 0:
                matches[intent] = count
                total_matches += count
                
        if not matches:
            return IntentClass.unknown, 0.0
            
        # Determine the primary intent
        best_intent = max(matches.items(), key=lambda x: x[1])[0]
        
        # Calculate confidence based on the strength of the match
        # If one intent dominates, confidence is higher.
        confidence = matches[best_intent] / total_matches
        
        # Boost confidence slightly if the match is strong (e.g., > 1 keyword)
        if matches[best_intent] > 1:
            confidence = min(1.0, confidence + 0.2)
            
        return best_intent, confidence
