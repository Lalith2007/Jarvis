from app.agent.models import AgentResult
from app.mission.controller import mission_controller


class Agent:
    """
    Primary entry point into the JARVIS backend.

    Hermes communicates only with Agent.

    Agent delegates the complete request lifecycle
    to the Mission Controller.
    """

    def run(
        self,
        query: str,
    ) -> AgentResult:

        result = mission_controller.run(
            query,
        )

        if result is None:
            return AgentResult(
                tool_used=False,
            )

        return AgentResult(
            tool_used=True,
            tool_result=result,
        )


agent = Agent()
