import pytest
import os
import tempfile
from unittest.mock import patch, ANY
from app.memory.engine import MemoryEngine
from app.memory.storage.local import LocalMemoryStorage
from app.memory.core.models import MemoryRecord, MemoryQuery
from app.memory.capabilities import MemoryReadCapability, MemoryWriteCapability
from app.capabilities.core.base import CapabilityContext, CapabilityDiagnostics

def test_memory_engine_events():
    # Mock EventPublisher
    with patch("app.platform.publisher.EventPublisher.publish") as mock_publish:
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = LocalMemoryStorage(file_path=os.path.join(temp_dir, "mem.json"))
            engine = MemoryEngine(storage=storage)
            
            # Test Store Event
            r1 = MemoryRecord(title="Test", content="Test")
            engine.store(r1)
            mock_publish.assert_any_call(
                subsystem="memory",
                event_type="MemoryStored",
                payload={"memory_id": r1.memory_id}
            )
            
            # Test Search Event
            q = MemoryQuery(query="Test")
            engine.search(q)
            mock_publish.assert_any_call(
                subsystem="memory",
                event_type="MemorySearchCompleted",
                payload={"query": "Test", "total_results": 1, "execution_time_ms": ANY}
            )

def test_memory_capabilities():
    # Patch global engine to use temp storage
    with tempfile.TemporaryDirectory() as temp_dir:
        storage = LocalMemoryStorage(file_path=os.path.join(temp_dir, "mem.json"))
        temp_engine = MemoryEngine(storage=storage)
        
        with patch("app.memory.capabilities.memory_engine", temp_engine):
            # Mock diagnostics
            mock_diag = CapabilityDiagnostics(id="123", capability_id="mem")
            
            # 1. Write Capability
            write_cap = MemoryWriteCapability()
            ctx_write = CapabilityContext(
                mission_id="mission_1",
                graph_id="g1",
                execution_id="e1",
                node_id="n1",
                runtime_state={"content": "Capability test content", "title": "Cap Title", "tags": ["cap"]}
            )
            write_res = write_cap.execute(ctx_write, mock_diag)
            assert write_res.success is True
            assert write_res.status == "success"
            
            # 2. Read Capability
            read_cap = MemoryReadCapability()
            ctx_read = CapabilityContext(
                mission_id="mission_1",
                graph_id="g1",
                execution_id="e1",
                node_id="n2",
                runtime_state={"query": "Capability test"}
            )
            read_res = read_cap.execute(ctx_read, mock_diag)
            assert read_res.success is True
            assert read_res.status == "success"
            assert len(read_res.result["results"]) == 1
            assert read_res.result["results"][0]["title"] == "Cap Title"
