# ADR-018 — Vault Grounding (read the user's Obsidian notes)

**Status:** Accepted
**Sprint:** 13.11 (found via live pipeline forensics, not unit tests)
**Date:** 2026-07-06

## Context

Live tracing of a real query — "Review my Obsidian vault North Star" — showed
Athena routed it to `runtime.generate` only, with **no** capability to read the
user's vault. Grounding discipline held (it refused: "I don't have access")
rather than hallucinating, but JARVIS genuinely could not read `brain/North
Star.md`. Green hermetic tests never caught this because they mock the LLM and
never exercise "read my vault" intents. The user was right to be skeptical of
green-suite-only confidence.

## Decision

Add `vault.search`, a grounding capability that reads the user's actual Obsidian
notes via the existing `VaultService` (index + `QueryProcessor` + search), and
an Athena `vault_information` intent group routing vault/notes/North-Star/goals
queries to it before `runtime.generate`. `vault.search` is added to
`GROUNDING_CAPABILITY_IDS`, so its output is injected as authoritative context
and enforcement fires. Vault reads happen only through this capability;
ContextBuilder stays formatter-only.

## Consequences

**Positive**
- "Review my North Star" now executes `vault.search → runtime.generate`, the
  prompt contains the real note content, and the summary is grounded in the
  user's actual goals (verified live).
- Closes the gap between "unit tests green" and "the live pipeline actually
  reads the vault." 323 tests pass (+3 routing tests), zero regression.

**Method note**
- This gap was found by **live forensic tracing of a real query**, reinforcing
  that hermetic tests verify wiring, not end-to-end grounding. Live tracing is
  now part of the acceptance bar for grounding-dependent features.

## Alternatives considered
- Letting the LLM answer from prior knowledge — rejected (that is the exact
  hallucination Sprint 12 forbids). Reading the real note is the only grounded
  answer.
