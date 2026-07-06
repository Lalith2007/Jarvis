from app.memory.core.models import MemoryQuery, MemoryRecord, MemoryType, MemoryImportance
from app.memory.pipeline.analyzer import QueryAnalyzer
from app.memory.pipeline.filter import MemoryFilter
from app.memory.pipeline.ranker import MemoryRanker

def test_query_analyzer():
    query = MemoryQuery(query="Where is the #secret base for Jarvis?")
    keywords, implicit_tags = QueryAnalyzer.analyze(query)
    
    assert "secret" in implicit_tags
    assert "base" in keywords
    assert "jarvis" in keywords
    assert "the" not in keywords
    assert "is" not in keywords

def test_memory_filter():
    r1 = MemoryRecord(type=MemoryType.FACT, importance=MemoryImportance.HIGH, tags=["secret"])
    r2 = MemoryRecord(type=MemoryType.EPISODIC, importance=MemoryImportance.LOW, tags=["public"])
    r3 = MemoryRecord(type=MemoryType.FACT, importance=MemoryImportance.NORMAL, tags=[])
    
    candidates = [r1, r2, r3]
    
    # Filter by type
    q1 = MemoryQuery(query="", types=[MemoryType.FACT])
    f1 = MemoryFilter.apply(candidates, q1)
    assert len(f1) == 2
    
    # Filter by importance
    q2 = MemoryQuery(query="", min_importance=MemoryImportance.NORMAL)
    f2 = MemoryFilter.apply(candidates, q2)
    assert len(f2) == 2
    assert f2[0].importance == MemoryImportance.HIGH
    
    # Filter by tag
    q3 = MemoryQuery(query="", tags=["secret"])
    f3 = MemoryFilter.apply(candidates, q3)
    assert len(f3) == 1
    assert f3[0].tags == ["secret"]

def test_memory_ranker():
    r1 = MemoryRecord(title="Apples", content="I like apples and bananas.", tags=["fruit"])
    r2 = MemoryRecord(title="Cars", content="I drive a fast car.", tags=["vehicle"])
    
    candidates = [r1, r2]
    
    # Query for apples
    ranked = MemoryRanker.rank(candidates, keywords=["apples", "bananas"], implicit_tags=["fruit"])
    
    assert len(ranked) == 1  # Cars record should drop out (score 0)
    assert ranked[0].record.title == "Apples"
    assert ranked[0].score > 0
