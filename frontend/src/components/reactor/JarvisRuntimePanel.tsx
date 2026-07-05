import { Moon, Power, Radio, ShieldCheck, Volume2, Waves } from "lucide-react";
import { useJarvisVoiceRuntime } from "../../hooks/use-jarvis-voice-runtime";

const statusCopy: Record<string, string> = {
  offline: "System offline",
  arming: "Requesting microphone access",
  armed: "Armed: say Hey Jarvis",
  awake: "Standby",
  listening: "Listening",
  processing: "Reasoning",
  speaking: "Speaking",
  error: "Runtime attention required",
};

export function JarvisRuntimePanel() {
  const { arm, sleep, armed, status, supported, lastHeard, audioLevel, error } = useJarvisVoiceRuntime();
  const awake = ["awake", "listening", "processing", "speaking"].includes(status);
  const nativeShell = Boolean(window.jarvisNative);

  return (
    <div className={`jarvis-runtime-panel state-${status}`} aria-label="Automatic JARVIS runtime controller" data-runtime-state={status}>
      <div className="runtime-rail">
        <span className="runtime-orb"><Radio size={13} /></span>
        <span>
          <b>{statusCopy[status]}</b>
          <small>{error ?? (supported ? "Automatic reactor control active" : "Speech recognition is not supported in this browser")}</small>
        </span>
      </div>

      <div className="audio-meter" aria-label={`Audio input level ${Math.round(audioLevel * 100)} percent`}>
        <i style={{ transform: `scaleX(${audioLevel})` }} />
      </div>

      <div className="runtime-signals">
        <span><Waves size={12} /> Wake phrase active</span>
        <span><Volume2 size={12} /> {lastHeard ? `Heard: ${lastHeard.slice(0, 32)}` : "Awaiting voice"}</span>
        <span><ShieldCheck size={12} /> {nativeShell ? "Native shell" : armed ? "Mic armed" : "Mic offline"}</span>
      </div>

      <div className="runtime-actions">
        {!armed && (
          <button className="runtime-primary" onClick={arm} disabled={status === "arming"}>
            <Power size={13} /> Arm JARVIS audio
          </button>
        )}
        {armed && awake && (
          <button className="runtime-secondary" onClick={sleep}>
            <Moon size={13} /> Sleep
          </button>
        )}
      </div>
    </div>
  );
}
