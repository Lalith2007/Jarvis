from typing import List

from app.memory.core.models import MemoryCandidate


class Deduplicator:
    """
    Ensures memory candidates are unique by memory_id.
    Retains the highest scoring instance.
    """
    
    @classmethod
    def apply(cls, candidates: List[MemoryCandidate]) -> List[MemoryCandidate]:
        seen = set()
        deduped = []
        
        for cand in candidates:
            if cand.record.memory_id not in seen:
                seen.add(cand.record.memory_id)
                deduped.append(cand)
                
        return deduped
