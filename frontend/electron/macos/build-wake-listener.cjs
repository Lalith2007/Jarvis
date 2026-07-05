const { spawnSync } = require("node:child_process");
const fs = require("node:fs");
const path = require("node:path");

const sourcePath = path.join(__dirname, "JarvisWakeListener.swift");
const infoPlistPath = path.join(__dirname, "JarvisWakeListener-Info.plist");
const buildDir = path.join(__dirname, "bin");
const binaryPath = path.join(buildDir, "jarvis-wake-listener");

fs.mkdirSync(buildDir, { recursive: true });

// Step 1: Compile Swift — embed the Info.plist into __TEXT,__info_plist
const args = ["swiftc", sourcePath, "-o", binaryPath];
if (fs.existsSync(infoPlistPath)) {
  args.push(
    "-Xlinker", "-sectcreate",
    "-Xlinker", "__TEXT",
    "-Xlinker", "__info_plist",
    "-Xlinker", infoPlistPath
  );
}
const compileResult = spawnSync("xcrun", args, { encoding: "utf8", stdio: "inherit" });
if (compileResult.status !== 0) process.exit(compileResult.status ?? 1);

// Step 2: Re-sign ad-hoc so macOS TCC sees Info.plist as "bound" (entries=N),
// not "not bound". Without this step, codesign -dv reports "Info.plist=not bound"
// and TCC ignores NSMicrophoneUsageDescription / NSSpeechRecognitionUsageDescription,
// causing an immediate SIGABRT on macOS 15+ (Sequoia / macOS 27).
//
// --sign -   : ad-hoc identity (no Developer cert required)
// --force    : overwrite the linker-generated adhoc signature
// No --options runtime: avoid the Lightweight Code Requirement check on Sequoia
//   that rejects non-entitlement keys like NSSpeechRecognitionUsageDescription.
const signResult = spawnSync("codesign", [
  "--sign", "-",
  "--force",
  binaryPath
], { encoding: "utf8", stdio: "inherit" });

if (signResult.status !== 0) {
  console.error("codesign failed — binary may not have TCC access.");
  process.exit(signResult.status ?? 1);
}

// Verify the result.
const verifyResult = spawnSync("codesign", ["-dv", binaryPath], { encoding: "utf8", stdio: "pipe" });
const verifyOut = verifyResult.stderr + verifyResult.stdout;
if (verifyOut.includes("Info.plist entries=")) {
  console.log("Info.plist bound successfully (TCC-visible).");
} else if (verifyOut.includes("Info.plist=not bound")) {
  console.error("WARNING: Info.plist still not bound — TCC will reject microphone/speech permissions.");
}

console.log(`Built J.A.R.V.I.S wake listener: ${binaryPath}`);
