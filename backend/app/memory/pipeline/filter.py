from typing import List

from app.memory.core.models import MemoryRecord, MemoryQuery


class MemoryFilter:
    """
    Applies deterministic filters (type, visibility, importance, explicit tags).
    """
    
    @classmethod
    def apply(cls, candidates: List[MemoryRecord], query: MemoryQuery) -> List[MemoryRecord]:
        filtered = []
        
        for record in candidates:
            # 1. Type filter
            if query.types and record.type not in query.types:
                continue
                
            # 2. Importance filter
            if query.min_importance:
                # Basic priority ranking: low=0, normal=1, high=2, critical=3
                importances = {"low": 0, "normal": 1, "high": 2, "critical": 3}
                rec_val = importances.get(record.importance.value, 1)
                min_val = importances.get(query.min_importance.value, 1)
                if rec_val < min_val:
                    continue
                    
            # 3. Explicit tag filter
            if query.tags:
                if not any(tag in record.tags for tag in query.tags):
                    continue
                    
            filtered.append(record)
            
        return filtered
