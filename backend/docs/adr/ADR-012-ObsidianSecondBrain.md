# ADR-012 — Obsidian Second Brain

**Status:** Accepted
**Sprint:** 13.4 (Obsidian Second Brain)
**Date:** 2026-07-06

## Context

Objective 6: JARVIS should automatically maintain a linked Obsidian vault
(People, Projects, Meetings, Research, Daily, Architecture, Conversations,
Ideas, Tasks, Knowledge) with frontmatter, tags, and `[[wikilink]]` backlinks —
through the pipeline, not a bespoke writer.

## Decision

Add `obsidian.note`, a `BaseCapability` that renders structured input into a
vault note and writes it via the existing `StorageService` (the single vault
I/O owner — no new filesystem path).

- **Note types → folders**: each type maps to `jarvis/<type>/`. JARVIS-authored
  notes are namespaced under `jarvis/` so the user's curated vault structure is
  never overwritten (matches the pre-existing `jarvis/conversations/` convention).
- **Markdown**: YAML frontmatter (`date`, `type`, `tags`, `created_by: jarvis`),
  an `# H1` title, the body, and a `## Related` section of `[[wikilinks]]` from
  the `links` input — producing real graph edges in Obsidian.
- **Naming**: daily notes by date (`YYYY-MM-DD.md`), others by slugified title.
- **Pipeline**: executes through `CapabilityManager → lifecycle → runtime`, so
  it inherits events, metrics, health, and the `write:vault` permission.

## Consequences

**Positive**
- Any mission/capability (or a future conversation-capture hook) can persist
  linked notes by targeting `obsidian.note` — no direct vault writes elsewhere.
- Backlinks/tags create a real knowledge graph; hermetic tests write to a temp
  vault. 297 tests pass (+3), zero regression.

**Remaining (tracked)**
- **Automatic** conversation→note capture (a Stop/post-mission hook that calls
  `obsidian.note` for meaningful exchanges) is a thin follow-up on top of this
  capability.
- Merge/update-in-place (append to an existing person/project note) currently
  overwrites; incremental update is a later enhancement.

## Alternatives considered
- A dedicated Obsidian writer service — rejected (duplicate vault I/O path).
  Reusing `StorageService` keeps one owner and one permission surface.
