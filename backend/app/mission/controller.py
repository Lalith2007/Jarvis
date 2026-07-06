import logging

from app.capabilities.core.grounding import GROUNDING_CAPABILITY_IDS
from app.execution.manager import execution_manager
from app.execution.models import ExecutionContext
from app.mission.graph import NodeStatus
from app.mission.models import (
    Mission,
    MissionStatus,
)
from app.mission.builder import mission_graph_builder
from app.mission.engine import graph_execution_manager
from app.mission.service import mission_service
from app.tools.models import ToolResult

logger = logging.getLogger(__name__)


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
        stream: bool = False,
    ) -> tuple[ToolResult | None, ExecutionContext]:
        """
        Full mission lifecycle: create → analyze → route → plan → execute → complete.
        """

        from app.platform.publisher import EventPublisher

        mission, execution = self.create(goal, session_id=session_id)
        mission.metadata["stream"] = stream

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
                if node.capability == "runtime.generate" and node.result is not None:
                    result = node.result
                    break

            # Fallback if no runtime.generate (shouldn't happen in 12.7)
            if result is None:
                for node in graph.nodes.values():
                    if node.capability == "executor.execute" and node.result is not None:
                        result = node.result
                        break

            # Grounding guarantee: if runtime.generate never produced output
            # because a required grounding capability failed, return an explicit
            # refusal instead of a silent "Mission completed." — never fabricate.
            if result is None:
                grounding_failure = self._grounding_failure_message(graph)
                if grounding_failure:
                    tool_result_obj = ToolResult(
                        success=False, output=grounding_failure
                    )
                    self.complete(
                        mission,
                        execution,
                        response=grounding_failure,
                        session_id=session_id,
                    )
                    if getattr(execution, "runtime_session", None):
                        from app.runtime.service import runtime_service
                        runtime_service.cleanup_session(execution.runtime_session)
                        execution.runtime_session = None
                    return tool_result_obj, execution
        except Exception as exc:
            logger.exception("Mission pipeline error: %s", exc)

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

        # `result` is the UNWRAPPED capability payload (CapabilityManager.execute
        # returns result.result), so runtime.generate yields either a plain
        # string (non-stream) or a StreamResult dict {"stream_id", "is_stream"}.
        response = "Mission completed."
        tool_result_obj = None
        if result is not None:
            if isinstance(result, dict) and result.get("is_stream"):
                # Streaming: preserve the stream metadata so Hermes can consume it.
                tool_result_obj = ToolResult(
                    success=True, output="<stream>", metadata=result
                )
            elif isinstance(result, dict) and "response" in result:
                response = result["response"]
                tool_result_obj = ToolResult(success=True, output=response)
            elif hasattr(result, "output"):
                response = result.output
                tool_result_obj = (
                    result
                    if isinstance(result, ToolResult)
                    else ToolResult(
                        success=getattr(result, "success", True), output=response
                    )
                )
            elif hasattr(result, "result"):
                res_val = result.result
                response = str(res_val)
                tool_result_obj = ToolResult(
                    success=getattr(result, "success", True), output=response
                )
            else:
                response = str(result)
                tool_result_obj = ToolResult(success=True, output=response)

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

        return tool_result_obj, execution

    def _grounding_failure_message(self, graph) -> str | None:
        """
        If a required grounding capability failed or was cancelled (so
        runtime.generate never produced grounded output), return an explicit
        refusal listing the sources that could not be retrieved.  Returns None
        when there is no grounding failure to report.
        """
        failed = [
            node.capability
            for node in graph.nodes.values()
            if node.capability in GROUNDING_CAPABILITY_IDS
            and node.status in (NodeStatus.FAILED, NodeStatus.CANCELLED)
        ]
        if not failed:
            return None
        return (
            "I was unable to retrieve the authoritative system information "
            "required to answer this question. The following data sources did "
            f"not return results: {', '.join(sorted(set(failed)))}. "
            "I will not fabricate this information from prior knowledge."
        )

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
