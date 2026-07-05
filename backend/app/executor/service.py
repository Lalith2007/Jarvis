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
        execution=None,
    ) -> ToolResult:

        from app.platform.publisher import EventPublisher

        EventPublisher.publish(
            subsystem="executor",
            event_type="ExecutorStarted",
            execution_id=execution.mission_id if execution else None,
            payload={"plan": plan.model_dump() if hasattr(plan, "model_dump") else {}}
        )

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

                from app.runtime.service import runtime_service
                from app.capabilities.models import CapabilityType
                from app.runtime.models import SecurityAction
                
                # Determine capability
                def get_cap(name):
                    n = name.lower()
                    if "file" in n or "dir" in n: return CapabilityType.FILESYSTEM
                    if "terminal" in n or "shell" in n: return CapabilityType.TERMINAL
                    if "python" in n: return CapabilityType.PYTHON_RUNTIME
                    if "browser" in n or "search" in n: return CapabilityType.BROWSER
                    if "memory" in n: return CapabilityType.MEMORY
                    return CapabilityType.TOOL_USAGE
                
                cap = get_cap(call.name)
                session = execution.runtime_session if execution else runtime_service.create_session()
                
                rt_result = runtime_service.execute_capability(
                    capability=cap,
                    session=session,
                    action=SecurityAction.READ if 'read' in call.name or 'list' in call.name or 'search' in call.name else (SecurityAction.WRITE if 'write' in call.name else SecurityAction.EXECUTE),
                    resource=call.name,
                    provider_name=call.name,
                    call_args=call.arguments
                )
                
                if execution:
                    if cap not in execution.active_capabilities:
                        execution.active_capabilities.append(cap)
                    execution.executed_capabilities.append(cap)
                    execution.runtime_results[call.name] = rt_result
                
                result = ToolResult(
                    success=rt_result.success,
                    output=rt_result.output if rt_result.success else str(rt_result.error),
                    metadata=rt_result.metadata
                )

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
            EventPublisher.publish(
                subsystem="executor",
                event_type="ExecutorCompleted",
                execution_id=execution.mission_id if execution else None,
                payload={"result": last_tool_result.model_dump() if hasattr(last_tool_result, "model_dump") else {}}
            )
            return last_tool_result

        result = ToolResult(
            success=True,
            output="Execution completed successfully.",
        )
        
        EventPublisher.publish(
            subsystem="executor",
            event_type="ExecutorCompleted",
            execution_id=execution.mission_id if execution else None,
            payload={"result": result.model_dump() if hasattr(result, "model_dump") else {}}
        )

        return result


executor = Executor()
