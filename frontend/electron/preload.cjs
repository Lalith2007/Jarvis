console.log(`[TIMELINE] ${Date.now()} preload.cjs start`);
try {
  const { contextBridge, ipcRenderer } = require("electron");

  contextBridge.exposeInMainWorld("jarvisNative", {
    isNative: true,
    platform: process.platform,
    showDashboard: () => ipcRenderer.invoke("jarvis:show-dashboard"),
    hideDashboard: () => ipcRenderer.invoke("jarvis:hide-dashboard"),
    getWakeDiagnostics: () => ipcRenderer.invoke("jarvis:get-wake-diagnostics"),
    consumePendingWake: () => ipcRenderer.invoke("jarvis:consume-pending-wake"),
    setWakeState: (awake) => ipcRenderer.send("jarvis:wake-state", Boolean(awake)),
    logRuntime: (payload) => ipcRenderer.send("jarvis:runtime-log", payload),
    onNativeCommand: (callback) => {
      const listener = (_event, payload) => callback(payload);
      ipcRenderer.on("jarvis:native-command", listener);
      return () => ipcRenderer.removeListener("jarvis:native-command", listener);
    },
  });
  console.log(`[TIMELINE] ${Date.now()} preload.cjs end`);
} catch (error) {
  console.log(`[TIMELINE] ${Date.now()} preload crash:`, error.stack || error);
}
