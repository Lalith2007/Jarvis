from typing import Any

from app.mission.graph import MissionNode
from app.mission.registry import capability_registry


class CapabilityManager:
    """
    CapabilityManager acts as the primary facade for executing any
    capability in the system. It delegates strictly to the CapabilityRegistry,
    ensuring that the execution engine never knows about specific node types.
    """
    
    def execute(self, node: MissionNode) -> Any:
        return capability_registry.execute(node)

capability_manager = CapabilityManager()

# ---------------------------------------------------------
# Default Capability Registrations
# ---------------------------------------------------------

def execute_analyzer(node: MissionNode) -> Any:
    from app.capabilities.service import capability_service
    from app.execution.manager import execution_manager
    from app.mission.service import mission_service
    
    mission_id = node.metadata.get("mission_id") or node.payload.get("mission_id")
    execution_id = node.metadata.get("execution_id") or node.payload.get("execution_id")
    if not mission_id or not execution_id:
        return None
        
    mission = mission_service.get(mission_id)
    execution = execution_manager.get(execution_id)
    
    if mission and execution:
        capability_service.evaluate_mission(mission, execution)
    return None

def execute_router(node: MissionNode) -> Any:
    from app.athena.router import athena
    from app.llm.prompts.loader import prompt_loader
    from app.agents.hermes.models import PromptContext
    from app.execution.manager import execution_manager
    
    payload = node.payload
    mission_id = payload.get("mission_id")
    execution_id = payload.get("execution_id")
    goal = payload.get("goal")
    
    context = PromptContext(
        system_prompt=prompt_loader.load("system.md"),
        user_query=goal,
        metadata={
            "mission_id": mission_id,
            "stage": "routing",
        },
    )
    
    decision = athena.route(context)
    
    execution = execution_manager.get(execution_id) if execution_id else None
    if execution:
        execution.metadata["athena_primary"] = decision.primary.value
        execution.metadata["athena_reason"] = decision.reason
        
    return {
        "primary_model": decision.primary.value,
        "reason": decision.reason
    }

def execute_planner(node: MissionNode) -> Any:
    from app.planner.service import planner
    
    goal = node.payload.get("goal")
    plan = planner.plan(goal)
    
    return plan

def execute_tool(node: MissionNode) -> Any:
    from app.executor.service import executor
    from app.execution.manager import execution_manager
    
    plan = node.payload.get("planner.plan")
    execution_id = node.metadata.get("execution_id") or node.payload.get("execution_id")
    execution = execution_manager.get(execution_id) if execution_id else None
    
    print(f"DEBUG execute_tool: plan={plan}, execution_id={execution_id}, execution={execution}")
    if execution and plan:
        result = executor.execute(plan, execution)
        return result
    return None

def execute_reflector(node: MissionNode) -> Any:
    # Reflection placeholder
    return {"status": "reflected"}


# Register legacy pipeline capabilities
capability_registry.register("mission.analyze", execute_analyzer)
capability_registry.register("athena.route", execute_router)
capability_registry.register("planner.plan", execute_planner)
capability_registry.register("executor.execute", execute_tool)
capability_registry.register("mission.reflect", execute_reflector)
