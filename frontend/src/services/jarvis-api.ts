import axios from "axios";
import { FrontendConfig } from "../../electron/config.cjs";

// In Electron, FrontendConfig.API_BASE = "http://127.0.0.1:8000/api"
// In browser dev mode, proxy handles /api prefix
const baseURL: string = import.meta.env.VITE_API_URL
  ?? (window.jarvisNative ? FrontendConfig.API_BASE : "/api");

const api = axios.create({
  baseURL,
  timeout: 60_000,
  headers: { "Content-Type": "application/json" },
});

/** Blocking chat — preserved for backward compatibility. */
export async function sendChatMessage(message: string): Promise<string> {
  const { data } = await api.post<{ response: string }>("/chat", { message });
  return data.response;
}

export interface ChatStreamCallbacks {
  onChunk: (chunk: string) => void;
  onDone: (sessionId: string) => void;
  onError: (error: string) => void;
}

/**
 * Streaming chat via Server-Sent Events.
 *
 * Opens a POST /api/chat/stream request and calls callbacks as tokens arrive.
 * Returns a cancel function that aborts the request.
 */
export function sendChatMessageStream(
  message: string,
  callbacks: ChatStreamCallbacks,
  sessionId?: string,
): () => void {
  const controller = new AbortController();

  const streamURL: string = window.jarvisNative
    ? `${FrontendConfig.API_BASE}/chat/stream`
    : "/api/chat/stream";

  fetch(streamURL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId ?? undefined }),
    signal: controller.signal,
  })
    .then(async (res) => {
      if (!res.ok || !res.body) {
        callbacks.onError(`HTTP ${res.status}`);
        return;
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        // SSE format: "data: <json>\n\n"
        const lines = buffer.split("\n\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          try {
            const payload = JSON.parse(line.slice(6));
            if (payload.type === "chunk") {
              callbacks.onChunk(payload.content);
            } else if (payload.type === "done") {
              callbacks.onDone(payload.session_id ?? "");
            } else if (payload.type === "error") {
              callbacks.onError(payload.content);
            }
          } catch {
            // ignore malformed SSE lines
          }
        }
      }
    })
    .catch((err) => {
      if (err.name !== "AbortError") {
        callbacks.onError(err.message ?? "Stream failed");
      }
    });

  return () => controller.abort();
}

export { api };
