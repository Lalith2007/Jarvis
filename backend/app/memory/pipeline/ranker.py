from datetime import datetime, timezone
from typing import List

from app.memory.core.models import MemoryRecord, MemoryCandidate


class MemoryRanker:
    """
    Deterministic heuristic ranking combining:
    - keyword overlap
    - tag overlap
    - importance modifier
    - recency modifier
    """
    
    @classmethod
    def rank(
        cls, 
        candidates: List[MemoryRecord], 
        keywords: List[str], 
        implicit_tags: List[str]
    ) -> List[MemoryCandidate]:
        
        results = []
        now = datetime.now(timezone.utc)
        
        for record in candidates:
            score = 0.0
            matched_keywords = []
            matched_tags = []
            
            # Content & Title keyword overlap
            text_corpus = (record.title + " " + record.summary + " " + record.content).lower()
            for kw in keywords:
                if kw in text_corpus:
                    score += 1.0
                    matched_keywords.append(kw)
                    
            # Tag overlap
            for tag in implicit_tags:
                if tag in record.tags:
                    score += 2.0  # Tags are stronger signals
                    matched_tags.append(tag)
                    
            # Importance modifier
            importances = {"low": 0.8, "normal": 1.0, "high": 1.5, "critical": 2.0}
            score *= importances.get(record.importance.value, 1.0)
            
            # Recency modifier (small bump for newer memories)
            age_days = (now - record.created_at).total_seconds() / (24 * 3600)
            recency_multiplier = max(0.5, 1.0 - (age_days * 0.001)) # Decays slowly
            score *= recency_multiplier
            
            # Only include if there is some relevance, unless query is empty
            if score > 0 or not keywords:
                results.append(
                    MemoryCandidate(
                        record=record,
                        score=score,
                        matched_tags=matched_tags,
                        matched_keywords=matched_keywords
                    )
                )
                
        # Sort descending by score, then ascending by memory_id (deterministic tie-breaker)
        results.sort(key=lambda x: (-x.score, x.record.memory_id))
        return results
