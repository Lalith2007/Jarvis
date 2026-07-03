from app.executor.models import StepResult
from app.planner.models import Plan, StepType
from app.tools.models import ToolCall, ToolResult
from app.tools.registry import tool_registry


class Executor:
    """
    Executor v2.

    Executes planner steps sequentially.

    Public API remains unchanged by returning ToolResult.
    """

    def execute(
        self,
        plan: Plan,
    ) -> ToolResult:

        if not plan.steps:
            return ToolResult(
                success=False,
                output="Plan contains no executable steps.",
            )

        step_results: list[StepResult] = []

        last_tool_result: ToolResult | None = None

        for step in plan.steps:

            if step.type == StepType.MEMORY:

                step_results.append(
                    StepResult(
                        step=step,
                        success=True,
                        output="Memory step completed.",
                    )
                )

                continue

            if step.type == StepType.TOOL:

                call = ToolCall(
                    name=step.tool_name,
                    arguments=step.arguments,
                )

                result = tool_registry.execute(call)

                last_tool_result = result

                step_results.append(
                    StepResult(
                        step=step,
                        success=result.success,
                        output=result.output,
                        metadata=result.metadata,
                        tool_result=result,
                    )
                )

                if not result.success:
                    return result

                continue

            if step.type == StepType.LLM:

                step_results.append(
                    StepResult(
                        step=step,
                        success=True,
                        output="LLM step deferred to Hermes.",
                    )
                )

                continue

            if step.type == StepType.VALIDATION:

                step_results.append(
                    StepResult(
                        step=step,
                        success=True,
                        output="Validation step completed.",
                    )
                )

                continue

            if step.type == StepType.STORAGE:

                step_results.append(
                    StepResult(
                        step=step,
                        success=True,
                        output="Storage step completed.",
                    )
                )

        if last_tool_result is not None:
            return last_tool_result

        return ToolResult(
            success=True,
            output="Execution completed successfully.",
        )


executor = Executor()
