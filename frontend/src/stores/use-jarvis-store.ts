import { create } from "zustand";
import type { ChatMessage, ReactorMode } from "../types/jarvis";

interface JarvisState {
  reactorMode: ReactorMode;
  activeSector: string | null;
  runtimeAwake: boolean;
  sidebarOpen: boolean;
  commandPaletteOpen: boolean;
  messages: ChatMessage[];
  setReactorMode: (mode: ReactorMode, sector?: string | null) => void;
  setRuntimeAwake: (awake: boolean) => void;
  setSidebarOpen: (open: boolean) => void;
  setCommandPaletteOpen: (open: boolean) => void;
  addMessage: (message: ChatMessage) => void;
  updateMessage: (id: string, patch: Partial<ChatMessage>) => void;
}

export const useJarvisStore = create<JarvisState>((set) => ({
  reactorMode: "offline",
  activeSector: null,
  runtimeAwake: false,
  sidebarOpen: false,
  commandPaletteOpen: false,
  messages: [
    { id: "welcome", role: "system", content: "JARVIS is offline. Say Hey Jarvis to wake the system.", createdAt: new Date().toISOString(), status: "sent" },
  ],
  setReactorMode: (reactorMode, activeSector = null) => set({ reactorMode, activeSector }),
  setRuntimeAwake: (runtimeAwake) => set({ runtimeAwake }),
  setSidebarOpen: (sidebarOpen) => set({ sidebarOpen }),
  setCommandPaletteOpen: (commandPaletteOpen) => set({ commandPaletteOpen }),
  addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
  updateMessage: (id, patch) => set((state) => ({ messages: state.messages.map((message) => message.id === id ? { ...message, ...patch } : message) })),
}));
