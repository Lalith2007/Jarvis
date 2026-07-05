const fs = require("node:fs");
const path = require("node:path");
const os = require("node:os");

const nativeLogDir = path.join(os.homedir(), "Library", "Logs", "JARVIS");
const wakeLogPath = path.join(nativeLogDir, "wake.log");
const MAX_LOG_SIZE = 10 * 1024 * 1024; // 10 MB

class WakeDiagnosticsService {
  constructor() {
    this.state = {
      listener_running: "No",
      microphone_permission: "Unknown",
      speech_permission: "Unknown",
      audio_engine_running: "Unknown",
      wake_model_loaded: "Unknown",
      last_audio_frame: null,
      audio_heartbeat_age_ms: null,
      last_confidence: null,
      threshold: null,
      last_detected_phrase: null,
      last_activation: null,
      ipc_sent: null,
      ipc_received: null,
      window_activation: null,
      last_error: null,
    };
    this.onStateChange = null;
    this.enabled = process.env.DEBUG_WAKE === "1" || process.env.JARVIS_ELECTRON_DEV === "1";
    
    // Setup directory
    try {
      fs.mkdirSync(nativeLogDir, { recursive: true });
    } catch {}
  }

  rotateLogIfNeeded() {
    try {
      if (!fs.existsSync(wakeLogPath)) return;
      const stats = fs.statSync(wakeLogPath);
      if (stats.size >= MAX_LOG_SIZE) {
        for (let i = 4; i >= 1; i--) {
          const oldFile = `${wakeLogPath}.${i}`;
          const newFile = `${wakeLogPath}.${i + 1}`;
          if (fs.existsSync(oldFile)) {
            fs.renameSync(oldFile, newFile);
          }
        }
        if (fs.existsSync(wakeLogPath)) {
          fs.renameSync(wakeLogPath, `${wakeLogPath}.1`);
        }
      }
    } catch (e) {
      console.error("Log rotation error:", e);
    }
  }

  writeLog(stage, status, details = {}) {
    if (!this.enabled) return;
    
    this.rotateLogIfNeeded();
    
    const entry = {
      timestamp: new Date().toISOString(),
      stage,
      status,
      details
    };
    
    try {
      fs.appendFileSync(wakeLogPath, JSON.stringify(entry) + "\n");
    } catch (e) {
      console.error("Failed to write to wake.log", e);
    }
  }

  updateState(updates) {
    let changed = false;
    for (const [key, value] of Object.entries(updates)) {
      if (this.state[key] !== value) {
        this.state[key] = value;
        changed = true;
      }
    }
    
    if (changed && this.onStateChange) {
      // Recalculate age before sending
      const snapshot = this.getSnapshot();
      this.onStateChange(snapshot);
    }
  }

  getSnapshot() {
    const snap = { ...this.state };
    if (snap.last_audio_frame) {
      snap.audio_heartbeat_age_ms = Date.now() - new Date(snap.last_audio_frame).getTime();
    }
    return snap;
  }
}

const wakeDiagnostics = new WakeDiagnosticsService();
module.exports = { wakeDiagnostics };
