from typing import Any

from app.mission.graph import MissionNode
from app.capabilities.registry import capability_registry
from app.capabilities.executor import capability_lifecycle
from app.capabilities.core.models import CapabilityContext


class CapabilityManager:
    """
    CapabilityManager acts as the primary facade for executing any
    capability in the system. It constructs the capability context
    and delegates to the CapabilityRegistry & Lifecycle engine.
    """
    
    def __init__(self):
        # Ensure built-ins are registered when the manager is initialized
        from app.capabilities.builtin import register_builtins
        register_builtins()

    def execute(self, node: MissionNode) -> Any:
        # Retrieve the abstract capability by node.capability
        capability = capability_registry.get(node.capability)
        
        # Build standard CapabilityContext
        mission_id = node.metadata.get("mission_id") or node.payload.get("mission_id", "")
        execution_id = node.metadata.get("execution_id") or node.payload.get("execution_id", "")
        
        # We place node payload into runtime_state so capabilities have access to what they need
        runtime_state = dict(node.payload)
        # Some legacy capabilities look at context.runtime_state.get("goal") instead of node.payload
        if "goal" not in runtime_state and node.metadata.get("goal"):
             runtime_state["goal"] = node.metadata.get("goal")

        raw_budget = node.metadata.get("budget", {})
        resource_budget = raw_budget if isinstance(raw_budget, dict) else {"latency_budget_ms": raw_budget}

        context = CapabilityContext(
            mission_id=mission_id,
            graph_id=node.metadata.get("graph_id", ""),
            execution_id=execution_id,
            node_id=node.id,
            athena_decision=None,
            memory_plan=None,
            resource_budget=resource_budget,
            runtime_state=runtime_state,
            approved_resources=[]
        )
        
        # Execute the capability strictly through the lifecycle
        result = capability_lifecycle.execute(capability, context)
        
        if result.success:
            return result.result
        else:
            raise Exception(f"Capability {node.capability} failed: {result.errors}")


capability_manager = CapabilityManager()
