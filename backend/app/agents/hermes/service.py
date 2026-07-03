from datetime import datetime

from app.agent.service import agent
from app.agents.hermes.context import validate_context
from app.agents.hermes.context_builder import context_builder
from app.formatters.markdown import markdown
from app.llm.service import llm
from app.memory.conversation.service import conversation
from app.storage.service import storage


class Hermes:
    def __init__(self):
        self.llm = llm

    def chat(
        self,
        user_query: str,
    ) -> str:

        print("[Hermes] Starting Agent")

        # Execute agent (planner + executor)
        agent_result = agent.run(user_query)

        print("[Hermes] Agent Finished")

        tool_results = []

        if (
            agent_result.tool_used
            and agent_result.tool_result is not None
        ):
            tool_results.append(
                {
                    "tool_name": "tool",
                    "success": agent_result.tool_result.success,
                    "output": agent_result.tool_result.output,
                }
            )

        print("[Hermes] Building Context")

        # Build prompt context
        context = context_builder.build(
            user_query=user_query,
            tool_results=tool_results,
        )

        print("[Hermes] Context Built")

        # Validate context
        print("[Hermes] Validating Context")
        validate_context(context)
        print("[Hermes] Context Valid")

        # Generate response
        print("[Hermes] Calling LLM")

        response = self.llm.chat(context)

        print("[Hermes] LLM Finished")

        # Save conversation in memory
        conversation.add_user(user_query)
        conversation.add_assistant(response)

        print("[Hermes] Conversation Saved")

        # Persist conversation to Obsidian
        now = datetime.now()

        relative_path = (
            f"jarvis/conversations/"
            f"{now.year}/"
            f"{now.month:02d}/"
            f"{now.date()}.md"
        )

        print("[Hermes] Writing Conversation to Obsidian")

        storage.append(
            relative_path,
            markdown.conversation(
                user=user_query,
                assistant=response,
            ),
        )

        print("[Hermes] Finished")

        return response


hermes = Hermes()
