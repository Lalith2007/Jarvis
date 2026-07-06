from typing import List

from app.memory.core.models import MemoryCandidate, MemoryRecord


class Summarizer:
    """
    Extracts the final payload from candidates, applying any pagination limits.
    """
    
    @classmethod
    def apply(cls, candidates: List[MemoryCandidate], limit: int, offset: int) -> List[MemoryRecord]:
        paginated = candidates[offset:offset+limit]
        return [cand.record for cand in paginated]
