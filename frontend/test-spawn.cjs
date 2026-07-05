const { spawn } = require("child_process");
const path = require("path");

const binaryPath = path.join(__dirname, "dist/mac-arm64/J.A.R.V.I.S.app/Contents/Resources/app.asar.unpacked/electron/macos/bin/jarvis-wake-listener");
console.log(`[SPAWN] Executable path: ${binaryPath}`);
console.log(`[SPAWN] About to spawn()`);

const p = spawn(binaryPath, [], { stdio: ["ignore", "pipe", "pipe"] });

console.log(`[SPAWN] Spawned successfully. PID: ${p.pid}`);

p.stdout.on("data", d => console.log(`[STDOUT] ${d.toString().trim()}`));
p.stderr.on("data", d => console.log(`[STDERR] ${d.toString().trim()}`));

p.on("error", err => console.log(`[SPAWN ERROR] ${err.message}`));
p.on("exit", (code, signal) => {
    console.log(`[SPAWN EXIT] Code: ${code}, Signal: ${signal}`);
});
