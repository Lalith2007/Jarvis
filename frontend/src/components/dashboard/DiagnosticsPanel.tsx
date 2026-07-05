import { useEffect, useState } from "react";
import { TerminalSquare } from "lucide-react";
import { usePlatformEvents } from "../../hooks/usePlatformEvents";
import { useDashboardSnapshot } from "../../hooks/useDashboard";

export function DiagnosticsPanel() {
  const { events } = usePlatformEvents();
  const { data } = useDashboardSnapshot();

  const [sessionInfo, setSessionInfo] = useState({
    sessionId: "None",
    missionId: "None",
    model: "None",
    provider: "None",
    latency: "None",
  });

  const [wakeState, setWakeState] = useState<any>({
    listener_running: "Unknown",
    microphone_permission: "Unknown",
    speech_permission: "Unknown",
    audio_engine_running: "Unknown",
    wake_model_loaded: "Unknown",
    audio_heartbeat_age_ms: null,
    last_confidence: null,
    threshold: null,
    last_detected_phrase: "None",
    last_activation: "None",
    ipc_sent: "None",
    ipc_received: "None",
    window_activation: "None",
    last_error: null,
  });

  useEffect(() => {
    // Scan events for metadata
    const reversed = [...events].reverse();
    const info = { ...sessionInfo };

    const athenaDecision = reversed.find((e) => e.event_type === "AthenaCompleted");
    if (athenaDecision) {
      info.model = athenaDecision.payload?.primary_model ?? "None";
      info.provider = info.model !== "None" && info.model.includes("/") ? info.model.split("/")[0] : "unknown";
      if (athenaDecision.duration_ms) {
        info.latency = `${athenaDecision.duration_ms} ms`;
      }
    }

    const latest = reversed[0];
    if (latest) {
      if (latest.session_id) info.sessionId = latest.session_id;
      if (latest.mission_id) info.missionId = latest.mission_id;
    }

    setSessionInfo(info);
  }, [events]);

  useEffect(() => {
    let interval: number;
    if (window.jarvisNative?.getWakeDiagnostics) {
      window.jarvisNative.getWakeDiagnostics().then(setWakeState).catch(() => {});
      
      const unsubscribe = window.jarvisNative.onNativeCommand?.((payload: any) => {
        if (payload.type === "wake-diagnostics") {
          setWakeState(payload.data);
        }
      });
      
      // Local polling to keep heartbeat age updated
      interval = window.setInterval(() => {
        window.jarvisNative?.getWakeDiagnostics?.().then(setWakeState).catch(() => {});
      }, 1000);
      
      return () => {
        if (unsubscribe) unsubscribe();
        window.clearInterval(interval);
      };
    }
  }, []);

  const getStatusColor = (val: string | null | undefined, successVals: string[] = ["Yes", "Granted", "success"]) => {
    if (!val || val === "Unknown" || val === "None") return "inherit";
    if (successVals.includes(val)) return "#4ade80"; // green
    if (val === "No" || val.startsWith("Denied") || val === "failure") return "#ef4444"; // red
    return "#facc15"; // yellow
  };

  return (
    <div className="diagnostics-panel panel">
      <div className="panel-header">
        <div className="panel-title">
          <TerminalSquare size={14} />
          <b>Developer Diagnostics</b>
        </div>
      </div>
      <div className="panel-content">
        <div className="mini-list">
          <div><span>Backend</span><b>{data?.system ? "Connected" : "Offline"}</b></div>
          <div><span>Event Bus</span><b>{events.length > 0 ? "Active" : "Waiting"}</b></div>
          <div><span>Session ID</span><b>{sessionInfo.sessionId}</b></div>
          <div><span>Mission ID</span><b>{sessionInfo.missionId}</b></div>
          <div><span>Model</span><b>{sessionInfo.model}</b></div>
          <div><span>Provider</span><b>{sessionInfo.provider}</b></div>
          <div><span>Athena Latency</span><b>{sessionInfo.latency}</b></div>
          <div><span>Total Events</span><b>{events.length}</b></div>
        </div>

        <div className="panel-title" style={{ marginTop: 15, marginBottom: 10 }}>
          <TerminalSquare size={14} />
          <b>Wake Diagnostics</b>
        </div>
        <div className="mini-list">
          <div><span>Listener</span><b style={{ color: getStatusColor(wakeState.listener_running) }}>{wakeState.listener_running}</b></div>
          <div><span>Mic Permission</span><b style={{ color: getStatusColor(wakeState.microphone_permission) }}>{wakeState.microphone_permission}</b></div>
          <div><span>Speech Permission</span><b style={{ color: getStatusColor(wakeState.speech_permission) }}>{wakeState.speech_permission}</b></div>
          <div><span>Audio Engine</span><b style={{ color: getStatusColor(wakeState.audio_engine_running) }}>{wakeState.audio_engine_running}</b></div>
          <div><span>Wake Model</span><b style={{ color: getStatusColor(wakeState.wake_model_loaded) }}>{wakeState.wake_model_loaded}</b></div>
          
          <div>
            <span>Heartbeat Age</span>
            <b style={{ color: (wakeState.audio_heartbeat_age_ms ?? 99999) < 10000 ? "#4ade80" : "#ef4444" }}>
              {wakeState.audio_heartbeat_age_ms != null ? `${wakeState.audio_heartbeat_age_ms} ms` : "None"}
            </b>
          </div>
          
          <div><span>Last Phrase</span><b>{wakeState.last_detected_phrase}</b></div>
          <div><span>Last Confidence</span><b>{wakeState.last_confidence ?? "None"}</b></div>
          <div><span>Threshold</span><b>{wakeState.threshold ?? "None"}</b></div>
          
          <div><span>IPC Sent</span><b>{wakeState.ipc_sent ? new Date(wakeState.ipc_sent).toLocaleTimeString() : "None"}</b></div>
          <div><span>IPC Received</span><b>{wakeState.ipc_received ? new Date(wakeState.ipc_received).toLocaleTimeString() : "None"}</b></div>
          <div><span>Window Activation</span><b>{wakeState.window_activation ? new Date(wakeState.window_activation).toLocaleTimeString() : "None"}</b></div>
          
          {wakeState.last_error && (
            <div style={{ color: "#ef4444", marginTop: 5, fontSize: "0.85em", wordBreak: "break-all" }}>
              Error: {wakeState.last_error}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
