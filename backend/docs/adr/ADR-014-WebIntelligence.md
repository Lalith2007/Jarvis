# ADR-014 — Web Intelligence (Browser)

**Status:** Accepted
**Sprint:** 13.6 (Web Intelligence)
**Date:** 2026-07-06

## Context

Objective 2: production browser automation (navigate, multi-tab, cookies,
DOM reasoning, screenshots, PDF, scraping, forms, sessions) as capabilities.

## Decision

Introduce a `BrowserDriver` interface with a lazy `PlaywrightDriver`
implementation, fronted by a driver-injectable `BrowserManager`. Browser
capabilities call the manager, never Playwright directly:

- `browser.navigate` — open a URL in a per-session context
- `browser.extract` — text / DOM scraping (optionally by selector)
- `browser.interact` — click / fill (forms)
- `browser.capture` — screenshot / PDF

Each Playwright **session** is an isolated browser **context**, giving
per-session cookie persistence and multi-tab isolation. Capabilities run through
the standard pipeline (events/metrics/health/permissions). The driver is
lazy-imported so the backend boots without browser binaries; `health_check`
reports `degraded` when Playwright is unavailable.

## Consequences

**Positive**
- Full browser capability surface, hermetically tested via an injected
  `FakeBrowserDriver` (navigate/extract/interact/capture verified). 308 tests
  pass (+4), zero regression.
- Driver abstraction keeps Playwright out of the capability logic and enables
  a future remote/CDP driver without touching capabilities.

**Requires to run live (tracked)**
- `playwright` is importable, but browser binaries need `playwright install`
  (chromium). Until then live navigation returns a clear driver error; the
  architecture + tests are complete.
- Downloads/uploads and advanced DOM reasoning are follow-on methods on the
  same driver interface.

## Alternatives considered
- Calling Playwright directly inside capabilities — rejected (untestable
  without binaries; couples capability logic to one engine). The driver
  interface is the seam for both testing and future engines.
