const { spawnSync } = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const labels = ["ai.jarvis", "ai.jarvis.awake", "ai.jarvis.alpha", "ai.jarvis.alpha.awake"];
const launchAgentsDir = path.join(os.homedir(), "Library", "LaunchAgents");
const target = `gui/${process.getuid()}`;

function run(command, args) {
  return spawnSync(command, args, { encoding: "utf8" });
}

if (process.platform !== "darwin") {
  throw new Error("JARVIS LaunchAgent removal is only available on macOS.");
}

for (const label of labels) {
  const plistPath = path.join(launchAgentsDir, `${label}.plist`);
  run("launchctl", ["bootout", target, plistPath]);
  fs.rmSync(plistPath, { force: true });
  console.log(`Removed ${label}`);
}

console.log("JARVIS LaunchAgents have been unloaded. Logs were left in ~/Library/Logs/JARVIS.");
