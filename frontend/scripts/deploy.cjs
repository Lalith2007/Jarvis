const { spawnSync, spawn } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');

const frontendDir = path.resolve(__dirname, '..');

function run(cmd, args, { allowFailure = false, cwd = frontendDir } = {}) {
  console.log(`> ${cmd} ${args.join(' ')}`);
  const result = spawnSync(cmd, args, { cwd, stdio: 'inherit' });
  if (result.status !== 0 && !allowFailure) {
    console.error(`ERROR: ${cmd} failed with status ${result.status}`);
    process.exit(1);
  }
}

async function verifyBackend(url) {
  return new Promise((resolve) => {
    http.get(url, (res) => {
      if (res.statusCode === 200) {
        resolve(true);
      } else {
        resolve(false);
      }
    }).on('error', () => {
      resolve(false);
    });
  });
}

async function main() {
  console.log("=== JARVIS DEPLOYMENT PIPELINE ===");

  console.log("1. Running Regression Check");
  run('npm', ['run', 'test:regression']);

  console.log("2. Stopping LaunchAgent");
  run('npm', ['run', 'native:uninstall'], { allowFailure: true });

  console.log("3. Stopping existing J.A.R.V.I.S and Backend");
  spawnSync('pkill', ['-f', 'J.A.R.V.I.S']);
  spawnSync('pkill', ['-f', 'jarvis-wake-listener']);
  spawnSync('pkill', ['-f', 'uvicorn main:app']);

  console.log("4. Launching Backend");
  const backendDir = path.resolve(frontendDir, '../backend');
  const backendLogPath = path.join(frontendDir, 'backend_deploy.log');
  // truncate log
  fs.writeFileSync(backendLogPath, '');
  const outFd = fs.openSync(backendLogPath, 'a');

  const backendCmd = 'source .venv/bin/activate && uvicorn main:app --host 127.0.0.1 --port 8000';
  console.log(`  > Command: ${backendCmd}`);
  console.log(`  > CWD: ${backendDir}`);
  
  const backendProcess = spawn('/bin/bash', ['-c', backendCmd], {
    cwd: backendDir,
    detached: true,
    stdio: ['ignore', outFd, outFd]
  });
  backendProcess.unref();
  console.log(`  > Spawned PID: ${backendProcess.pid}`);
  console.log(`  > Logs written to: ${backendLogPath}`);

  console.log("4.5. Removing stale builds");
  const distDir = path.join(frontendDir, 'dist');
  if (fs.existsSync(distDir)) {
    fs.rmSync(distDir, { recursive: true, force: true });
  }

  console.log("5. Building Frontend");
  run('npm', ['run', 'build']);

  console.log("6. Packaging Electron");
  run('npm', ['run', 'native:package']);

  console.log("7. Installing & Starting LaunchAgent");
  run('npm', ['run', 'native:install']);

  console.log("8. Waiting for backend / Verify /api/dashboard");
  let backendReady = false;
  for (let i = 1; i <= 30; i++) {
    console.log(`  > Health check retry ${i}/30...`);
    if (await verifyBackend('http://127.0.0.1:8000/api/dashboard')) {
      backendReady = true;
      break;
    }
    await new Promise(r => setTimeout(r, 1000));
  }
  
  if (!backendReady) {
    console.error("ERROR: Backend did not become reachable at /api/dashboard");
    if (fs.existsSync(backendLogPath)) {
      console.error("--- BACKEND LOGS ---");
      console.error(fs.readFileSync(backendLogPath, 'utf8'));
      console.error("--------------------");
    }
    process.exit(1);
  }
  console.log("  > Backend is reachable and healthy.");

  console.log("9. Verify WebSockets");
  const WebSocket = require('ws');
  
  await new Promise((resolve, reject) => {
    const ws = new WebSocket('ws://127.0.0.1:8000/ws/platform');
    const timeout = setTimeout(() => {
      ws.terminate();
      reject(new Error("WebSocket connection timed out"));
    }, 5000);

    ws.on('open', () => {
      clearTimeout(timeout);
      console.log("WebSockets (Platform) active.");
      ws.close();
      resolve();
    });

    ws.on('error', (err) => {
      clearTimeout(timeout);
      reject(err);
    });
  }).catch((err) => {
    console.error(`ERROR: /ws/platform cannot establish a WebSocket connection.`, err.message);
    process.exit(1);
  });

  console.log("10. Verify resident process and wake listener");
  const pgrepJarvis = spawnSync('pgrep', ['-f', 'J.A.R.V.I.S']);
  if (pgrepJarvis.status !== 0) {
    console.error("ERROR: Resident process is not running.");
    process.exit(1);
  }

  // Sleep a bit to allow wake-listener to spawn
  await new Promise(r => setTimeout(r, 2000));
  const pgrepWake = spawnSync('pgrep', ['-f', 'jarvis-wake-listener']);
  if (pgrepWake.status !== 0) {
    console.warn("WARNING: Wake listener is not active. It may be disabled in this environment.");
  }

  console.log("11. Launching J.A.R.V.I.S");
  // The app was already started by LaunchAgent. But we can explicitly 'open' it to show the dashboard.
  const appPath = path.join(distDir, 'mac-arm64', 'J.A.R.V.I.S.app');
  if (fs.existsSync(appPath)) {
    run('open', [appPath]);
  } else {
    run('open', [path.join(distDir, 'mac', 'J.A.R.V.I.S.app')], { allowFailure: true });
  }

  console.log("=== DEPLOYMENT SUCCESSFUL ===");
}

main().catch(err => {
  console.error("Deployment failed:", err);
  process.exit(1);
});
