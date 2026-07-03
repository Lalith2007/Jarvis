from pydantic import BaseModel, Field


class ProcessedQuery(BaseModel):
    original: str

    normalized: str

    keywords: list[str] = Field(default_factory=list)

    phrases: list[str] = Field(default_factory=list)

    metadata: dict = Field(default_factory=dict)
