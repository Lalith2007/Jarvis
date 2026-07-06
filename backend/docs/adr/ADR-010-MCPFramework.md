# ADR-010 — MCP Framework & Tool→Capability Adapter

**Status:** Accepted
**Sprint:** 13.2 (MCP Framework)
**Date:** 2026-07-06

## Context

Objective 1 requires a full MCP ecosystem where **every MCP tool becomes a
BaseCapability usable by Athena exactly like built-ins**, with discovery,
dynamic registration, auth, permissions, health, and hot load/unload — without
introducing a second execution path.

## Decision

MCP tools are adapted into the existing Capability System rather than executed
through a parallel MCP runtime:

- **Transport** (`app/mcp/transport.py`): `MCPTransport` base (inert stub) +
  `StdioMCPTransport` (spawns an MCP server subprocess, line-delimited JSON-RPC
  over stdin/stdout, thread-safe). Transport is injectable (enables hermetic
  fake-server tests and future HTTP transport).
- **Client** (`app/mcp/client.py`): `initialize`, `tools/list` → `list_tools()`,
  `tools/call` → `call_tool()`, `ping` → `health()`. Tolerant parsing (returns
  `[]` on malformed/legacy responses, preserving backward compatibility).
- **Adapter** (`app/mcp/capability.py`): `MCPToolCapability(BaseCapability)`
  wraps one `(client, tool)`; id = `mcp.<server>.<tool>`; `execute()` calls the
  MCP tool and returns a structured `CapabilityResult`. Because it is a
  `BaseCapability`, it runs through the **same** `CapabilityManager → lifecycle`
  path and automatically gets events, metrics, health, and permission checks
  (ADR-009).
- **Manager** (`app/mcp/manager.py`): `connect(config, transport)` discovers
  tools and registers each as a capability in the `CapabilityRegistry`;
  `remove_server()` unregisters them (**hot unload**). Legacy
  `register_server(name, endpoint, capabilities)` preserved.
- **Config** (`MCPServerConfig`): stdio/http, command/args or endpoint,
  `auth_token`/`headers`, `permissions`.

## Consequences

**Positive**
- MCP tools are first-class capabilities: discoverable, metered, health-checked,
  event-emitting, permission-gated — no separate MCP execution path.
- Hot load/unload works by (un)registering capabilities at runtime.
- Hermetic tests via injected fake transport; 290 tests pass, zero regression.

**Remaining (tracked)**
- Only `stdio` transport is implemented; HTTP/remote transport is a follow-up
  (the config + adapter already accommodate it).
- Auth headers are modeled in `MCPServerConfig` but only wired for HTTP (stdio
  uses process env); complete in the HTTP transport work.
- **Athena dynamic planning over MCP capabilities**: MCP tools are registered
  and executable through the pipeline today, but Athena's `CapabilityEngine`
  still selects from fixed intent groups. Auto-selecting arbitrary registered
  (incl. MCP) capabilities is delivered in Sprint 13.11 (Autonomous Planning).

## Alternatives considered
- A dedicated MCP execution runtime — rejected (duplicate system, bypasses the
  Capability System). Adapting to `BaseCapability` reuses all existing
  guarantees.
