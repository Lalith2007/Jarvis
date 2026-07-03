from pydantic import BaseModel


class VaultNote(BaseModel):
    path: str
    title: str
    content: str


class SearchResult(BaseModel):
    score: int
    matched_fields: list[str]
    note: VaultNote
