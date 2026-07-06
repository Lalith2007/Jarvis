# ADR-013 — Computer Control

**Status:** Accepted
**Sprint:** 13.5 (Computer Control)
**Date:** 2026-07-06

## Context

Objective 3: native OS control (filesystem, terminal, clipboard, keyboard,
mouse, window management, app launch, notifications, processes) — as
permission-gated capabilities, no bypass.

## Decision

Expose OS operations as `BaseCapability` instances running through the standard
pipeline:

- `computer.filesystem` — read/write/list/search, delegating to the Sprint-12.9
  resolve-then-validate permission gate (reuses the tool registry; no new fs path).
- `computer.terminal` — runs a command with **no shell** (`shell=False`, arg
  list via `shlex.split`) under a timeout; captures rc/stdout/stderr.
- `computer.process` — read-only process listing (psutil).
- `computer.clipboard` — get/set via `pbcopy`/`pbpaste` (macOS).

All are permission-scoped in their manifests and inherit events/metrics/health
from the lifecycle (ADR-009).

## Consequences

**Positive**
- Filesystem control is sandbox-safe (traversal denied — tested); terminal is
  injection-safe (no shell) and bounded (timeout — tested); processes read-only.
- 304 tests pass (+7), zero regression.

**Remaining / requires host capabilities (tracked)**
- **GUI automation** — keyboard, mouse, window management, app launch,
  notifications — needs `pyautogui`/AppleScript **and** macOS Accessibility +
  Automation permissions granted to the host process. Deferred until the
  Electron host requests those OS permissions; the capability pattern is
  identical (wrap the OS call, gate by permission). Not implementable/testable
  headless in this environment.
- Terminal is intentionally powerful; production should add a per-mission
  command allowlist policy (PolicyEngine) before enabling autonomous use.

## Alternatives considered
- A single monolithic `computer.control` capability — rejected; discrete
  capabilities give precise permissions, metrics, and Athena tool selection.
