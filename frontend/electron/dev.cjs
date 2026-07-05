const { spawn } = require("node:child_process");

function waitFor(url, timeoutMs = 30_000) {
  const startedAt = Date.now();
  return new Promise((resolve, reject) => {
    const tick = async () => {
      try {
        const response = await fetch(url);
        if (response.ok) {
          resolve();
          return;
        }
      } catch {
        // Keep polling until Vite is ready.
      }
      if (Date.now() - startedAt > timeoutMs) {
        reject(new Error(`Timed out waiting for ${url}`));
        return;
      }
      setTimeout(tick, 400);
    };
    tick();
  });
}

const vite = spawn("npm", ["run", "dev", "--", "--host", "127.0.0.1"], {
  stdio: "inherit",
  shell: true,
});

const { FrontendConfig } = require("./config.cjs");

waitFor(FrontendConfig.VITE_DEV_SERVER)
  .then(() => {
    const electron = spawn("npx", ["electron", "."], {
      stdio: "inherit",
      shell: true,
      env: {
        ...process.env,
        JARVIS_ELECTRON_DEV: "1",
        JARVIS_FRONTEND_URL: FrontendConfig.FRONTEND_DEV_DASHBOARD,
      },
    });
    electron.on("exit", (code) => {
      vite.kill();
      process.exit(code ?? 0);
    });
  })
  .catch((error) => {
    console.error(error);
    vite.kill();
    process.exit(1);
  });

process.on("SIGINT", () => {
  vite.kill();
  process.exit(0);
});

