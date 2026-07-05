const { spawn, spawnSync } = require("node:child_process");
const fs = require("node:fs");
const path = require("node:path");
const os = require("node:os");

const isDev = process.env.JARVIS_ELECTRON_DEV === "1";
const appDisplayName = "J.A.R.V.I.S";
const { FrontendConfig } = require("./config.cjs");
const devUrl = process.env.JARVIS_FRONTEND_URL || FrontendConfig.FRONTEND_DEV_DASHBOARD;
const { app, BrowserWindow, Menu, Tray, globalShortcut, ipcMain, nativeImage, powerMonitor, session } = require("electron");
const { wakeDiagnostics } = require("./wake-diagnostics.cjs");

function findBackendDir(startPath) {
  let current = startPath;
  while (current !== "/" && current !== ".") {
    const candidate = require("node:path").join(current, "backend");
    if (require("node:fs").existsSync(candidate)) return candidate;
    current = require("node:path").dirname(current);
  }
  return require("node:path").join(startPath, "backend"); // fallback
}

const backendDir = findBackendDir(__dirname);
const launchedByAgent = process.env.JARVIS_LAUNCH_AGENT === "1";
const startHidden = process.env.JARVIS_START_HIDDEN === "1" || (launchedByAgent && process.env.JARVIS_START_HIDDEN !== "0");

let mainWindow = null;
let tray = null;
let isQuitting = false;
let backendProcess = null;
let wakeProcess = null;
let wakeHelperPermissionBlocked = false;
let pendingWakeReason = null;
const nativeLogDir = path.join(os.homedir(), "Library", "Logs", "JARVIS");
const runtimeLogPath = path.join(nativeLogDir, "runtime.log");
const unpackedDirname = __dirname.includes("app.asar") ? __dirname.replace("app.asar", "app.asar.unpacked") : __dirname;
const wakeSourcePath = path.join(__dirname, "macos", "JarvisWakeListener.swift");
const wakeInfoPlistPath = path.join(__dirname, "macos", "JarvisWakeListener-Info.plist");
const wakeBuildDir = path.join(unpackedDirname, "macos", "bin");
let wakeBinaryPath;
if (app.isPackaged) {
  wakeBinaryPath = path.join(process.execPath, "..", "jarvis-wake-listener");
} else {
  wakeBinaryPath = path.join(wakeBuildDir, "jarvis-wake-listener");
}

function logNative(message, details = undefined) {
  const line = `[${new Date().toISOString()}] ${message}${details ? ` ${JSON.stringify(details)}` : ""}\n`;
  try {
    fs.mkdirSync(nativeLogDir, { recursive: true });
    fs.appendFileSync(runtimeLogPath, line);
  } catch {
    // Logging should never prevent JARVIS from starting.
  }
  if (isDev) process.stdout.write(line);
}

function getPythonExecutable() {
  const venvPython = process.platform === "win32"
    ? path.join(backendDir, ".venv", "Scripts", "python.exe")
    : path.join(backendDir, ".venv", "bin", "python");
  if (fs.existsSync(venvPython)) return venvPython;
  return "python3";
}

async function isBackendOnline() {
  try {
    const response = await fetch(FrontendConfig.API_DASHBOARD, { method: "GET" });
    return response.ok;
  } catch {
    return false;
  }
}

async function ensureBackend() {
  if (await isBackendOnline()) {
    logNative("backend-online");
    return;
  }
  const python = getPythonExecutable();
  logNative("backend-starting", { python, backendDir });
  backendProcess = spawn(python, ["-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"], {
    cwd: backendDir,
    env: { ...process.env },
    stdio: isDev ? "inherit" : "ignore",
  });
  backendProcess.on("exit", () => {
    logNative("backend-exit");
    backendProcess = null;
  });
}

function ensureWakeHelperBuilt() {
  if (process.platform !== "darwin") {
    logNative("wake-helper-skipped", { reason: "not-darwin", platform: process.platform });
    return false;
  }
  if (process.env.JARVIS_DISABLE_NATIVE_WAKE === "1") {
    logNative("wake-helper-skipped", { reason: "disabled-env" });
    return false;
  }
  if (app.isPackaged) {
    if (fs.existsSync(wakeBinaryPath)) return true;
    logNative("wake-helper-build-failed", { reason: "missing-packaged-binary", binary: wakeBinaryPath });
    return false;
  }

  if (!fs.existsSync(wakeSourcePath)) {
    logNative("wake-helper-skipped", { reason: "missing-source", wakeSourcePath });
    return false;
  }

  const sourceStat = fs.statSync(wakeSourcePath);
  const plistStat = fs.existsSync(wakeInfoPlistPath) ? fs.statSync(wakeInfoPlistPath) : sourceStat;
  const binaryFresh = fs.existsSync(wakeBinaryPath)
    && fs.statSync(wakeBinaryPath).mtimeMs >= sourceStat.mtimeMs
    && fs.statSync(wakeBinaryPath).mtimeMs >= plistStat.mtimeMs;
  if (binaryFresh) return true;

  fs.mkdirSync(wakeBuildDir, { recursive: true });
  logNative("wake-helper-building", { source: wakeSourcePath, binary: wakeBinaryPath });
  const args = ["swiftc", wakeSourcePath, "-o", wakeBinaryPath];
  if (fs.existsSync(wakeInfoPlistPath)) {
    args.push("-Xlinker", "-sectcreate", "-Xlinker", "__TEXT", "-Xlinker", "__info_plist", "-Xlinker", wakeInfoPlistPath);
  }
  const result = spawnSync("xcrun", args, {
    cwd: path.dirname(wakeSourcePath),
    encoding: "utf8",
  });
  if (result.status !== 0) {
    logNative("wake-helper-build-failed", { stdout: result.stdout, stderr: result.stderr });
    return false;
  }
  logNative("wake-helper-built", { binary: wakeBinaryPath });
  return true;
}

function startWakeHelper() {
  logNative("wake-helper-start-requested");
  wakeDiagnostics.updateState({ listener_running: "Yes" });
  wakeDiagnostics.writeLog("wake-listener", "success", { action: "start-requested" });
  if (wakeProcess) {
    logNative("wake-helper-skipped", { reason: "already-running", pid: wakeProcess.pid });
    return;
  }
  if (!ensureWakeHelperBuilt()) return;

  wakeProcess = spawn(wakeBinaryPath, [], {
    cwd: path.dirname(wakeBinaryPath),
    stdio: ["ignore", "pipe", "pipe"],
  });
  logNative("wake-helper-started", { pid: wakeProcess.pid });

  wakeProcess.stdout.on("data", (chunk) => {
    const lines = chunk.toString("utf8").split(/\r?\n/).filter(Boolean);
    for (const line of lines) {
      if (line.startsWith("[WAKE]")) {
        logNative("wake-helper-stdout", { message: line });
        continue;
      }
      try {
        const payload = JSON.parse(line);
        logNative("wake-helper", payload);
        
        // Update Wake Diagnostics State
        const now = new Date().toISOString();
        if (payload.event === "error") {
          wakeDiagnostics.updateState({ last_error: payload.message });
          wakeDiagnostics.writeLog("wake-helper", "failure", { error: payload.message });
          if (/permission denied/i.test(String(payload.message ?? ""))) {
            wakeHelperPermissionBlocked = true;
          }
        } else if (payload.event === "speech-permission") {
          const status = payload.status === "3" ? "Granted" : `Denied (${payload.status})`;
          wakeDiagnostics.updateState({ speech_permission: status });
          wakeDiagnostics.writeLog("speech-permission", status === "Granted" ? "success" : "failure", payload);
        } else if (payload.event === "microphone-permission") {
          const status = payload.granted === "true" ? "Granted" : "Denied";
          wakeDiagnostics.updateState({ microphone_permission: status });
          wakeDiagnostics.writeLog("microphone-permission", status === "Granted" ? "success" : "failure", payload);
        } else if (payload.event === "heartbeat") {
          wakeDiagnostics.updateState({
            audio_engine_running: payload.engine_running === "true" ? "Yes" : "No",
            last_audio_frame: now
          });
          wakeDiagnostics.writeLog("audio-heartbeat", "success", payload);
        } else if (payload.event === "wake-confidence") {
          wakeDiagnostics.updateState({
            last_confidence: payload.confidence,
            threshold: payload.threshold,
            last_detected_phrase: payload.phrase
          });
          wakeDiagnostics.writeLog("wake-confidence", payload.status, payload);
        } else if (payload.event === "wake") {
          wakeDiagnostics.updateState({ ipc_sent: now });
          wakeDiagnostics.writeLog("ipc-emitted", "success", { command: payload.command });
          
          console.log(`[WAKE] ${now} IPC message received success`);
          wakeDiagnostics.updateState({ ipc_received: now });
          wakeDiagnostics.writeLog("ipc-received", "success", { command: payload.command });
          
          wakeDashboard("native-wake-word");
        } else if (payload.event === "ready") {
          wakeDiagnostics.updateState({ wake_model_loaded: "Yes" });
          wakeDiagnostics.writeLog("wake-model-loaded", "success", payload);
        }
      } catch {
        logNative("wake-helper-output", { line });
      }
    }
  });

  wakeProcess.stderr.on("data", (chunk) => {
    const message = chunk.toString("utf8").trim();
    logNative("wake-helper-error", { message });
    wakeDiagnostics.updateState({ last_error: message });
    wakeDiagnostics.writeLog("wake-helper-stderr", "failure", { message });
  });

  wakeProcess.on("exit", (code, signal) => {
    logNative("wake-helper-exit", { code, signal });
    wakeDiagnostics.updateState({ listener_running: "No" });
    wakeDiagnostics.writeLog("wake-listener", "exit", { code, signal });
    
    wakeProcess = null;
    if (!isQuitting && !wakeHelperPermissionBlocked) {
      setTimeout(startWakeHelper, 1500);
    }
  });
}

function createTray() {
  const icon = nativeImage.createFromDataURL(
    "data:image/svg+xml;base64," +
      Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#02070d"/><circle cx="32" cy="32" r="24" fill="none" stroke="#08c8ff" stroke-width="3"/><circle cx="32" cy="32" r="11" fill="none" stroke="#82edff" stroke-width="2"/><circle cx="32" cy="32" r="4" fill="#08c8ff"/></svg>`).toString("base64")
  );
  tray = new Tray(icon);
  tray.setToolTip(appDisplayName);
  tray.setContextMenu(Menu.buildFromTemplate([
    { label: `Show ${appDisplayName}`, click: showDashboard },
    { label: "Hide Dashboard", click: hideDashboard },
    { type: "separator" },
    { label: `Quit ${appDisplayName}`, click: () => { isQuitting = true; app.quit(); } },
  ]));
  tray.on("click", showDashboard);
}

function showDashboard() {
  if (!mainWindow) return;
  const now = new Date().toISOString();
  console.log(`[WAKE] ${now} showDashboard() invoked`);
  wakeDiagnostics.writeLog("show-dashboard", "success");
  
  logNative("dashboard-show");
  if (mainWindow.isMinimized()) mainWindow.restore();
  if (!mainWindow.isVisible()) mainWindow.show();
  
  console.log(`[WAKE] ${new Date().toISOString()} BrowserWindow.show() invoked`);
  wakeDiagnostics.writeLog("browser-window-show", "success");
  mainWindow.show();
  
  console.log(`[WAKE] ${new Date().toISOString()} BrowserWindow.focus() invoked`);
  wakeDiagnostics.writeLog("browser-window-focus", "success");
  mainWindow.focus();
  app.show();
  
  console.log(`[WAKE] ${new Date().toISOString()} app.focus() invoked`);
  wakeDiagnostics.writeLog("app-focus", "success");
  app.focus({ steal: true });
  
  console.log(`[WAKE] ${new Date().toISOString()} Window focused success`);
  wakeDiagnostics.updateState({ window_activation: new Date().toISOString(), last_activation: now });
  wakeDiagnostics.writeLog("window-focused", "success");
  
  mainWindow.webContents.send("jarvis:native-command", { type: "show-dashboard" });
}

function wakeDashboard(reason = "native-wake-word") {
  pendingWakeReason = reason;
  showDashboard();
  mainWindow?.webContents.send("jarvis:native-command", { type: "native-wake-word", reason });
}

function hideDashboard() {
  if (!mainWindow) return;
  logNative("dashboard-hide");
  mainWindow.hide();
  mainWindow.webContents.send("jarvis:native-command", { type: "hide-dashboard" });
}

async function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1720,
    height: 980,
    minWidth: 1180,
    minHeight: 760,
    backgroundColor: "#02070d",
    title: appDisplayName,
    show: false,
    webPreferences: {
      preload: path.join(__dirname, "preload.cjs"),
      contextIsolation: true,
      nodeIntegration: false,
      backgroundThrottling: false,
    },
  });

  mainWindow.on("close", (event) => {
    if (!isQuitting) {
      event.preventDefault();
      hideDashboard();
    }
  });

  mainWindow.once("ready-to-show", () => {
    if (startHidden) {
      logNative("window-ready-hidden");
      mainWindow.hide();
      mainWindow.webContents.send("jarvis:native-command", { type: "background-start" });
      return;
    }
    logNative("window-ready-visible");
    showDashboard();
    // mainWindow.webContents.openDevTools({ mode: 'detach' });
  });

  logNative("BrowserWindow-created");
  mainWindow.webContents.on('did-start-loading', () => logNative("window-did-start-loading"));
  mainWindow.webContents.on('dom-ready', () => logNative("window-dom-ready"));
  mainWindow.webContents.on('did-finish-load', () => logNative("window-did-finish-load"));
  mainWindow.webContents.on('did-fail-load', (e, code, desc) => logNative("window-did-fail-load", { code, desc }));
  mainWindow.webContents.on('render-process-gone', (e, details) => logNative("window-render-process-gone", { reason: details.reason, exitCode: details.exitCode }));
  mainWindow.webContents.on('unresponsive', () => logNative("window-unresponsive"));
  mainWindow.webContents.on('crashed', () => logNative("window-crashed"));
  mainWindow.webContents.on('console-message', (event, level, message, line, sourceId) => {
    logNative("renderer-console", { level, message, line, sourceId });
  });

  if (isDev) {
    logNative("window-loadURL", { devUrl });
    await mainWindow.loadURL(devUrl);
  } else {
    logNative("window-loadFile", { path: "dist/index.html" });
    await mainWindow.loadFile(path.join(__dirname, "..", "dist", "index.html"), { hash: "dashboard" });
  }

  // TEMPORARILY DISABLED
  // mainWindow.webContents.on('did-finish-load', async () => {
  //   setTimeout(async () => {
  //     try {
  //       const image = await mainWindow.webContents.capturePage();
  //       const fs = require('fs');
  //       fs.writeFileSync('/Users/lalithpraveen/Desktop/Jarvis/frontend/screenshot.png', image.toPNG());
  //       console.log("[FORENSIC] Screenshot saved to frontend/screenshot.png, size:", image.toPNG().length);
  //     } catch (e) {
  //       console.log("[FORENSIC] Screenshot failed:", e.message);
  //     }
  //   }, 3000);
  // });
}

function wireIpc() {
  ipcMain.handle("jarvis:show-dashboard", () => {
    showDashboard();
    return true;
  });
  ipcMain.handle("jarvis:hide-dashboard", () => {
    hideDashboard();
    return true;
  });
  ipcMain.handle("jarvis:consume-pending-wake", () => {
    const reason = pendingWakeReason;
    pendingWakeReason = null;
    logNative("pending-wake-consumed", { reason });
    return reason;
  });
  ipcMain.on("jarvis:wake-state", (_event, awake) => {
    logNative("wake-state", { awake: Boolean(awake) });
    if (tray) tray.setToolTip(awake ? `${appDisplayName} — awake` : `${appDisplayName} — sleeping`);
  });
  ipcMain.on("jarvis:runtime-log", (_event, payload) => {
    logNative("renderer", payload);
  });

  // Push wake diagnostics state when it changes
  wakeDiagnostics.onStateChange = (snapshot) => {
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send("jarvis:native-command", {
        type: "wake-diagnostics",
        data: snapshot
      });
    }
  };
  
  ipcMain.handle("jarvis:get-wake-diagnostics", () => {
    return wakeDiagnostics.getSnapshot();
  });
}

function configurePermissions() {
  session.defaultSession.setPermissionRequestHandler((webContents, permission, callback) => {
    const url = webContents.getURL();
    const localOrigin = url.startsWith(FrontendConfig.VITE_DEV_SERVER) || url.startsWith("file://");
    if (localOrigin && permission === "media") {
      callback(true);
      return;
    }
    callback(false);
  });
}


app.on("child-process-gone", (event, details) => {
  console.log("[APP] child-process-gone:", details);
});

app.commandLine.appendSwitch("autoplay-policy", "no-user-gesture-required");
app.setName(appDisplayName);
app.setAboutPanelOptions({ applicationName: appDisplayName });
logNative("main-start", { isDev, launchedByAgent, startHidden });

const instanceData = process.env.JARVIS_WAKE_OPEN ? { wake: process.env.JARVIS_WAKE_OPEN } : undefined;
const gotLock = app.requestSingleInstanceLock(instanceData);
if (!gotLock) {
  app.quit();
} else {
  app.on("second-instance", (_event, _argv, workingDirectory, additionalData) => {
    if (additionalData?.wake) {
      wakeDashboard(String(additionalData.wake));
      return;
    }
    logNative("second-instance", { workingDirectory });
    showDashboard();
  });
function ensureLaunchAgentUpdated() {
  if (!app.isPackaged || process.platform !== "darwin") return;
  const launchAgentPlistPath = path.join(os.homedir(), "Library", "LaunchAgents", "ai.jarvis.plist");
  if (!fs.existsSync(launchAgentPlistPath)) return;

  try {
    const content = fs.readFileSync(launchAgentPlistPath, "utf8");
    const currentExe = app.getPath("exe");
    // If the path in the plist is not the exact current executable path
    if (!content.includes(`>${currentExe}<`)) {
      logNative("launch-agent-stale", { oldPlist: true, newExe: currentExe });
      const installScript = path.join(unpackedDirname, "macos", "install-launch-agent.cjs");
      if (fs.existsSync(installScript)) {
        spawnSync(process.execPath, [installScript], {
          env: { ...process.env, JARVIS_APP_EXE_OVERRIDE: currentExe },
          stdio: "ignore"
        });
        logNative("launch-agent-updated", { exe: currentExe });
      }
    }
  } catch (err) {
    logNative("launch-agent-update-error", { error: String(err) });
  }
}

  app.on("activate", showDashboard);
  app.whenReady().then(async () => {
    logNative("app-when-ready");

    ensureLaunchAgentUpdated();
    configurePermissions();
    createTray();
    wireIpc();
    await ensureBackend();
    startWakeHelper();
    await createWindow();
    globalShortcut.register("CommandOrControl+Shift+J", showDashboard);
  });
}

powerMonitor.on("resume", () => {
  if (mainWindow) {
    mainWindow.webContents.send("jarvis:native-command", { type: "system-resume" });
  }
});

app.on("before-quit", (event) => {
  if (!isQuitting) {
    logNative("quit-intercepted", { action: "hide-to-background" });
    event.preventDefault();
    hideDashboard();
    return;
  }
  isQuitting = true;
  if (backendProcess) backendProcess.kill();
  if (wakeProcess) wakeProcess.kill();
});

app.on("window-all-closed", (event) => {
  event.preventDefault();
});

app.on("will-quit", () => {
  globalShortcut.unregisterAll();
});
