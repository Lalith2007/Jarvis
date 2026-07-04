from datetime import datetime
from uuid import uuid4

from app.execution.models import (
    Artifact,
    ExecutionContext,
    ExecutionStatus,
    ExecutionStepState,
)


class ExecutionContextManager:
    """
    Creates and manages execution contexts.

    Every mission executed by JARVIS receives its own
    isolated ExecutionContext.
    """

    def create(
        self,
        goal: str,
    ) -> ExecutionContext:

        return ExecutionContext(
            mission_id=str(uuid4()),
            goal=goal,
        )

    def update_status(
        self,
        context: ExecutionContext,
        status: ExecutionStatus,
    ) -> None:

        context.status = status
        context.updated_at = datetime.now()

    def add_step(
        self,
        context: ExecutionContext,
        name: str,
    ) -> ExecutionStepState:

        step = ExecutionStepState(
            id=len(context.steps) + 1,
            name=name,
        )

        context.steps.append(step)
        context.updated_at = datetime.now()

        return step

    def start_step(
        self,
        step: ExecutionStepState,
    ) -> None:

        step.status = ExecutionStatus.RUNNING
        step.started_at = datetime.now()

    def complete_step(
        self,
        step: ExecutionStepState,
        output=None,
    ) -> None:

        step.status = ExecutionStatus.COMPLETED
        step.output = output
        step.finished_at = datetime.now()

    def fail_step(
        self,
        step: ExecutionStepState,
        output=None,
    ) -> None:

        step.status = ExecutionStatus.FAILED
        step.output = output
        step.finished_at = datetime.now()

    def add_artifact(
        self,
        context: ExecutionContext,
        name: str,
        artifact_type: str,
        value,
        metadata: dict | None = None,
    ) -> Artifact:

        artifact = Artifact(
            name=name,
            type=artifact_type,
            value=value,
            metadata=metadata or {},
        )

        context.artifacts[name] = artifact
        context.updated_at = datetime.now()

        return artifact

    def set_variable(
        self,
        context: ExecutionContext,
        key: str,
        value,
    ) -> None:

        context.variables[key] = value
        context.updated_at = datetime.now()

    def get_variable(
        self,
        context: ExecutionContext,
        key: str,
        default=None,
    ):

        return context.variables.get(
            key,
            default,
        )


execution_context = ExecutionContextManager()
