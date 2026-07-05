const { spawnSync } = require('node:child_process');
const path = require('node:path');

const projectRoot = path.resolve(__dirname, '..', '..');

const patterns = [
  '/system/snapshot',
  'http://localhost',
  'http://127.0.0.1',
  'ws://localhost',
  'ws://127.0.0.1'
];

const excludeFiles = [
  'frontend/electron/config.cjs',
  'frontend/electron/config.d.cts',
  'frontend/scripts/regression-check.cjs',
  'frontend/electron/dev.cjs',
  'frontend/package.json',
  'frontend/package-lock.json',
  'backend/tests/',
  'backend/upgrade_'
];

let failed = false;

for (const pattern of patterns) {
  // Use ripgrep or git grep. We'll use git grep since it's a git repo.
  const result = spawnSync('git', ['grep', '-n', pattern], { cwd: projectRoot, encoding: 'utf8' });
  if (result.stdout) {
    const lines = result.stdout.trim().split('\n');
    for (const line of lines) {
      // line format: filepath:line:content
      const filePath = line.split(':')[0];
      if (!excludeFiles.some(ex => filePath.includes(ex))) {
        console.error(`ERROR: Deprecated endpoint or hardcoded URL found: ${pattern}`);
        console.error(`-> ${line}`);
        failed = true;
      }
    }
  }
}

if (failed) {
  console.error("Regression check failed. Please remove deprecated endpoints and hardcoded URLs.");
  process.exit(1);
}

console.log("Regression check passed.");
