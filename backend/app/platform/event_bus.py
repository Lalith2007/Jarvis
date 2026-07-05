import asyncio
import logging
import threading
from typing import List
from app.platform.models import PlatformEvent
from app.platform.subscriber import EventSubscriber

logger = logging.getLogger(__name__)

class EventBus:
    """
    Central, async, non-blocking platform event bus.
    Subscribers run asynchronously and do not block the critical execution paths.
    """
    def __init__(self):
        self._subscribers: List[EventSubscriber] = []
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def subscribe(self, subscriber: EventSubscriber) -> None:
        self._subscribers.append(subscriber)

    def unsubscribe(self, subscriber: EventSubscriber) -> None:
        if subscriber in self._subscribers:
            self._subscribers.remove(subscriber)

    def publish(self, event: PlatformEvent) -> None:
        """
        Publish an event to all matching subscribers.
        Spawns background tasks so publishers are not blocked.
        """
        for sub in self._subscribers:
            if sub.matches(event):
                asyncio.run_coroutine_threadsafe(self._safe_dispatch(sub, event), self._loop)

    async def _safe_dispatch(self, sub: EventSubscriber, event: PlatformEvent) -> None:
        try:
            await sub.callback(event)
        except Exception as e:
            logger.error(f"Error in event subscriber for {event.event_type}: {e}")

event_bus = EventBus()
