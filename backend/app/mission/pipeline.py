import time
from app.execution.models import ExecutionContext
from app.executor.service import executor
from app.mission.models import Mission, MissionStatus
from app.mission.context import MissionContext
from app.planner.service import planner
from app.platform.publisher import EventPublisher
from app.platform.observability import TimingScope
from app.tools.models import ToolResult


class MissionPipeline:
    """
    Canonical execution pipeline for JARVIS.

    Every mission executes through this pipeline.

    Order:
      analyze → route (Athena) → plan → execute → reflect

    The pipeline owns execution order.
    Individual subsystems own implementation.
    """

    def run(
        self,
        mission: Mission = None,
        execution: ExecutionContext = None,
        mission_context: MissionContext = None,
    ) -> ToolResult | None:
        if mission_context:
            mission = mission_context.mission
            execution = mission_context.execution
        elif mission and execution:
            # Fallback wrapper
            mission_context = MissionContext(
                request_id=execution.metadata.get("request_id", ""),
                session_id=execution.metadata.get("session_id", ""),
                mission=mission,
                execution=execution
            )
        else:
            raise ValueError("Must provide either mission_context or both mission and execution")

        self.analyze(mission, execution, mission_context)

        from app.runtime.service import runtime_service
        execution.runtime_session = runtime_service.create_session()

        self.route(mission, execution, mission_context)

        plan = self.plan(mission, execution, mission_context)

        if not plan.use_tool:
            if execution.runtime_session:
                from app.runtime.service import runtime_service
                runtime_service.cleanup_session(execution.runtime_session)
                execution.runtime_session = None
            return None

        result = self.execute(mission, execution, plan, mission_context)

        self.reflect(mission, execution, mission_context)

        if execution.runtime_session:
            from app.runtime.service import runtime_service
            runtime_service.cleanup_session(execution.runtime_session)
            execution.runtime_session = None

        return result

    # ──────────────────────────────────────────────────────────────────

    def analyze(
        self,
        mission: Mission,
        execution: ExecutionContext,
        mission_context: MissionContext = None,
    ) -> None:
        """
        Evaluate capabilities required for this mission.
        """
        from app.capabilities.service import capability_service

        capability_service.evaluate_mission(mission, execution)

    def route(
        self,
        mission: Mission,
        execution: ExecutionContext,
        mission_context: MissionContext = None,
    ) -> None:
        """
        Athena model-routing step.

        Builds a minimal PromptContext from the mission goal and routes
        through Athena to determine the optimal model.  The decision is
        stored in execution.metadata so later steps can use it.
        """
        try:
            from app.agents.hermes.models import PromptContext
            from app.athena.router import athena
            from app.llm.prompts.loader import prompt_loader

            context = PromptContext(
                system_prompt=prompt_loader.load("system.md"),
                user_query=mission.goal,
                metadata={
                    "mission_id": mission.id,
                    "stage": "routing",
                },
            )

            session_id = execution.metadata.get("session_id")

            with TimingScope(
                subsystem="athena",
                event_base="Athena",
                session_id=session_id,
                mission_id=mission.id,
                payload={"query": mission.goal}
            ) as scope:
                decision = athena.route(context)
                
                # Update payload before scope finishes
                scope.payload = {
                    "primary_model": decision.primary.value,
                    "reason": decision.reason,
                }
                
                if mission_context:
                    from app.mission.context import AthenaDecision
                    mission_context.athena_decision = AthenaDecision(
                        primary_model=decision.primary.value,
                        reason=decision.reason
                    )

            execution.metadata["athena_primary"] = decision.primary.value
            execution.metadata["athena_reason"] = decision.reason

        except Exception as exc:
            # TimingScope handles the Failed event emission if we don't catch it,
            # but since we WANT to swallow it (routing failure must not abort mission),
            # we need to emit manually or just swallow and log. The TimingScope will re-raise if we don't catch here.
            # Actually, since we caught it here, TimingScope already saw it? No, if we catch it INSIDE TimingScope it's hidden.
            # We catch it OUTSIDE TimingScope, so TimingScope saw it and emitted Failed. We just pass.
            pass

    def plan(
        self,
        mission: Mission,
        execution: ExecutionContext,
        mission_context: MissionContext = None,
    ):
        """
        Generate an execution plan via the Planner.
        """
        from app.mission.service import mission_service

        mission_service.update_status(mission, MissionStatus.PLANNING)

        session_id = execution.metadata.get("session_id")

        with TimingScope(
            subsystem="planner",
            event_base="Planning",
            session_id=session_id,
            mission_id=mission.id,
            execution_id=execution.mission_id,
            payload={"goal": mission.goal}
        ) as scope:
            plan = planner.plan(mission.goal)
            if mission_context:
                mission_context.plan = plan
            
            scope.payload = {
                "use_tool": plan.use_tool,
                "tool_name": plan.tool_name,
                "steps": plan.estimated_steps,
            }

        return plan

    def execute(
        self,
        mission: Mission,
        execution: ExecutionContext,
        plan,
        mission_context: MissionContext = None,
    ) -> ToolResult:
        """
        Execute the generated plan via the Executor.
        """
        from app.mission.service import mission_service
        from app.execution.manager import execution_manager

        mission_service.update_status(mission, MissionStatus.EXECUTING)
        execution_manager.start(execution)

        session_id = execution.metadata.get("session_id")

        with TimingScope(
            subsystem="executor",
            event_base="Execution",
            session_id=session_id,
            mission_id=mission.id,
            execution_id=execution.mission_id,
            payload={"tool_name": plan.tool_name}
        ) as scope:
            result = executor.execute(plan, execution)
            
            scope.payload = {
                "success": result.success,
                "output_preview": (result.output or "")[:200],
            }

        return result

    def reflect(
        self,
        mission: Mission,
        execution: ExecutionContext,
        mission_context: MissionContext = None,
    ) -> None:
        """
        Placeholder for Sprint 12 Reflection Engine.
        """
        from app.mission.service import mission_service
        mission_service.update_status(mission, MissionStatus.REFLECTING)


mission_pipeline = MissionPipeline()
