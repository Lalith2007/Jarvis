from app.execution.manager import execution_manager
from app.execution.models import ExecutionContext
from app.mission.models import (
    Mission,
    MissionStatus,
)
from app.mission.builder import mission_graph_builder
from app.mission.engine import graph_execution_manager
from app.mission.service import mission_service
from app.tools.models import ToolResult


class MissionController:
    """
    Operating System Kernel of JARVIS.

    Every mission enters the backend here.

    The controller owns the lifecycle.

    It delegates planning and execution to the Pipeline.
    It does not perform them itself.
    """

    def create(
        self,
        goal: str,
        session_id: str | None = None,
    ) -> tuple[Mission, ExecutionContext]:

        from app.platform.publisher import EventPublisher

        mission = mission_service.create(goal)
        execution = execution_manager.create(goal)

        if session_id:
            execution.metadata["session_id"] = session_id

        mission_service.add_execution(
            mission,
            execution.mission_id,
        )
        mission.execution_id = execution.mission_id

        EventPublisher.publish(
            subsystem="mission",
            event_type="MissionCreated",
            mission_id=mission.id,
            session_id=session_id,
            execution_id=execution.mission_id,
            payload={"goal": goal},
        )

        return mission, execution

    def run(
        self,
        goal: str,
        session_id: str | None = None,
    ) -> tuple[ToolResult | None, ExecutionContext]:
        """
        Full mission lifecycle: create → analyze → route → plan → execute → complete.
        """

        from app.platform.publisher import EventPublisher

        mission, execution = self.create(goal, session_id=session_id)

        EventPublisher.publish(
            subsystem="mission",
            event_type="MissionStarted",
            mission_id=mission.id,
            session_id=session_id,
            execution_id=execution.mission_id,
        )

        # Transition to ANALYZING before the pipeline starts
        mission_service.update_status(mission, MissionStatus.ANALYZING)

        try:
            from app.runtime.service import runtime_service
            execution.runtime_session = runtime_service.create_session()
            
            graph = mission_graph_builder.build(mission)
            graph_execution_manager.execute(graph, mission.mission_id, session_id=session_id)
            
            result = None
            for node in graph.nodes.values():
                if node.capability == "executor.execute" and node.result is not None:
                    result = node.result
                    break
        except Exception as exc:
            print(f"DEBUG controller pipeline error: {exc}")
            import traceback
            traceback.print_exc()
            
            if hasattr(execution, "runtime_session") and execution.runtime_session:
                from app.runtime.service import runtime_service
                runtime_service.cleanup_session(execution.runtime_session)
                execution.runtime_session = None
            self.fail(
                mission,
                execution,
                response=f"Pipeline error: {exc}",
                session_id=session_id,
            )
            return None, execution

        # Result might be ToolResult or dict. Handle accordingly for response string.
        response = "Mission completed."
        if result is not None:
            if hasattr(result, "output"):
                response = result.output
            elif isinstance(result, dict) and "response" in result:
                response = result["response"]
            else:
                response = str(result)

        self.complete(
            mission,
            execution,
            response=response,
            session_id=session_id,
        )

        if hasattr(execution, "runtime_session") and execution.runtime_session:
            from app.runtime.service import runtime_service
            runtime_service.cleanup_session(execution.runtime_session)
            execution.runtime_session = None

        return result, execution

    def complete(
        self,
        mission: Mission,
        execution: ExecutionContext,
        response: str,
        session_id: str | None = None,
    ) -> None:

        from app.platform.publisher import EventPublisher

        execution_manager.complete(execution)

        mission_service.complete(
            mission,
            response=response,
        )

        EventPublisher.publish(
            subsystem="mission",
            event_type="MissionCompleted",
            mission_id=mission.id,
            session_id=session_id,
            execution_id=execution.mission_id,
            payload={"response": response[:200]},
        )

    def fail(
        self,
        mission: Mission,
        execution: ExecutionContext,
        response: str,
        session_id: str | None = None,
    ) -> None:

        from app.platform.publisher import EventPublisher

        execution_manager.fail(execution)

        mission_service.fail(
            mission,
            response=response,
        )

        EventPublisher.publish(
            subsystem="mission",
            event_type="MissionFailed",
            mission_id=mission.id,
            session_id=session_id,
            execution_id=execution.mission_id,
            severity="error",
            payload={"response": response},
        )


mission_controller = MissionController()
