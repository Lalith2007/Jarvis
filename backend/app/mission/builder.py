import uuid
from typing import List

from app.agents.hermes.models import PromptContext
from app.athena.engines.orchestrator import athena
from app.mission.graph import MissionGraph, MissionNode, NodeStatus, NodeType
from app.mission.models import Mission
from app.athena.models import AthenaDecision


class MissionGraphBuilder:
    """
    Constructs the Mission Execution Graph dynamically from a given Mission,
    driven strictly by the AthenaDecision.
    """
    
    def build(self, mission: Mission) -> MissionGraph:
        graph_id = mission.graph_id or str(uuid.uuid4())
        
        # Shared configuration
        base_payload = {
            "mission_id": mission.mission_id,
            "execution_id": mission.execution_id,
            "goal": mission.goal,
        }
        
        # 1. Invoke Athena Orcherstrator for Strategic Planning
        context = PromptContext(
            mission_id=mission.mission_id,
            goal=mission.goal,
            system_prompt="You are Athena Intelligence Engine.",
            user_query=mission.goal,
        )
        decision: AthenaDecision = athena.analyze(context)
        
        # 2. Enforce Policy Engine Decision
        # If policy rejected it, recommended_capabilities is empty, so graph will be empty or fail.
        
        nodes = {}
        node_counter = 1
        
        def create_node(capability: str, node_type: NodeType, deps: List[str], metadata: dict = None) -> MissionNode:
            nonlocal node_counter
            node_id = f"node_{graph_id}_{node_counter}"
            node_counter += 1
            node = MissionNode(
                id=node_id,
                type=node_type,
                capability=capability,
                payload=base_payload.copy(),
                dependencies=deps,
                metadata=metadata or {}
            )
            nodes[node_id] = node
            return node
            
        last_deps = []
        
        # Add pre-planning nodes (e.g. Memory Retrieval)
        if decision.requires_memory and decision.memory_plan.retrieval_required:
            mem_node = create_node("memory.retrieve", NodeType.MEMORY, [])
            last_deps = [mem_node.id]
            
        # Add Capability Nodes (Planning, Execution)
        for cap in decision.recommended_capabilities:
            node_type = NodeType.TOOL
            if cap.capability == "planner.plan":
                node_type = NodeType.PLANNER
                
            node = create_node(
                capability=cap.capability, 
                node_type=node_type, 
                deps=last_deps.copy(),
                metadata={"budget": decision.latency_budget_ms}
            )
            
            # If sequential, this node becomes the dependency for the next
            if not decision.requires_parallel_execution or cap.capability == "planner.plan":
                last_deps = [node.id]
            else:
                # If parallel, they all depend on the previous stage, and the next stage depends on all of them
                # (Assuming simple fork-join for now)
                last_deps.append(node.id)
                
        # We need a predictable executor node ID for controller.py backwards compatibility.
        # controller.py expects the final result to be from `f"node_{graph_id}_4"` usually.
        # Wait, if we change node IDs, we must change controller.py to find the right node!
        
        # Add Reflection Node
        if decision.requires_reflection:
            reflect_node = create_node("mission.reflect", NodeType.AGGREGATOR, last_deps.copy())
            last_deps = [reflect_node.id]
            
        return MissionGraph(
            graph_id=graph_id,
            nodes=nodes,
        )

mission_graph_builder = MissionGraphBuilder()
