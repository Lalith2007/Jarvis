from app.agents.hermes.models import PromptContext


class MessageBuilder:
    """
    Converts a PromptContext into an OpenAI-compatible
    chat message list.

    This class is intentionally provider-agnostic.
    """

    def build(
        self,
        context: PromptContext,
    ) -> list[dict]:

        messages: list[dict] = [
            {
                "role": "system",
                "content": context.system_prompt,
            }
        ]

        # -----------------------------
        # Knowledge
        # -----------------------------
        if context.knowledge:

            knowledge = "\n\n".join(
                [
                    f"# {result.note.title}\n{result.note.content}"
                    for result in context.knowledge
                ]
            )

            messages.append(
                {
                    "role": "system",
                    "content": (
                        "Relevant knowledge from the user's vault:\n\n"
                        + knowledge
                    ),
                }
            )
        else:
            messages.append(
                {
                    "role": "system",
                    "content": "You currently have no stored memories or knowledge about the user. If asked about the user's identity, preferences, or past, explicitly state that you have no stored memories."
                }
            )

        # -----------------------------
        # Tool Results
        # -----------------------------
        if context.tool_results:

            tool_output = "\n\n".join(
                [
                    (
                        f"Tool: {tool.get('tool_name', 'Unknown')}\n"
                        f"Success: {tool.get('success', False)}\n"
                        f"Output:\n{tool.get('output', '')}"
                    )
                    for tool in context.tool_results
                ]
            )

            messages.append(
                {
                    "role": "system",
                    "content": (
                        "Recent tool execution results:\n\n"
                        + tool_output
                    ),
                }
            )

        # -----------------------------
        # Conversation
        # -----------------------------
        messages.extend(
            context.conversation
        )

        # -----------------------------
        # User Message
        # -----------------------------
        messages.append(
            {
                "role": "user",
                "content": context.user_query,
            }
        )

        return messages


message_builder = MessageBuilder()
