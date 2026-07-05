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
        session_id: str | None = None,
    ) -> AgentResult:

        result, execution = mission_controller.run(
            query,
            session_id=session_id,
        )

        if result is None:
            return AgentResult(
                tool_used=False,
                metadata=execution.metadata,
                mission_id=execution.mission_id,
            )

        return AgentResult(
            tool_used=True,
            tool_result=result,
            metadata=execution.metadata,
            mission_id=execution.mission_id,
        )


agent = Agent()
