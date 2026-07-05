const { spawnSync } = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const APP_LABEL = "ai.jarvis";
const AWAKE_LABEL = "ai.jarvis.awake";
const LEGACY_LABELS = ["ai.jarvis.alpha", "ai.jarvis.alpha.awake"];
const frontendDir = path.resolve(__dirname, "..", "..");
const launcherPath = path.join(__dirname, "launch-electron.cjs");
const nodePath = process.execPath;
const launchAgentsDir = path.join(os.homedir(), "Library", "LaunchAgents");
const logDir = path.join(os.homedir(), "Library", "Logs", "JARVIS");
const appPlistPath = path.join(launchAgentsDir, `${APP_LABEL}.plist`);
const awakePlistPath = path.join(launchAgentsDir, `${AWAKE_LABEL}.plist`);
const target = `gui/${process.getuid()}`;

const args = new Set(process.argv.slice(2));
const stayAwake = args.has("--stay-awake");
const noStart = args.has("--no-start");
const showOnLogin = args.has("--show-on-login");
const forceDevLauncher = args.has("--dev");

function findPackagedAppExecutable() {
  if (process.env.JARVIS_APP_EXE_OVERRIDE && fs.existsSync(process.env.JARVIS_APP_EXE_OVERRIDE)) {
    return process.env.JARVIS_APP_EXE_OVERRIDE;
  }
  const candidates = [
    path.join(frontendDir, "dist", "mac-arm64", "J.A.R.V.I.S.app", "Contents", "MacOS", "J.A.R.V.I.S"),
    path.join(frontendDir, "dist", "mac", "J.A.R.V.I.S.app", "Contents", "MacOS", "J.A.R.V.I.S"),
    path.join(frontendDir, "dist", "mac-universal", "J.A.R.V.I.S.app", "Contents", "MacOS", "J.A.R.V.I.S"),
  ];
  return candidates.find((candidate) => fs.existsSync(candidate)) ?? null;
}

function xml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&apos;");
}

function run(command, commandArgs, { allowFailure = false } = {}) {
  const result = spawnSync(command, commandArgs, { encoding: "utf8" });
  if (result.status !== 0 && !allowFailure) {
    const output = [result.stdout, result.stderr].filter(Boolean).join("\n").trim();
    throw new Error(`${command} ${commandArgs.join(" ")} failed${output ? `:\n${output}` : ""}`);
  }
  return result;
}

function appPlist() {
  const hidden = showOnLogin ? "0" : "1";
  const packagedExecutable = forceDevLauncher ? null : findPackagedAppExecutable();
  const programArguments = packagedExecutable
    ? [`<string>${xml(packagedExecutable)}</string>`]
    : [`<string>${xml(nodePath)}</string>`, `<string>${xml(launcherPath)}</string>`];

  return `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${APP_LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    ${programArguments.join("\n    ")}
  </array>
  <key>WorkingDirectory</key>
  <string>${xml(frontendDir)}</string>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <dict>
    <key>Crashed</key>
    <true/>
  </dict>
  <key>StandardOutPath</key>
  <string>${xml(path.join(logDir, "launch-agent.out.log"))}</string>
  <key>StandardErrorPath</key>
  <string>${xml(path.join(logDir, "launch-agent.err.log"))}</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>JARVIS_NATIVE_HELPER</key>
    <string>1</string>
    <key>JARVIS_LAUNCH_AGENT</key>
    <string>1</string>
    <key>JARVIS_START_HIDDEN</key>
    <string>${hidden}</string>
  </dict>
</dict>
</plist>
`;
}

function awakePlist() {
  return `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${AWAKE_LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/caffeinate</string>
    <string>-dimsu</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>${xml(path.join(logDir, "stay-awake.out.log"))}</string>
  <key>StandardErrorPath</key>
  <string>${xml(path.join(logDir, "stay-awake.err.log"))}</string>
</dict>
</plist>
`;
}

function load(label, plistPath) {
  run("launchctl", ["bootout", target, plistPath], { allowFailure: true });
  run("launchctl", ["bootstrap", target, plistPath]);
  run("launchctl", ["kickstart", "-k", `${target}/${label}`], { allowFailure: true });
}

if (process.platform !== "darwin") {
  throw new Error("JARVIS LaunchAgent installation is only available on macOS.");
}

if (!fs.existsSync(path.join(frontendDir, "node_modules", "electron"))) {
  throw new Error(`Electron was not found in ${frontendDir}/node_modules. Run npm install in ${frontendDir} first.`);
}

if (!fs.existsSync(launcherPath)) {
  throw new Error(`Native launcher was not found at ${launcherPath}.`);
}

fs.mkdirSync(launchAgentsDir, { recursive: true });
fs.mkdirSync(logDir, { recursive: true });
for (const legacyLabel of LEGACY_LABELS) {
  const legacyPlistPath = path.join(launchAgentsDir, `${legacyLabel}.plist`);
  run("launchctl", ["bootout", target, legacyPlistPath], { allowFailure: true });
  fs.rmSync(legacyPlistPath, { force: true });
}
fs.writeFileSync(appPlistPath, appPlist(), { mode: 0o644 });

if (stayAwake) {
  fs.writeFileSync(awakePlistPath, awakePlist(), { mode: 0o644 });
} else if (fs.existsSync(awakePlistPath)) {
  run("launchctl", ["bootout", target, awakePlistPath], { allowFailure: true });
  fs.rmSync(awakePlistPath, { force: true });
}

if (!noStart) {
  load(APP_LABEL, appPlistPath);
  if (stayAwake) load(AWAKE_LABEL, awakePlistPath);
}

console.log(`Installed ${APP_LABEL}`);
console.log(`App LaunchAgent: ${appPlistPath}`);
console.log(`Logs: ${logDir}`);
console.log(`Launcher: ${findPackagedAppExecutable() && !forceDevLauncher ? "packaged J.A.R.V.I.S.app" : "development Electron launcher"}`);
console.log(`Start mode: ${showOnLogin ? "show dashboard at login" : "hidden background helper at login"}`);
console.log(`Stay-awake helper: ${stayAwake ? "enabled via caffeinate -dimsu" : "disabled"}`);
if (noStart) console.log("LaunchAgent was written but not started because --no-start was used.");
