import json
from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.platform.event_bus import event_bus
from app.platform.subscriber import EventSubscriber
from app.platform.models import PlatformEvent

router = APIRouter(tags=["platform_ws"])

@router.get("/ws/platform/test")
def test_platform_ws():
    return {"message": "platform ws router is active"}

class PlatformConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, event: PlatformEvent):
        message = event.model_dump_json()
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

ws_manager = PlatformConnectionManager()

async def ws_event_handler(event: PlatformEvent):
    await ws_manager.broadcast(event)

# Register the global subscriber for the websocket manager
# It listens to all events
ws_subscriber = EventSubscriber(callback=ws_event_handler)
event_bus.subscribe(ws_subscriber)

@router.websocket("/ws/platform")
async def platform_websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
