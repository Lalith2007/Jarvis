import uuid
from app.mission.graph import MissionGraph, MissionNode, NodeStatus, NodeType
from app.mission.models import Mission

class MissionGraphBuilder:
    """
    Constructs the Mission Execution Graph from a given Mission.
    For Sprint 12.1, it builds the legacy sequence as a generic DAG:
    Analyzer -> Router -> Planner -> Executor -> Reflector.
    """
    
    def build(self, mission: Mission) -> MissionGraph:
        graph_id = mission.graph_id or str(uuid.uuid4())
        
        # Shared configuration
        base_payload = {
            "mission_id": mission.mission_id,
            "execution_id": mission.execution_id,
            "goal": mission.goal,
        }
        
        # Node 1: Analyzer
        analyzer = MissionNode(
            id=f"node_{graph_id}_1",
            type=NodeType.RUNTIME,
            capability="mission.analyze",
            payload=base_payload,
        )
        
        # Node 2: Router (depends on analyzer)
        router = MissionNode(
            id=f"node_{graph_id}_2",
            type=NodeType.AGGREGATOR,
            capability="athena.route",
            payload=base_payload,
            dependencies=[analyzer.id],
        )
        
        # Node 3: Planner (depends on router)
        planner = MissionNode(
            id=f"node_{graph_id}_3",
            type=NodeType.PLANNER,
            capability="planner.plan",
            payload=base_payload,
            dependencies=[router.id],
        )
        
        # Node 4: Executor (depends on planner)
        executor = MissionNode(
            id=f"node_{graph_id}_4",
            type=NodeType.TOOL,
            capability="executor.execute",
            payload=base_payload,
            dependencies=[planner.id],
        )
        
        # Node 5: Reflector (depends on executor)
        reflector = MissionNode(
            id=f"node_{graph_id}_5",
            type=NodeType.AGGREGATOR,
            capability="mission.reflect",
            payload=base_payload,
            dependencies=[executor.id],
        )
        
        nodes = {
            analyzer.id: analyzer,
            router.id: router,
            planner.id: planner,
            executor.id: executor,
            reflector.id: reflector
        }
        
        return MissionGraph(
            graph_id=graph_id,
            nodes=nodes,
        )

mission_graph_builder = MissionGraphBuilder()
