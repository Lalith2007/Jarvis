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

        self.route(
            mission,
            execution,
        )

        plan = self.plan(
            mission,
            execution,
        )

        if not plan.use_tool:
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

        return result

    def analyze(
        self,
        mission: Mission,
        execution: ExecutionContext,
    ) -> None:
        """
        Placeholder for mission analysis.
        """

        return None

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
