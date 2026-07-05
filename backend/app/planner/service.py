import re
from pathlib import Path

from app.planner.models import (
    Plan,
    PlanStep,
    StepType,
)


class Planner:
    """
    Planner v2

    Converts a user request into an execution plan.
    """

    def plan(
        self,
        user_query: str,
    ) -> Plan:

        from app.platform.publisher import EventPublisher

        EventPublisher.publish(
            subsystem="planner",
            event_type="PlannerStarted",
            payload={"query": user_query}
        )

        query = user_query.lower()

        words = set(
            re.findall(
                r"\b[\w]+\b",
                query,
            )
        )

        steps: list[PlanStep] = []

        reasoning: list[str] = []

        step_id = 1

        # ---------------------------------
        # Memory
        # ---------------------------------

        memory_keywords = {
            "remember",
            "memory",
            "vault",
            "obsidian",
            "previous",
            "conversation",
        }

        if words & memory_keywords:

            steps.append(
                PlanStep(
                    id=step_id,
                    type=StepType.MEMORY,
                    description="Retrieve relevant memory.",
                )
            )

            reasoning.append(
                "Memory retrieval required."
            )

            step_id += 1

        # ---------------------------------
        # Tool Selection
        # ---------------------------------

        tool_name = None
        arguments = {}

        if "search" in words or "find" in words:

            tool_name = "search_files"

            ignored = {
                "search",
                "find",
                "for",
                "a",
                "an",
                "the",
                "my",
                "file",
                "files",
            }

            pattern = None

            for word in words:
                if word not in ignored:
                    pattern = word
                    break

            arguments = {
                "path": str(Path.cwd()),
                "pattern": pattern or "",
            }

        elif "read" in words:

            tool_name = "read_file"

        elif "write" in words:

            tool_name = "write_file"

        elif "list" in words:

            tool_name = "list_directory"

            arguments = {
                "path": str(Path.cwd()),
            }

        if tool_name is not None:

            steps.append(
                PlanStep(
                    id=step_id,
                    type=StepType.TOOL,
                    description=f"Execute {tool_name}.",
                    tool_name=tool_name,
                    arguments=arguments,
                )
            )

            reasoning.append(
                f"Tool required: {tool_name}."
            )

            step_id += 1

        # ---------------------------------
        # LLM
        # ---------------------------------

        steps.append(
            PlanStep(
                id=step_id,
                type=StepType.LLM,
                description="Generate final response.",
            )
        )

        reasoning.append(
            "LLM response required."
        )

        plan = Plan(
            use_tool=tool_name is not None,
            tool_name=tool_name,
            arguments=arguments,
            steps=steps,
            reasoning=" ".join(reasoning),
            estimated_steps=len(steps),
            requires_llm=True,
            requires_tools=tool_name is not None,
            requires_memory=any(
                step.type == StepType.MEMORY
                for step in steps
            ),
        )

        EventPublisher.publish(
            subsystem="planner",
            event_type="PlannerCompleted",
            payload={"plan": plan.model_dump() if hasattr(plan, "model_dump") else {}}
        )

        return plan


planner = Planner()
