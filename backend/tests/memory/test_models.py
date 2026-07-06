import json
from app.memory.core.models import MemoryRecord, MemoryType

def test_memory_record_serialization():
    record = MemoryRecord(
        title="Test Memory",
        content="This is a test.",
        tags=["test", "memory"],
        type=MemoryType.FACT
    )
    
    # dict roundtrip
    d = record.to_dict()
    assert d["title"] == "Test Memory"
    assert d["type"] == "fact"
    
    record2 = MemoryRecord.from_dict(d)
    assert record2.memory_id == record.memory_id
    assert record2.tags == ["test", "memory"]
    
    # json roundtrip
    j = record.to_json()
    record3 = MemoryRecord.from_json(j)
    assert record3.memory_id == record.memory_id
    assert record3.type == MemoryType.FACT
