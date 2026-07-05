const { spawn, spawnSync } = require("node:child_process");
const fs = require("node:fs");
const path = require("node:path");

const sourcePath = path.join(__dirname, "JarvisWakeListener.swift");
const infoPlistPath = path.join(__dirname, "JarvisWakeListener-Info.plist");
const buildDir = path.join(__dirname, "bin");
const binaryPath = path.join(buildDir, "jarvis-wake-listener");
const frontendDir = path.resolve(__dirname, "..", "..");
const electronBin = path.join(frontendDir, "node_modules", ".bin", "electron");

let openedAt = 0;

function showRunningJarvis() {
  const now = Date.now();
  if (now - openedAt < 2500) return;
  openedAt = now;

  console.log("Wake detected. Asking the running JARVIS app to open...");
  const opener = spawn(electronBin, ["."], {
    cwd: frontendDir,
    env: { ...process.env, JARVIS_START_HIDDEN: "0", JARVIS_WAKE_OPEN: "native-wake-test" },
    stdio: "ignore",
    detached: true,
  });
  opener.unref();
}

fs.mkdirSync(buildDir, { recursive: true });

const args = ["swiftc", sourcePath, "-o", binaryPath];
if (fs.existsSync(infoPlistPath)) {
  args.push("-Xlinker", "-sectcreate", "-Xlinker", "__TEXT", "-Xlinker", "__info_plist", "-Xlinker", infoPlistPath);
}

const build = spawnSync("xcrun", args, { encoding: "utf8", stdio: "inherit" });
if (build.status !== 0) process.exit(build.status ?? 1);

console.log("JARVIS wake listener is running. Say: Hey Jarvis");
console.log("Press Ctrl+C to stop.");

const child = spawn(binaryPath, [], { stdio: ["ignore", "pipe", "inherit"] });

child.stdout.on("data", (chunk) => {
  const lines = chunk.toString("utf8").split(/\r?\n/).filter(Boolean);
  for (const line of lines) {
    console.log(line);
    try {
      const payload = JSON.parse(line);
      if (payload.event === "wake") showRunningJarvis();
    } catch {
      // Keep test output resilient if the native helper ever writes a non-JSON line.
    }
  }
});

child.on("exit", (code, signal) => {
  if (signal) process.kill(process.pid, signal);
  process.exit(code ?? 0);
});
