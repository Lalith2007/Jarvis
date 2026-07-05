import re
from typing import Tuple

from app.athena.models import ComplexityClass, IntentClass


class RiskEngine:
    """
    Deterministically evaluates the risk level of a mission goal.
    Returns (risk_level, confidence_score).
    """

    def evaluate(self, goal: str, intent: IntentClass, complexity: ComplexityClass) -> Tuple[str, float]:
        goal_lower = goal.lower()
        
        # High risk heuristics
        high_risk_keywords = [
            r"\b(delete|remove|destroy|drop|format|rm -rf|sudo)\b",
            r"\b(production|prod|live)\b",
            r"\b(password|secret|key|token|credential)\b"
        ]
        
        # Medium risk heuristics
        medium_risk_keywords = [
            r"\b(update|modify|change|edit|overwrite|deploy|push)\b"
        ]
        
        high_risk_matches = sum(1 for kw in high_risk_keywords if re.search(kw, goal_lower))
        medium_risk_matches = sum(1 for kw in medium_risk_keywords if re.search(kw, goal_lower))
        
        if high_risk_matches > 0:
            return "high", 0.95
            
        if intent in [IntentClass.coding, IntentClass.automation] and complexity in [ComplexityClass.high, ComplexityClass.expert]:
            return "high", 0.85
            
        if medium_risk_matches > 0:
            return "medium", 0.90
            
        if intent in [IntentClass.coding, IntentClass.automation]:
            return "medium", 0.80
            
        return "low", 0.95
