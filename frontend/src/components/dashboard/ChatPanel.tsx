import { ArrowUp, MessageSquareText, Mic, Zap } from "lucide-react";
import { type FormEvent, useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { sendChatMessageStream } from "../../services/jarvis-api";
import { useJarvisStore } from "../../stores/use-jarvis-store";
import { usePlatformEvents } from "../../hooks/usePlatformEvents";
import { Panel } from "../ui/Panel";

export function ChatPanel({ full = false }: { full?: boolean }) {
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const messages = useJarvisStore((state) => state.messages);
  const addMessage = useJarvisStore((state) => state.addMessage);
  const updateMessage = useJarvisStore((state) => state.updateMessage);
  const setMode = useJarvisStore((state) => state.setReactorMode);
  const { events } = usePlatformEvents();

  useEffect(() => {
    if (!sending) return;
    const latestEvent = events[events.length - 1];
    if (!latestEvent) return;
    if (latestEvent.event_type === "MemoryRetrievalStarted") {
      setMode("memory");
    } else if (latestEvent.event_type === "AthenaStarted") {
      setMode("routing");
    } else if (latestEvent.event_type === "AthenaCompleted") {
      setMode("thinking");
    }
  }, [events, sending, setMode]);

  // Hold cancel reference so we can abort in-flight streams
  const cancelRef = useRef<(() => void) | null>(null);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    const text = input.trim();
    if (!text || sending) return;

    // Add user message to store
    const userId = crypto.randomUUID();
    addMessage({
      id: userId,
      role: "user",
      content: text,
      createdAt: new Date().toISOString(),
      status: "sent",
    });

    setInput("");
    setSending(true);
    setMode("thinking");

    // Placeholder assistant message that will grow token by token
    const responseId = crypto.randomUUID();
    addMessage({
      id: responseId,
      role: "assistant",
      content: "",
      createdAt: new Date().toISOString(),
      status: "sending",
    });

    let accumulated = "";

    cancelRef.current = sendChatMessageStream(text, {
      onChunk: (chunk) => {
        accumulated += chunk;
        updateMessage(responseId, { content: accumulated, status: "sending" });
        if (accumulated.length === chunk.length) {
          // First chunk received — switch reactor to speaking
          setMode("speaking");
        }
      },
      onDone: (sessionId) => {
        updateMessage(responseId, {
          content: accumulated || "Mission completed.",
          status: "sent",
          // Store session_id in metadata for event correlation
          metadata: { sessionId },
        } as any);
        setSending(false);
        cancelRef.current = null;
        window.setTimeout(() => setMode("idle"), 2200);
      },
      onError: (error) => {
        const isOffline =
          error.includes("fetch") ||
          error.includes("Failed") ||
          error.includes("HTTP");
        updateMessage(responseId, {
          content: isOffline
            ? "I couldn't reach Hermes. Start the FastAPI backend and try again."
            : `Error: ${error}`,
          status: "error",
        });
        setSending(false);
        cancelRef.current = null;
        setMode("error");
        window.setTimeout(() => setMode("idle"), 2200);
      },
    });
  };

  const cancel = () => {
    cancelRef.current?.();
    cancelRef.current = null;
    setSending(false);
    setMode("idle");
  };

  const displayMessages = messages.slice(full ? -30 : -3);

  return (
    <Panel
      title="Chat with JARVIS"
      icon={<MessageSquareText size={15} />}
      className={`chat-panel${full ? " chat-full" : ""}`}
      action={
        <span className="live-label">
          <i /> Hermes
          {sending && (
            <span className="streaming-badge">
              <Zap size={10} /> streaming
            </span>
          )}
        </span>
      }
    >
      <div className="chat-messages" aria-live="polite">
        {displayMessages.map((message) => (
          <article
            key={message.id}
            className={`chat-message ${message.role} ${message.status ?? ""}`}
          >
            <div className="chat-avatar">
              {message.role === "user" ? "LP" : "J"}
            </div>
            <div>
              <span>{message.role === "user" ? "You" : "JARVIS"}</span>
              {message.role === "assistant" ? (
                <div className="chat-markdown">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {message.content}
                  </ReactMarkdown>
                  {message.status === "sending" && (
                    <span className="typing-cursor" aria-hidden="true" />
                  )}
                </div>
              ) : (
                <p>{message.content}</p>
              )}
            </div>
          </article>
        ))}
      </div>
      <form className="chat-composer" onSubmit={submit}>
        <button
          type="button"
          className="icon-button"
          aria-label="Voice input unavailable"
          title="Voice provider pending"
        >
          <Mic size={17} />
        </button>
        <label>
          <span className="sr-only">Message JARVIS</span>
          <input
            id="chat-input"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Type a command…"
            disabled={sending}
          />
        </label>
        {sending ? (
          <button
            className="send-button cancel"
            type="button"
            onClick={cancel}
            aria-label="Cancel streaming"
          >
            ✕
          </button>
        ) : (
          <button
            className="send-button"
            type="submit"
            disabled={!input.trim()}
            aria-label="Send message"
          >
            <ArrowUp size={16} />
          </button>
        )}
      </form>
    </Panel>
  );
}
