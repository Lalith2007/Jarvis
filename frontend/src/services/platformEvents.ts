export interface PlatformEvent {
  id: string;
  request_id: string;
  timestamp: string;
  mission_id?: string;
  session_id?: string;
  execution_id?: string;
  subsystem: string;
  event_type: string;
  status: string;
  severity: string;
  duration_ms?: number;
  payload: Record<string, any>;
  metadata: Record<string, any>;
}

type EventCallback = (event: PlatformEvent) => void;

import { FrontendConfig } from '../../electron/config.cjs';

class PlatformEventBus {
  private ws: WebSocket | null = null;
  private url = FrontendConfig.WS_PLATFORM;
  private listeners: Set<EventCallback> = new Set();
  private reconnectTimer: number | null = null;

  connect() {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    console.log(`[WS ATTEMPT] Connecting to Platform Event Bus at ${this.url}...`);
    this.ws = new WebSocket(this.url);

    this.ws.onopen = () => {
      console.log(`[WS SUCCESS] Platform Event Bus connected at ${this.url}`);
      if (this.reconnectTimer) {
        clearTimeout(this.reconnectTimer);
        this.reconnectTimer = null;
      }
    };

    this.ws.onmessage = (messageEvent) => {
      try {
        const event: PlatformEvent = JSON.parse(messageEvent.data);
        this.listeners.forEach((cb) => cb(event));
      } catch (e) {
        console.error(`[WS MESSAGE ERROR] Failed to parse PlatformEvent`, e);
      }
    };

    this.ws.onclose = (event) => {
      console.log(`[WS CLOSED] Platform Event Bus disconnected. URL: ${this.url} | Code: ${event.code} | Reason: ${event.reason} | WasClean: ${event.wasClean}. Reconnecting in 3s...`);
      this.ws = null;
      this.reconnectTimer = setTimeout(() => this.connect(), 3000) as any;
    };

    this.ws.onerror = (error) => {
      console.error(`[WS ERROR] Platform Event Bus error at ${this.url}`, error);
      this.ws?.close();
    };
  }

  subscribe(callback: EventCallback) {
    this.listeners.add(callback);
    return () => {
      this.listeners.delete(callback);
    };
  }

  disconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    if (this.ws) {
      this.ws.close();
    }
  }
}

export const platformEventBus = new PlatformEventBus();
