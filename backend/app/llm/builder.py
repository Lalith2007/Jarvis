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
                self._format_tool_result(tool)
                for tool in context.tool_results
            )

            messages.append(
                {
                    "role": "system",
                    "content": (
                        "Authoritative tool execution results "
                        "(treat as ground truth — do not invent alternative values):\n\n"
                        + tool_output
                    ),
                }
            )

            if context.grounding_enforced:
                messages.append(
                    {
                        "role": "system",
                        "content": (
                            "GROUNDING ENFORCEMENT ACTIVE.\n\n"
                            "The tool results above contain authoritative system data. "
                            "Answer ONLY using information from the tool results. "
                            "Do NOT add items, models, providers, or capabilities that are "
                            "not present in the tool results. "
                            "If the tool result lists zero items, report zero items. "
                            "Your training knowledge about external AI systems is irrelevant "
                            "here — answer only from the tool results provided above."
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


    # ──────────────────────────────────────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _format_tool_result(tool: dict) -> str:
        """
        Sprint 12.8 — Structured tool context.

        When the output is a dict (structured CapabilityResult.result), render
        it as compact JSON so the LLM receives typed data rather than
        concatenated strings.  Plain strings are passed through unchanged for
        backward compatibility with legacy capabilities.
        """
        import json

        tool_name = tool.get("tool_name", "Unknown")
        success = tool.get("success", False)
        output = tool.get("output", "")

        if isinstance(output, (dict, list)):
            output_str = json.dumps(output, indent=2, ensure_ascii=False)
        else:
            output_str = str(output) if output is not None else ""

        return (
            f"Tool: {tool_name}\n"
            f"Success: {success}\n"
            f"Output:\n{output_str}"
        )


message_builder = MessageBuilder()
