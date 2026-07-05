import { useCallback, useEffect, useRef, useState } from "react";
import { sendChatMessage } from "../services/jarvis-api";
import { useJarvisStore } from "../stores/use-jarvis-store";
import type { ReactorMode } from "../types/jarvis";

type RuntimeStatus =
  | "offline"
  | "arming"
  | "armed"
  | "awake"
  | "listening"
  | "processing"
  | "speaking"
  | "error";

type SpeechRecognitionConstructor = new () => SpeechRecognitionLike;

interface SpeechRecognitionEventLike extends Event {
  resultIndex: number;
  results: {
    length: number;
    [index: number]: {
      isFinal: boolean;
      [index: number]: { transcript: string };
    };
  };
}

interface SpeechRecognitionLike extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onresult: ((event: SpeechRecognitionEventLike) => void) | null;
  onend: (() => void) | null;
  onerror: (() => void) | null;
  start: () => void;
  stop: () => void;
}

type WindowWithSpeechRecognition = Window & {
  SpeechRecognition?: SpeechRecognitionConstructor;
  webkitSpeechRecognition?: SpeechRecognitionConstructor;
};

const SILENCE_TO_STANDBY_MS = 1_500;

function classifyCommand(text: string): { mode: ReactorMode; sector: string } {
  const normalized = text.toLowerCase();
  if (/\b(browser|browse|website|web|open|google|search online|internet)\b/.test(normalized)) {
    return { mode: "browsing", sector: "browser" };
  }
  if (/\b(memory|remember|recall|vault|knowledge|note|notes)\b/.test(normalized)) {
    return { mode: "memory", sector: "memory" };
  }
  if (/\b(code|build|fix|file|repository|repo|terminal|script|function|component)\b/.test(normalized)) {
    return { mode: "coding", sector: "coding" };
  }
  if (/\b(collaborate|models|athena|deepseek|nemotron|minimax|compare|debate)\b/.test(normalized)) {
    return { mode: "collaborating", sector: "models" };
  }
  return { mode: "thinking", sector: "athena" };
}

function stripWakePhrase(text: string) {
  return text.replace(/\b(?:hey\s+)?jarvis\b/gi, "").replace(/\s+/g, " ").trim();
}

function runtimeLog(event: string, details: Record<string, unknown> = {}) {
  window.jarvisNative?.logRuntime({ event, ...details });
}

function greeting() {
  const hour = new Date().getHours();
  const part = hour < 12 ? "morning" : hour < 18 ? "afternoon" : "evening";
  return `Good ${part}, Lalith. JARVIS is online.`;
}

export function useJarvisVoiceRuntime() {
  const [status, setStatus] = useState<RuntimeStatus>("offline");
  const [armed, setArmed] = useState(false);
  const [supported, setSupported] = useState(true);
  const [lastHeard, setLastHeard] = useState("");
  const [audioLevel, setAudioLevel] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [awake, setAwake] = useState(false);

  const setMode = useJarvisStore((state) => state.setReactorMode);
  const setRuntimeAwake = useJarvisStore((state) => state.setRuntimeAwake);
  const addMessage = useJarvisStore((state) => state.addMessage);
  const updateMessage = useJarvisStore((state) => state.updateMessage);

  const awakeRef = useRef(false);
  const armedRef = useRef(false);
  const statusRef = useRef<RuntimeStatus>("offline");
  const nativeShellRef = useRef(false);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);
  const audioLoopRef = useRef<number | null>(null);
  const lastAudioDiagnosticAtRef = useRef(0);
  const lastVoiceAtRef = useRef(0);
  const startRecognitionRef = useRef<(() => void) | null>(null);
  const speakingRef = useRef(false);
  const submittingRef = useRef(false);

  const updateStatus = useCallback((next: RuntimeStatus) => {
    statusRef.current = next;
    setStatus(next);
  }, []);

  const speak = useCallback((text: string) => {
    speakingRef.current = true;
    updateStatus("speaking");
    setMode("speaking");

    const finish = () => {
      speakingRef.current = false;
      if (awakeRef.current) {
        updateStatus("awake");
        setMode("idle");
      } else {
        updateStatus("offline");
        setMode("offline");
      }
    };

    if (!("speechSynthesis" in window)) {
      globalThis.setTimeout(finish, 1800);
      return;
    }

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.95;
    utterance.pitch = 0.86;
    utterance.volume = 0.95;
    utterance.onend = finish;
    utterance.onerror = finish;
    window.speechSynthesis.speak(utterance);
  }, [setMode, updateStatus]);

  const submitCommand = useCallback(async (text: string) => {
    const clean = stripWakePhrase(text);
    if (!clean || submittingRef.current) return;

    submittingRef.current = true;
    const route = classifyCommand(clean);
    updateStatus("processing");
    setMode(route.mode, route.sector);

    const userId = crypto.randomUUID();
    const responseId = crypto.randomUUID();
    addMessage({ id: userId, role: "user", content: clean, createdAt: new Date().toISOString(), status: "sent" });
    addMessage({ id: responseId, role: "assistant", content: "Athena is routing this request…", createdAt: new Date().toISOString(), status: "sending" });

    try {
      const response = await sendChatMessage(clean);
      updateMessage(responseId, { content: response, status: "sent" });
      speak(response);
    } catch {
      const fallback = "Hermes is unreachable. Start the FastAPI backend and I will retry.";
      updateMessage(responseId, { content: fallback, status: "error" });
      updateStatus("error");
      setMode("error");
      speak(fallback);
    } finally {
      submittingRef.current = false;
    }
  }, [addMessage, setMode, speak, updateMessage, updateStatus]);

  const wake = useCallback((initialCommand?: string) => {
    if (!awakeRef.current) {
      awakeRef.current = true;
      setAwake(true);
      setRuntimeAwake(true);
      window.jarvisNative?.setWakeState(true);
      void window.jarvisNative?.showDashboard();
      
      setTimeout(() => {
        document.getElementById("chat-input")?.focus();
      }, 100);

      updateStatus("awake");
      setMode("speaking");
      const line = greeting();
      addMessage({ id: crypto.randomUUID(), role: "assistant", content: line, createdAt: new Date().toISOString(), status: "sent" });
      speak(line);
    }

    if (initialCommand) {
      window.setTimeout(() => {
        void submitCommand(initialCommand);
      }, 850);
    }
  }, [addMessage, setMode, setRuntimeAwake, speak, submitCommand, updateStatus]);

  const handleTranscript = useCallback((rawText: string, isFinal: boolean) => {
    const text = rawText.trim();
    if (!text) return;
    setLastHeard(text);

    const normalized = text.toLowerCase();
    const hasWakePhrase = /\b(?:hey\s+)?jarvis\b/.test(normalized);

    if (!awakeRef.current) {
      if (hasWakePhrase) {
        runtimeLog("wake-phrase-detected", { text });
        const command = stripWakePhrase(text);
        wake(command);
      }
      return;
    }

    if (isFinal) {
      const command = stripWakePhrase(text);
      if (command && !/^jarvis$/i.test(command)) {
        void submitCommand(command);
      }
    }
  }, [submitCommand, wake]);

  const startRecognition = useCallback(() => {
    if (nativeShellRef.current && !awakeRef.current) return;
    if (recognitionRef.current) return;

    const SpeechRecognition = (window as WindowWithSpeechRecognition).SpeechRecognition ?? (window as WindowWithSpeechRecognition).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setSupported(false);
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";
    recognition.onresult = (event) => {
      for (let index = event.resultIndex; index < event.results.length; index += 1) {
        const result = event.results[index];
        handleTranscript(result[0].transcript, result.isFinal);
      }
    };
    recognition.onerror = () => {
      runtimeLog("speech-recognition-error");
      setError("Speech recognition paused. JARVIS will try to resume automatically.");
    };
    recognition.onend = () => {
      recognitionRef.current = null;
      if (armedRef.current && (!nativeShellRef.current || awakeRef.current)) {
        window.setTimeout(() => {
          try {
            recognition.start();
            recognitionRef.current = recognition;
            runtimeLog("speech-recognition-restarted");
          } catch {
            // Recognition can throw if the browser is already restarting it.
          }
        }, 450);
      }
    };
    recognitionRef.current = recognition;
    try {
      recognition.start();
      runtimeLog("speech-recognition-started");
    } catch {
      runtimeLog("speech-recognition-start-failed");
      setError("Speech recognition could not start.");
    }
  }, [handleTranscript]);

  useEffect(() => {
    startRecognitionRef.current = startRecognition;
  }, [startRecognition]);

  const processAudioFrame = useCallback(function tick() {
    const analyser = analyserRef.current;
    if (!analyser) return;
    const audioContext = audioContextRef.current;

    if (audioContext?.state === "suspended") {
      void audioContext.resume();
    }

    const samples = new Uint8Array(analyser.fftSize);
    analyser.getByteTimeDomainData(samples);

    let peak = 0;
    let sum = 0;
    for (const sample of samples) {
      const centered = Math.abs(sample - 128) / 128;
      peak = Math.max(peak, centered);
      sum += centered * centered;
    }

    const rms = Math.sqrt(sum / samples.length);
    setAudioLevel(Math.min(1, rms * 7));

    const now = Date.now();
    if (window.jarvisNative && now - lastAudioDiagnosticAtRef.current > 5_000) {
      lastAudioDiagnosticAtRef.current = now;
      runtimeLog("audio-monitor", {
        peak: Number(peak.toFixed(3)),
        rms: Number(rms.toFixed(3)),
        level: Number(Math.min(1, rms * 7).toFixed(3)),
        status: statusRef.current,
        audioState: audioContext?.state ?? "unknown",
      });
    }

    if (awakeRef.current && !speakingRef.current && !submittingRef.current) {
      if (rms > 0.025) {
        lastVoiceAtRef.current = now;
        if (statusRef.current !== "listening") {
          updateStatus("listening");
          setMode("listening");
        }
      } else if (now - lastVoiceAtRef.current > SILENCE_TO_STANDBY_MS && statusRef.current === "listening") {
        updateStatus("awake");
        setMode("idle");
      }
    }
  }, [setMode, updateStatus]);

  const arm = useCallback(async () => {
    setError(null);
    updateStatus("arming");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: false,
        },
      });
      runtimeLog("microphone-granted");
      const AudioContextClass = window.AudioContext ?? (window as Window & { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
      if (!AudioContextClass) throw new Error("AudioContext unavailable");
      const audioContext = new AudioContextClass();
      await audioContext.resume();
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 1024;
      analyser.smoothingTimeConstant = 0.18;
      const source = audioContext.createMediaStreamSource(stream);
      source.connect(analyser);
      const [track] = stream.getAudioTracks();
      runtimeLog("microphone-track", {
        label: track?.label ?? "unknown",
        enabled: track?.enabled ?? false,
        muted: track?.muted ?? false,
        readyState: track?.readyState ?? "unknown",
        audioState: audioContext.state,
        settings: track?.getSettings?.() ?? {},
      });

      mediaStreamRef.current = stream;
      audioContextRef.current = audioContext;
      analyserRef.current = analyser;
      armedRef.current = true;
      setArmed(true);
      updateStatus("armed");
      setMode("offline");
      startRecognitionRef.current?.();
      if (audioLoopRef.current) window.clearInterval(audioLoopRef.current);
      audioLoopRef.current = window.setInterval(processAudioFrame, 50);
      runtimeLog("audio-loop-started", { intervalMs: 50 });
    } catch (caught) {
      const message = caught instanceof Error ? caught.message : "Microphone permission denied.";
      runtimeLog("microphone-error", { message });
      setError(message);
      updateStatus("error");
      setMode("error");
    }
  }, [processAudioFrame, setMode, updateStatus]);

  const sleep = useCallback(() => {
    awakeRef.current = false;
    setAwake(false);
    setRuntimeAwake(false);
    window.jarvisNative?.setWakeState(false);
    speakingRef.current = false;
    submittingRef.current = false;
    updateStatus(armed ? "armed" : "offline");
    setMode("offline");
    if ("speechSynthesis" in window) window.speechSynthesis.cancel();
    if (nativeShellRef.current) {
      recognitionRef.current?.stop();
      recognitionRef.current = null;
    }
  }, [armed, setMode, setRuntimeAwake, updateStatus]);

  useEffect(() => () => {
    armedRef.current = false;
    if (audioLoopRef.current) window.clearInterval(audioLoopRef.current);
    recognitionRef.current?.stop();
    mediaStreamRef.current?.getTracks().forEach((track) => track.stop());
    void audioContextRef.current?.close();
  }, []);

  useEffect(() => {
    nativeShellRef.current = Boolean(window.jarvisNative);
  }, []);

  useEffect(() => {
    if (!window.jarvisNative || armedRef.current) return undefined;
    if (window.localStorage.getItem("jarvis-native-auto-arm") === "0") return undefined;

    const timer = window.setTimeout(() => {
      if (!armedRef.current && statusRef.current === "offline") {
        runtimeLog("native-auto-arm");
        void arm();
      }
    }, 900);

    return () => window.clearTimeout(timer);
  }, [arm]);

  useEffect(() => {
    if (!window.jarvisNative) return undefined;
    void window.jarvisNative.consumePendingWake().then((reason) => {
      if (reason && !awakeRef.current) {
        runtimeLog("pending-wake-received", { reason });
        wake();
      }
    });
    return window.jarvisNative.onNativeCommand((payload) => {
      runtimeLog("native-command", { type: payload.type });
      if (payload.type === "native-wake-word" && !awakeRef.current) {
        wake();
      }
      if (payload.type === "system-resume" && !awakeRef.current) {
        updateStatus(armedRef.current ? "armed" : "offline");
        setMode("offline");
      }
      if (payload.type === "hide-dashboard" && !awakeRef.current) {
        updateStatus(armedRef.current ? "armed" : "offline");
      }
      if (payload.type === "show-dashboard" && !awakeRef.current) {
        updateStatus(armedRef.current ? "armed" : "offline");
        setMode("offline");
      }
    });
  }, [setMode, updateStatus, wake]);

  return {
    arm,
    sleep,
    armed,
    awake,
    status,
    supported,
    lastHeard,
    audioLevel,
    error,
  };
}
