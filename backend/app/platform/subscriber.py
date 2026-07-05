from typing import Callable, Coroutine, Any, List, Optional
from app.platform.models import PlatformEvent

# A subscriber callback is an async function that takes a PlatformEvent
SubscriberCallback = Callable[[PlatformEvent], Coroutine[Any, Any, None]]

class EventSubscriber:
    def __init__(self, callback: SubscriberCallback, subsystems: Optional[List[str]] = None, event_types: Optional[List[str]] = None):
        """
        :param callback: Async function to handle the event.
        :param subsystems: Optional list of subsystems to filter on. If None, receive all.
        :param event_types: Optional list of event_types to filter on. If None, receive all.
        """
        self.callback = callback
        self.subsystems = subsystems
        self.event_types = event_types

    def matches(self, event: PlatformEvent) -> bool:
        if self.subsystems and event.subsystem not in self.subsystems:
            return False
        if self.event_types and event.event_type not in self.event_types:
            return False
        return True
