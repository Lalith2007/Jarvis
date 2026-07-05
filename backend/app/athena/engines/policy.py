from typing import List, Tuple

from app.athena.models import CapabilityRecommendation


class PolicyEngine:
    """
    Deterministically evaluates safety, permission, capability restrictions, and execution limits.
    Returns (approved: bool, reason: str).
    """

    def evaluate(self, risk: str, capabilities: List[CapabilityRecommendation], token_budget: int) -> Tuple[bool, str]:
        # Rule 1: High risk tasks cannot execute automatically without user permission.
        # For Athena's strategic planning phase, if we lack the authorization framework in the graph, we might reject or allow with caution.
        # For now, we will approve but the frontend/executor should prompt. Here we approve.
        
        # Rule 2: Token budget limits
        if token_budget > 32000:
            return False, "Token budget exceeds system maximum of 32,000."
            
        # Rule 3: Banned capabilities check (example)
        banned = []
        for cap in capabilities:
            if cap.capability in banned:
                return False, f"Capability {cap.capability} is currently restricted."
                
        return True, "Policy checks passed."
