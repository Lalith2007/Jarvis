from app.execution.models import ExecutionContext
from app.executor.service import executor
from app.mission.models import Mission
from app.planner.service import planner
from app.tools.models import ToolResult


class MissionPipeline:
    """
    Canonical execution pipeline for JARVIS.

    Every mission executes through this pipeline.

    The pipeline owns the execution order while the
    individual subsystems own the implementation.
    """

    def run(
        self,
        mission: Mission,
        execution: ExecutionContext,
    ) -> ToolResult | None:

        self.analyze(
            mission,
            execution,
        )

        from app.runtime.service import runtime_service
        execution.runtime_session = runtime_service.create_session()
        
        self.route(
            mission,
            execution,
        )

        plan = self.plan(
            mission,
            execution,
        )

        if not plan.use_tool:
            if execution.runtime_session:
                from app.runtime.service import runtime_service
                runtime_service.cleanup_session(execution.runtime_session)
                execution.runtime_session = None
            return None

        result = self.execute(
            mission,
            execution,
            plan,
        )

        self.reflect(
            mission,
            execution,
        )

        if execution.runtime_session:
            from app.runtime.service import runtime_service
            runtime_service.cleanup_session(execution.runtime_session)
            execution.runtime_session = None
        return result

    def analyze(
        self,
        mission: Mission,
        execution: ExecutionContext,
    ) -> None:
        """
        Analyze mission to determine required capabilities.
        """
        from app.capabilities.service import capability_service
        
        capability_service.evaluate_mission(
            mission,
            execution,
        )

    def route(
        self,
        mission: Mission,
        execution: ExecutionContext,
    ) -> None:
        """
        Placeholder for Athena routing.
        """

        return None

    def plan(
        self,
        mission: Mission,
        execution: ExecutionContext,
    ):
        """
        Generate an execution plan.
        """

        return planner.plan(
            mission.goal,
        )

    def execute(
        self,
        mission: Mission,
        execution: ExecutionContext,
        plan,
    ) -> ToolResult:
        """
        Execute the generated plan.
        """

        return executor.execute(
            plan,
            execution,
        )

    def reflect(
        self,
        mission: Mission,
        execution: ExecutionContext,
    ) -> None:
        """
        Placeholder for Reflection.
        """

        return None


mission_pipeline = MissionPipeline()
