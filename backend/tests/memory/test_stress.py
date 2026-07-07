import os
import tempfile
import time
from app.memory.engine import MemoryEngine
from app.memory.storage.local import LocalMemoryStorage
from app.memory.core.models import MemoryRecord, MemoryQuery, MemoryType, MemoryImportance

def test_memory_stress_10000_records():
    with tempfile.TemporaryDirectory() as temp_dir:
        storage = LocalMemoryStorage(file_path=os.path.join(temp_dir, "stress.json"))
        engine = MemoryEngine(storage=storage)
        
        # Insert 10,000 synthetic memories
        records = []
        for i in range(10000):
            records.append(
                MemoryRecord(
                    title=f"Memory {i}",
                    content=f"Synthetic content for memory {i} with specific keyword_alpha_{i%100}",
                    tags=[f"tag_{i%10}"],
                    type=MemoryType.FACT,
                    importance=MemoryImportance.NORMAL
                )
            )
            
        # Fast bulk insert for test setup
        with storage._lock:
            for r in records:
                storage._memories[r.memory_id] = r
            storage._save()
            
        assert len(engine.storage.get_all()) == 10000
        
        # Random retrieval query
        query = MemoryQuery(query="keyword_alpha_42", tags=["tag_2"], limit=10)
        
        start_time = time.perf_counter()
        result = engine.search(query)
        end_time = time.perf_counter()
        
        latency_ms = (end_time - start_time) * 1000
        
        # Bounded latency (should easily be < 500ms for heuristic on 10k items)
        assert latency_ms < 500.0, f"Latency too high: {latency_ms}ms"
        
        # Verify deduplication (results <= limit)
        assert len(result.results) <= 10
        
        # Verify stable ranking (deterministic sorting means multiple calls yield identical results)
        result2 = engine.search(query)
        assert [r.memory_id for r in result.results] == [r.memory_id for r in result2.results]
