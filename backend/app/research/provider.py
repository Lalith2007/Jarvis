"""
Research source providers (Sprint 13.7).

`SearchProvider` is the seam research capabilities call; concrete providers
(web search API, GitHub, docs, the browser driver) implement it. Injectable so
research is hermetically testable without network/keys.
"""
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field


class SearchHit(BaseModel):
    title: str
    url: str
    snippet: str = ""
    source_type: str = "web"


class SearchProvider(ABC):
    @abstractmethod
    def search(self, query: str, limit: int = 8) -> list[SearchHit]: ...

    def fetch(self, url: str) -> str:  # optional deep-fetch
        return ""

    def available(self) -> bool:
        return True


class NullSearchProvider(SearchProvider):
    """Default when no search backend is configured — returns nothing."""

    def search(self, query: str, limit: int = 8) -> list[SearchHit]:
        return []

    def available(self) -> bool:
        return False


class ResearchManager:
    def __init__(self):
        self._provider: SearchProvider | None = None

    def set_provider(self, provider: SearchProvider) -> None:
        self._provider = provider

    def provider(self) -> SearchProvider:
        if self._provider is None:
            self._provider = NullSearchProvider()
        return self._provider


research_manager = ResearchManager()
