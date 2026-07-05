# JARVIS API Contract (v0.1.0-alpha)

This document represents the frozen public interfaces for the JARVIS backend.

## 1. REST Endpoints

### `POST /api/chat/stream`
The primary intelligence interface. Yields `text/event-stream`.

**Request Body (`ChatRequest`)**:
```json
{
  "message": "string (required)",
  "session_id": "string (optional, defaults to new uuid)"
}
```

**SSE Response Format**:
Chunks are emitted as JSON payloads prefixed by `data: `:
```text
data: {"type": "chunk", "content": "Hello"}
data: {"type": "done", "session_id": "uuid"}
data: {"type": "error", "content": "Exception string"}
```

### `POST /api/chat`
Blocking variant of chat (legacy/fallback).

**Request Body**: `ChatRequest`
**Response Body (`ChatResponse`)**:
```json
{
  "response": "string",
  "session_id": "string"
}
```

### `GET /api/dashboard`
Returns hydration data for the React dashboard.

**Response Body**:
```json
{
  "mission_active": "boolean",
  "mission_id": "string | null",
  "agents_online": "number",
  "system_status": "string (healthy | degraded | offline)"
}
```

## 2. WebSocket Interface

### `WS /ws/platform`
Real-time connection for `PlatformEvent` broadcasting.

**Message Format**:
All messages emitted to the client are strictly validated `PlatformEvent` objects serialized to JSON. The client does not send messages to this socket; it is receive-only.

**Reconnection Strategy**:
Clients must use exponential backoff up to 30 seconds if the socket disconnects.

---
*Note: Any breaking change to these interfaces requires a major version bump and deprecation notice.*
