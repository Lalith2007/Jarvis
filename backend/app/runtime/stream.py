import uuid
import queue
from typing import Iterator, Optional
from pydantic import BaseModel

class StreamResult(BaseModel):
    """
    A serializable reference to an active stream managed by the Runtime layer.
    """
    stream_id: str
    is_stream: bool = True

class StreamHandle:
    """
    Runtime-owned object that holds the actual python queue for streaming.
    """
    def __init__(self, stream_id: str):
        self.stream_id = stream_id
        self._queue = queue.Queue()
        self._done = False
        
    def push(self, chunk: str):
        self._queue.put(chunk)
        
    def finish(self):
        self._done = True
        self._queue.put(None)
        
    def __iter__(self) -> Iterator[str]:
        while True:
            chunk = self._queue.get()
            if chunk is None:
                break
            yield chunk

class StreamRegistry:
    """
    Thread-safe registry for stream handles, owned by the runtime service.
    """
    def __init__(self):
        self._streams: dict[str, StreamHandle] = {}
        
    def create_stream(self) -> StreamHandle:
        stream_id = str(uuid.uuid4())
        handle = StreamHandle(stream_id)
        self._streams[stream_id] = handle
        return handle
        
    def get_stream(self, stream_id: str) -> Optional[StreamHandle]:
        return self._streams.get(stream_id)
        
    def remove_stream(self, stream_id: str):
        if stream_id in self._streams:
            del self._streams[stream_id]

stream_registry = StreamRegistry()
