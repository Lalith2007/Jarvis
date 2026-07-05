import asyncio
import uuid

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import threading

from app.agents.hermes.service import hermes
from app.models.chat import ChatRequest, ChatResponse
from app.platform.publisher import EventPublisher
from app.system.routes import router as system_router
from app.api.endpoints.missions import router as missions_router
from app.api.endpoints.runtime import router as runtime_router
from app.api.endpoints.capabilities import router as capabilities_router
from app.api.endpoints.mcp import router as mcp_router
from app.api.endpoints.intelligence import router as intelligence_router
from app.api.endpoints.dashboard import router as dashboard_router
from app.api.endpoints.platform_ws import router as platform_ws_router

router = APIRouter()
api_router = APIRouter(prefix="/api")

api_router.include_router(system_router)
api_router.include_router(missions_router)
api_router.include_router(runtime_router)
api_router.include_router(capabilities_router)
api_router.include_router(mcp_router)
api_router.include_router(intelligence_router)
api_router.include_router(dashboard_router)


@api_router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Blocking chat endpoint — preserved for backward compatibility.

    Returns the full response after the mission pipeline completes.
    Also returns mission_id and session_id so the frontend can
    correlate Platform Events.
    """
    response, session_id = hermes.chat(
        request.message,
        session_id=request.session_id,
    )
    return ChatResponse(response=response, session_id=session_id)


@api_router.post("/chat/stream")
async def chat_stream(request: Request, body: ChatRequest):
    """
    Streaming chat endpoint.

    Returns text/event-stream (Server-Sent Events).
    Each event carries a JSON payload:

        data: {"type": "chunk", "content": "<token>"}
        data: {"type": "done", "session_id": "<id>"}
        data: {"type": "error", "content": "<message>"}

    The frontend should use EventSource or fetch with a ReadableStream.
    """
    session_id = body.session_id or str(uuid.uuid4())
    cancel_event = threading.Event()

    async def generate():
        try:
            # Run the synchronous streaming generator in a thread
            # so it doesn't block the event loop (required for WS delivery)
            loop = asyncio.get_event_loop()
            chunk_queue: asyncio.Queue[str | None] = asyncio.Queue()

            def _run_stream():
                try:
                    for chunk in hermes.chat_stream(
                        body.message,
                        session_id=session_id,
                        cancel_event=cancel_event,
                    ):
                        if cancel_event.is_set():
                            break
                        loop.call_soon_threadsafe(
                            chunk_queue.put_nowait, chunk
                        )
                except Exception as exc:
                    if not cancel_event.is_set():
                        loop.call_soon_threadsafe(
                            chunk_queue.put_nowait,
                            f"__ERROR__:{exc}",
                        )
                finally:
                    loop.call_soon_threadsafe(
                        chunk_queue.put_nowait, None
                    )  # sentinel

            import threading
            t = threading.Thread(target=_run_stream, daemon=True)
            t.start()

            while True:
                if await request.is_disconnected():
                    cancel_event.set()
                    break

                try:
                    # Wait for next item, checking disconnect status frequently
                    item = await asyncio.wait_for(chunk_queue.get(), timeout=0.5)
                except asyncio.TimeoutError:
                    continue

                if item is None:
                    break
                if isinstance(item, str) and item.startswith("__ERROR__:"):
                    error_msg = item[len("__ERROR__:"):]
                    yield f'data: {{"type":"error","content":{_json_str(error_msg)}}}\n\n'
                    break
                yield f'data: {{"type":"chunk","content":{_json_str(item)}}}\n\n'

            if not cancel_event.is_set():
                yield f'data: {{"type":"done","session_id":"{session_id}"}}\n\n'

        except Exception as exc:
            yield f'data: {{"type":"error","content":{_json_str(str(exc))}}}\n\n'

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


def _json_str(s: str) -> str:
    """Serialize a string to JSON-safe quoted form."""
    import json
    return json.dumps(s)


router.include_router(api_router)
router.include_router(platform_ws_router)
