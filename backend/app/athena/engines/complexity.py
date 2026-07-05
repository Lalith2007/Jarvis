import re
from typing import Tuple

from app.athena.models import ComplexityClass


class ComplexityEngine:
    """
    Deterministically estimates the complexity of a mission goal.
    Returns (ComplexityClass, confidence_score).
    """

    def evaluate(self, goal: str) -> Tuple[ComplexityClass, float]:
        goal_lower = goal.lower()
        length = len(goal)
        words = len(goal.split())
        
        # Heuristics for complexity indicators
        expert_keywords = [r"architect", r"system", r"end-to-end", r"full stack", r"production", r"design"]
        high_keywords = [r"refactor", r"optimize", r"integrate", r"pipeline", r"database", r"api"]
        medium_keywords = [r"create", r"build", r"write", r"script", r"generate", r"analyze", r"update"]
        
        expert_matches = sum(1 for kw in expert_keywords if re.search(kw, goal_lower))
        high_matches = sum(1 for kw in high_keywords if re.search(kw, goal_lower))
        medium_matches = sum(1 for kw in medium_keywords if re.search(kw, goal_lower))
        
        # Rules based on word count, length, and keywords
        if expert_matches > 0 or (words > 50 and high_matches > 0):
            return ComplexityClass.expert, 0.85
            
        if high_matches > 0 or words > 30:
            return ComplexityClass.high, 0.85
            
        if medium_matches > 0 or words > 15:
            return ComplexityClass.medium, 0.90
            
        if words > 5:
            return ComplexityClass.low, 0.95
            
        return ComplexityClass.trivial, 0.98
