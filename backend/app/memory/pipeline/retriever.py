from typing import List

from app.memory.core.models import MemoryRecord, MemoryQuery
from app.memory.storage.base import MemoryStorage


class CandidateRetriever:
    """
    Retrieves all initial candidates from storage.
    """
    
    @classmethod
    def retrieve(cls, storage: MemoryStorage, query: MemoryQuery) -> List[MemoryRecord]:
        # For heuristic search, we retrieve all and filter.
        # Future optimization: push down indexing/filters to storage.
        return storage.get_all()
