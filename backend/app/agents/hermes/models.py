from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.memory.vault.models import SearchResult


class PromptContext(BaseModel):
    """
    Complete context passed to the LLM.
    """

    # System prompt
    system_prompt: str

    # Current user query
    user_query: str

    # Conversation history
    conversation: list[dict] = Field(default_factory=list)

    # Knowledge retrieved from the Obsidian vault
    knowledge: list[SearchResult] = Field(default_factory=list)

    # Results returned from tool execution
    tool_results: list[dict] = Field(default_factory=list)

    # Additional runtime metadata
    metadata: dict[str, Any] = Field(default_factory=dict)

    # Conversation/session identifier
    session_id: str | None = None

    # Timestamp
    created_at: datetime = Field(default_factory=datetime.now)

    # Context schema version
    version: str = "0.3"
