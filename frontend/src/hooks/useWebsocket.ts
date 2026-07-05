import { useEffect, useRef, useState } from 'react';
import { FrontendConfig } from '../../electron/config.cjs';

export function useRuntimeWebsocket() {
  const [messages, setMessages] = useState<any[]>([]);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Only connect once
    if (ws.current) return;
    
    console.log(`[WS ATTEMPT] Connecting to ${FrontendConfig.WS_RUNTIME}`);
    const socket = new WebSocket(FrontendConfig.WS_RUNTIME);
    
    socket.onopen = () => {
      console.log(`[WS SUCCESS] Connected to ${FrontendConfig.WS_RUNTIME}`);
    };
    
    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setMessages((prev) => [...prev, data]);
      } catch (e) {
        console.error(`[WS MESSAGE ERROR] Failed to parse WebSocket message`, e);
      }
    };
    
    socket.onclose = (event) => {
      console.log(`[WS CLOSED] URL: ${FrontendConfig.WS_RUNTIME} | Code: ${event.code} | Reason: ${event.reason} | WasClean: ${event.wasClean}`);
    };
    
    socket.onerror = (error) => {
      console.error(`[WS ERROR] URL: ${FrontendConfig.WS_RUNTIME} | Error:`, error);
    };
    
    ws.current = socket;

    return () => {
      if (ws.current?.readyState === WebSocket.OPEN) {
        ws.current.close();
      }
      ws.current = null;
    };
  }, []);

  return { messages };
}
