import { useEffect, useState } from 'react';
import { platformEventBus, type PlatformEvent } from '../services/platformEvents';

export function usePlatformEvents() {
  const [events, setEvents] = useState<PlatformEvent[]>([]);

  useEffect(() => {
    platformEventBus.connect();
    
    const unsubscribe = platformEventBus.subscribe((event) => {
      setEvents((prev) => [...prev, event]);
    });

    return () => {
      unsubscribe();
      // Normally we wouldn't disconnect if this is a global bus,
      // but for simple cleanup we can leave it connected globally
      // and just unsubscribe the local listener.
    };
  }, []);

  return { events };
}
