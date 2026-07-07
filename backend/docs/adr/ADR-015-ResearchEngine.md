# ADR-015 — Research Engine (Grounded)

**Status:** Accepted
**Sprint:** 13.7 (Research Engine)
**Date:** 2026-07-06

## Context

Objective 8: deep research (web/docs/GitHub/papers/PDFs) with citations,
summaries, and source attribution — grounded, no hallucinated sources.

## Decision

Research is a **grounding capability**, not an LLM caller. `research.gather`
collects sources from the configured `SearchProvider`, dedupes by URL, and
returns STRUCTURED, citation-tagged sources (`S1`, `S2`, …) plus an instruction
to answer only from them and cite `[S#]`. `runtime.generate` (the terminal
node) then summarizes from those sources — so the summary is grounded and every
fact is attributable, and no LLM call happens outside `runtime.generate`.

- `SearchProvider` interface (search + optional deep-fetch), injectable via
  `research_manager` — hermetically testable without network/keys.
- Dedup + stable citation ids; optional per-source content fetch.

## Consequences

**Positive**
- Grounded-by-construction: citations come from real gathered sources fed to the
  LLM as authoritative context (same mechanism as `registry.models`).
- Hermetically tested via a fake provider (dedup, citation ids, fetch). 312
  tests pass (+4), zero regression.

**Requires to run live (tracked)**
- A concrete `SearchProvider` backend: a web-search API key, or a browser-driven
  provider reusing the Sprint-13.6 `browser.extract`. Default `NullSearchProvider`
  returns nothing and reports `degraded` until one is configured.
- GitHub/papers/PDF providers are additional `SearchProvider` implementations on
  the same interface.

## Alternatives considered
- A research capability that itself calls the LLM to summarize — rejected
  (violates "no LLM calls outside runtime.generate" and weakens grounding).
  Gathering sources for the terminal node keeps one generation path and real
  citations.
