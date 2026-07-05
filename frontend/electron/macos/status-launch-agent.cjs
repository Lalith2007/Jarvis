const { spawnSync } = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const labels = ["ai.jarvis", "ai.jarvis.awake", "ai.jarvis.alpha", "ai.jarvis.alpha.awake"];
const launchAgentsDir = path.join(os.homedir(), "Library", "LaunchAgents");
const target = `gui/${process.getuid()}`;

if (process.platform !== "darwin") {
  throw new Error("JARVIS LaunchAgent status is only available on macOS.");
}

for (const label of labels) {
  const plistPath = path.join(launchAgentsDir, `${label}.plist`);
  const result = spawnSync("launchctl", ["print", `${target}/${label}`], { encoding: "utf8" });
  const loaded = result.status === 0;
  console.log(`${label}`);
  console.log(`  plist: ${fs.existsSync(plistPath) ? plistPath : "not installed"}`);
  console.log(`  launchctl: ${loaded ? "loaded" : "not loaded"}`);
  if (loaded) {
    const interesting = result.stdout
      .split("\n")
      .filter((line) => /state =|pid =|last exit code =|runs =|program =/.test(line))
      .slice(0, 8);
    for (const line of interesting) console.log(`  ${line.trim()}`);
  }
}
