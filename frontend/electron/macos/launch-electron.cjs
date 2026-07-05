const { spawn } = require("node:child_process");
const path = require("node:path");

const frontendDir = path.resolve(__dirname, "..", "..");
const electronExecutable = require("electron");

process.chdir(frontendDir);

const child = spawn(electronExecutable, ["."], {
  cwd: frontendDir,
  env: {
    ...process.env,
    JARVIS_LAUNCH_AGENT: "1",
    JARVIS_START_HIDDEN: process.env.JARVIS_START_HIDDEN ?? "1",
  },
  stdio: "inherit",
});

child.on("exit", (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
    return;
  }
  process.exit(code ?? 0);
});

for (const signal of ["SIGINT", "SIGTERM"]) {
  process.on(signal, () => {
    if (!child.killed) child.kill(signal);
  });
}
