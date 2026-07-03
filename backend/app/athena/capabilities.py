from enum import Enum


class Capability(str, Enum):
    """
    High-level capabilities understood by Athena.
    """

    CODING = "coding"

    PLANNING = "planning"

    RESEARCH = "research"

    DOCUMENTS = "documents"

    KNOWLEDGE = "knowledge"

    BUSINESS = "business"

    FINANCE = "finance"

    TRADING = "trading"

    MONEY = "money"

    EXECUTION = "execution"

    WRITING = "writing"

    CONVERSATION = "conversation"

    TOOL_USAGE = "tool_usage"
