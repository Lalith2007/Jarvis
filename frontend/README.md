# J.A.R.V.I.S Frontend

React, Three.js, and Electron frontend for the J.A.R.V.I.S dashboard.

## Desktop runtime

```bash
npm run desktop
```

Production-style local desktop launch:

```bash
npm run desktop:prod
```

## macOS native helper

Install JARVIS as a login-time LaunchAgent. By default it starts hidden in the tray/menu bar and brings the dashboard forward when the runtime wakes.

```bash
npm run native:install
```

Useful options:

- `npm run native:install -- --show-on-login` opens the dashboard immediately at login.
- `npm run native:install -- --stay-awake` also installs a `caffeinate -dimsu` helper so macOS does not idle-sleep while JARVIS is listening.
- `npm run native:install -- --no-start` writes the LaunchAgent files without starting them immediately.

Status and removal:

```bash
npm run native:status
npm run native:uninstall
```

Wake listener permission test:

```bash
npm run native:wake-test
```

Say `Hey Jarvis`. If macOS asks for Microphone or Speech Recognition permission, allow it, then restart the LaunchAgent with `npm run native:install`.

Important macOS reality: a background helper can auto-start JARVIS after login, relaunch after crashes, and keep the machine awake if you enable `--stay-awake`. A fully sleeping Mac with audio hardware suspended still cannot hear claps until macOS wakes the machine again.

Logs are written to `~/Library/Logs/JARVIS/`.
