from app.agent.models import AgentResult
from app.executor.service import executor
from app.planner.service import planner


class Agent:
    """
    Coordinates planning and execution.

    Hermes communicates only with Agent.
    """

    def run(
        self,
        query: str,
    ) -> AgentResult:

        plan = planner.plan(query)

        if not plan.use_tool:
            return AgentResult(
                tool_used=False,
            )

        result = executor.execute(plan)

        return AgentResult(
            tool_used=True,
            tool_result=result,
        )


agent = Agent()
