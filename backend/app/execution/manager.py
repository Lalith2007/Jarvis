from app.execution.context import execution_context
from app.execution.models import (
    ExecutionContext,
    ExecutionStatus,
)
from app.execution.state import execution_state


class ExecutionManager:
    """
    High-level interface for mission execution.

    This is the ONLY object other subsystems should use.

    Responsibilities:

    • Create missions
    • Register missions
    • Update mission state
    • Complete missions
    • Fail missions
    • Query active missions

    Future:

    • Pause / Resume
    • Retry
    • Scheduling
    • Background execution
    • Distributed execution
    """

    def create(
        self,
        goal: str,
    ) -> ExecutionContext:

        context = execution_context.create(goal)

        execution_state.register(context)

        return context

    def start(
        self,
        context: ExecutionContext,
    ) -> None:

        execution_context.update_status(
            context,
            ExecutionStatus.RUNNING,
        )

    def complete(
        self,
        context: ExecutionContext,
    ) -> None:

        execution_context.update_status(
            context,
            ExecutionStatus.COMPLETED,
        )

    def fail(
        self,
        context: ExecutionContext,
    ) -> None:

        execution_context.update_status(
            context,
            ExecutionStatus.FAILED,
        )

    def waiting(
        self,
        context: ExecutionContext,
    ) -> None:

        execution_context.update_status(
            context,
            ExecutionStatus.WAITING,
        )

    def cancel(
        self,
        context: ExecutionContext,
    ) -> None:

        execution_context.update_status(
            context,
            ExecutionStatus.CANCELLED,
        )

    def get(
        self,
        mission_id: str,
    ) -> ExecutionContext | None:

        return execution_state.get(
            mission_id,
        )

    def active(
        self,
    ) -> list[ExecutionContext]:

        return execution_state.running()

    def all(
        self,
    ) -> list[ExecutionContext]:

        return execution_state.all()

    def clear(
        self,
    ) -> None:

        execution_state.clear()


execution_manager = ExecutionManager()
