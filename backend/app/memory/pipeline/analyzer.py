import re
from typing import List, Set

from app.memory.core.models import MemoryQuery


class QueryAnalyzer:
    """
    Parses natural language queries to extract keywords and potential tags.
    Deterministic, heuristic-based.
    """
    
    STOP_WORDS = {
        "a", "an", "the", "and", "or", "but", "if", "because", "as", "what",
        "when", "where", "how", "why", "who", "which", "this", "that", "these",
        "those", "then", "just", "so", "than", "such", "both", "through", "about",
        "for", "is", "of", "while", "during", "to", "what's", "i", "my", "me"
    }
    
    @classmethod
    def analyze(cls, query: MemoryQuery) -> tuple[List[str], List[str]]:
        """
        Returns (keywords, implicit_tags).
        """
        text = query.query.lower()
        
        # Extract explicit #tags if any
        implicit_tags = re.findall(r'#(\w+)', text)
        
        # Clean text
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        
        # Extract keywords
        keywords = []
        for word in words:
            if word not in cls.STOP_WORDS and len(word) > 2:
                keywords.append(word)
                
        return keywords, implicit_tags
