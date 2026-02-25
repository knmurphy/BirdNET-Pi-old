# BirdNET-Pi UI Improvement Proposal

## Context

The original issue requested "brainstorming a better UI system — faster, snappier,
better mobile, configurable dashboard." A first pass in this branch added a
`dashboard.php` stats-widget page and made it the default view. That is a useful
incremental step, but it leaves the deepest performance and UX problems untouched.

This document captures what is happening in the wider BirdNET-Pi ecosystem, identifies
the root causes of the current UI's problems, and recommends a concrete path forward
informed by those findings.

---

## What the Upstream Ecosystem Has Done (and Not Done)

### Nachtzuster/BirdNET-Pi — the active PHP fork

[Nachtzuster/BirdNET-Pi](https://github.com/Nachtzuster/BirdNET-Pi) is the most
actively maintained fork of the original mcguirepr89 project: 767 stars, 105 forks,
570+ commits ahead of the original as of early 2026.

**UI work status:** largely maintenance, not modernisation.

- **Issue #416 — "Any interest in a visual redesign of the UI?"** (opened Aug 2025):
  The repo owner responded directly:
  > "A _purely visual_ overhaul is probably not going to happen. I would like an
  > overhaul that does away with the PHP code and moves to some Python web framework
  > (flask, FastHTML, …)."

- **PR #562 — "Modernize v1"** (submitted Jan 31, 2026): A community contributor
  (`cpieper`) proposed a UI modernisation with 421 additions / 309 deletions across
  5 files. It was **closed without being merged the same day** — no comments, no
  review. The contributor has since carried the work forward in their own fork
  ([cpieper/BirdNET-Pibird](https://github.com/cpieper/BirdNET-Pibird)).

- **Open UX bugs:** Issue #556 ("can't scroll to end on 1920×1080 displays") has
  been open since January 2026 with no fix merged — a symptom of the iframe
  architecture used in the current UI.

- **Active feature discussions:** Monthly reports, fixed column headers on scroll,
  new-species-today badge, wikidata species infoboxes — all open, none UI-critical.

**Bottom line:** Nachtzuster maintains the PHP engine well but has explicitly
deprioritised visual/UX overhaul work on the PHP codebase.

---

### BirdNET-Go — the reference for what a modern BirdNET UI looks like

[tphakala/birdnet-go](https://github.com/tphakala/birdnet-go) is a complete
reimplementation in Go + Svelte 5. It is **not** a fork — there is no shared code
and no migration path — but it is the most instructive reference for what the UI
experience _could_ be:

- Migrated from HTMX → Svelte 5 (Dec 2025 nightly); the Svelte UI is now the only
  interface.
- Collapsible sidebar with icon-only compact mode; adapts seamlessly to mobile.
- Animated daily-summary dashboard; automatic real-time updates (no manual reload).
- Per-species notification thresholds, first-occurrence tracking.
- Mobile-native audio playback with speed control and on-demand spectrogram.
- Multi-language: English, German, French, Finnish, Spanish, Portuguese.

**What this tells us:** The Svelte 5 route (or its near-equivalent) is the best
long-term UI answer for this class of app. It is also the hardest migration for a
PHP-codebase project and requires a build toolchain that can't run on the Pi itself.

---

### BirdNET-BarChart — another complete reimplementation

[dacracot/BirdNET-BarChart](https://github.com/dacracot/BirdNET-BarChart) is yet
another full rewrite with no shared code. It focuses on charting/visualisation.

---

### Summary of the landscape

| Project | Tech stack | UI status | Migration path |
|---------|-----------|-----------|---------------|
| mcguirepr89/BirdNET-Pi | PHP + jQuery | Original; largely frozen | This repo |
| **Nachtzuster/BirdNET-Pi** | PHP + vanilla JS | Maintenance mode; no redesign planned | Direct fork |
| cpieper/BirdNET-Pibird | PHP (modernised) | Active modernisation; closed PR | Cherry-pick |
| **tphakala/birdnet-go** | Go + Svelte 5 | Full modern UI; best-in-class | None (rewrite) |
| dacracot/BirdNET-BarChart | Unknown | Charting focus | None (rewrite) |

---

## Implications for This Repository

Given what the upstream ecosystem has and hasn't done, the realistic options for
this repository (`knmurphy/BirdNET-Pi-old`) are:

1. **Stay in PHP, improve incrementally** — align with Nachtzuster for engine fixes,
   take UI improvements from cpieper's modernise branch (cherry-pick), and fix the
   iframe architecture with HTMX. This is the lowest-effort path with a meaningful
   UX payoff.

2. **Target a Python backend** — in line with Nachtzuster's stated aspiration
   (Flask or FastHTML), replace the PHP server with Python while keeping the SQLite
   database. This would be a significant rewrite but keeps the same Pi deployment
   model.

3. **Treat this as a staging fork and migrate toward BirdNET-Go** — contribute
   upstream to BirdNET-Go rather than maintaining a parallel PHP stack. The data
   model (SQLite, `birds.db`) would need a migration script.

---

---

## Root-Cause Analysis

### 1. iframe-based navigation is the single biggest bottleneck

Every tab click in the current UI loads a brand-new PHP page **inside an `<iframe>`**:

```
index.php (outer shell)
  └── <iframe src="/views.php?view=Overview">   ← full PHP page render per click
        └── overview.php (included)
              └── SQLite queries, shell_exec calls, HTML output
```

Consequences:
- Each navigation incurs a full HTTP round-trip plus a full PHP render pass.
- The browser must parse a new HTML document, re-evaluate the same `style.css`
  and JavaScript, and repaint the whole frame.
- Scroll position resets; browser back/forward do not work as users expect.
- On mobile, iframes require `height:93%` hacks that break on some browsers.
- **Known open bug in Nachtzuster's fork**: Issue #556 (can't scroll to end on
  1920×1080 displays, Jan 2026) is a direct symptom of this iframe architecture
  and has not been fixed there either.

### 2. No browser-side caching of repeated assets

`style.css` is versioned with a hardcoded query string (`?v=1.20.23`) that never
changes. The font (`RobotoFlex-Regular.ttf`, ~700 KB) is re-downloaded or not
cached consistently. No `Cache-Control` headers are set on static assets.

### 3. Blocking `shell_exec` calls on every page load

`views.php` ran `git fetch` (a network call!) on every single request to check
for updates, blocking the response until git finishes. On a slow network this
adds multiple seconds to every page load. *(Fixed in this branch: the fetch now
runs in the background at most once per hour.)*

### 4. Mobile navigation UX

The hamburger-dropdown approach works but feels dated. On phones, users expect
either a bottom navigation bar (iOS/Android pattern) or a slide-in drawer, not a
dropdown that appears in the middle of the page and requires a second tap.

### 5. No at-a-glance summary

The Overview page requires loading the iframe, which fetches the latest detection,
renders a chart, and fires several XHR requests before anything meaningful appears.
A lighter, always-visible dashboard panel would address this. *(The `dashboard.php`
added in this branch is a starting point.)*

---

## Options Evaluated

### Option A — HTMX migration of the PHP codebase (recommended near-term)

[HTMX](https://htmx.org) is a ~14 KB JavaScript library that replaces iframes and
full-page navigations with declarative AJAX partial-page swaps. No build step. No
Node.js. Works directly with the existing PHP templates.

This is also what BirdNET-Go started with before moving to Svelte 5 — validating it
as a sensible intermediate step.

**How it changes the architecture:**

```
index.php (outer shell, permanent — loads once)
  └── <main id="content">  ← HTMX swaps only this div on each nav click
        only the relevant PHP fragment is fetched and inserted
```

Each PHP view file returns an HTML **fragment** (no `<html>/<body>` wrapper).
This is already almost true — most of the view files are fragments today.

**Pros:**
- Biggest single performance win: eliminates the iframe overhead entirely.
- Backend PHP stays almost identical — minor change per view file.
- ~14 KB dependency, no build toolchain, works on PHP 7/8.
- Browser back/forward work correctly (HTMX `hx-push-url`).
- Progressive — the app still works without JavaScript (normal form submits).
- Fixes the Nachtzuster issue #556 scroll bug as a side-effect.

**Cons:**
- Requires refactoring `index.php` / `views.php` to remove the iframe shell.
- Inline `<script>` blocks in view files need slight adjustment (scripts inside
  HTMX-swapped content must use `htmx:afterSwap` events or be moved to the shell).

**Effort estimate:** Medium — 1–2 days for a careful migration.

---

### Option B — Cherry-pick from cpieper/BirdNET-Pibird

cpieper submitted a "Modernize v1" PR (562) to Nachtzuster in Jan 2026 with 421
additions / 309 deletions and it was closed without review. Their fork
([BirdNET-Pibird](https://github.com/cpieper/BirdNET-Pibird)) contains the rejected
modernisation work and is actively continued. The changes are PHP-only — safe to
cherry-pick.

**Pros:** Real, tested work that is almost mergeable. Zero new dependencies.

**Cons:** Need to diff and understand the changes before applying; may conflict with
this branch's existing work. Doesn't fix the iframe root cause.

**Recommendation:** Worth reviewing and cherry-picking compatible parts alongside
the HTMX migration.

---

### Option C — Python backend (Flask or FastHTML)

Aligns with Nachtzuster's stated future direction. Replace the PHP web tier with
Python while keeping the same SQLite database and Caddy reverse proxy.

**Pros:** More contributors know Python than PHP; better testing story; modern
templating (Jinja2); SQLAlchemy ORM for the database layer.

**Cons:**
- Significant rewrite of all view files.
- PHP is removed as a dependency but Python WSGI service is added.
- Installation/update scripts need rewriting.
- Multi-month effort.

**Recommendation:** Valid long-term goal, but not before the iframe architecture
is fixed. Establishing HTMX navigation first makes the eventual Python migration
easier (the view files are already decoupled fragments).

---

### Option D — BirdNET-Go (Go + Svelte 5) as the reference target

The [BirdNET-Go](https://github.com/tphakala/birdnet-go) UI (now Svelte 5) is the
best-in-class reference: mobile-first, real-time, animated dashboards, per-species
thresholds, multi-language. It is a complete reimplementation — no shared code, no
migration path from the PHP codebase.

**Recommendation:** Use as a design and feature reference; not a migration target
unless the decision is made to abandon the PHP codebase entirely.

---

### Option E — Continue with PHP + vanilla JS (status quo)

Keep the iframe architecture and improve it incrementally:
- Add `loading="lazy"` to the iframe.
- Use `postMessage` to avoid iframe height hacks.
- Add `Cache-Control` headers for assets.

**Pros:** Zero new dependencies, purely additive.

**Cons:** Does not fix the root problem. The iframe overhead remains. The "snappy"
feeling the issue asked for is not achievable within an iframe model.

---

## Recommended Path Forward

### Phase 1 — Fix the structural bottleneck (HTMX migration)

1. Add HTMX (self-hosted, no CDN dependency) to `homepage/static/`.
2. Refactor `index.php` to remove the `<iframe>`. The outer shell loads once;
   the inner `<main id="content">` is swapped by HTMX on navigation.
3. Adapt each view PHP file to return a plain HTML fragment (most already do).
4. ~~Move the `git fetch` update-check to an async background process.~~ *(Done in
   this branch — the fetch now runs non-blocking in the background at most once/hr.)*
5. Add proper `Cache-Control: public, max-age=31536000, immutable` headers for
   the font and static assets (via Caddy config or a PHP header).

**Expected outcome:** Page navigation feels instant. No more scroll-position resets.
Back button works. Nachtzuster issue #556 is fixed as a side-effect.

---

### Phase 2 — Dashboard and mobile UX

The `dashboard.php` added in the previous commit is a good starting point. Refine it:

1. **Replace the hamburger dropdown with a bottom navigation bar on mobile.**
   On screens ≤ 640 px, show 4–5 icon+label tabs pinned to the bottom edge
   (Dashboard / Detections / Recordings / Tools). This matches the native mobile
   app pattern from BirdNET-Go that users already know.

2. **Add a PWA manifest** (`manifest.json`) and minimal Service Worker that
   caches the shell, CSS, font, and icons. This enables "Add to Home Screen" and
   makes the first paint nearly instant on repeat visits.

3. **Refine the dashboard widgets** based on what bird-watchers actually want to
   see at a glance (informed by BirdNET-Go's dashboard design):
   - Today's detection count + sparkline of detections-per-hour
   - Most recent detection (species name + confidence + audio player)
   - Species count today vs. all-time, with first-detection-today badge
   - System health (disk usage, service status) — one small badge, not a full table

---

### Phase 3 — Polish / longer-term

- Dark mode (`prefers-color-scheme: dark`) CSS variables.
- Swipe gestures on mobile to navigate between main views (HTMX makes this
  easy to add with a small pointer-events handler).
- Notification badge on the nav when a new species is detected for the first time today.
- Evaluate Python rewrite (Flask/FastHTML) as Nachtzuster has suggested for the
  engine layer, keeping HTMX navigation in the frontend.

---

## What Has Already Been Done in This Branch

| Change | File | Status |
|--------|------|--------|
| Stats widget dashboard (card grid) | `homepage/dashboard.php` | ✅ done |
| Dashboard CSS (responsive grid, widget cards) | `homepage/style.css` | ✅ done |
| Dashboard as default view; nav item added | `homepage/views.php` | ✅ done |
| Non-blocking git fetch (1-hour file cache) | `homepage/views.php` | ✅ done |
| Root-cause analysis + ecosystem research | `docs/ui-improvement-proposal.md` | ✅ this file |

---

## What This Proposal Does NOT Recommend

- **A purely visual CSS overhaul** — Nachtzuster's maintainer has explicitly said
  this is not a priority in the PHP codebase. Any investment in visual polish should
  happen after the iframe architecture is fixed, so it benefits from the faster navigation.
- **Switching to a CSS framework like Bootstrap or Tailwind** — the current
  hand-written CSS is small and well-suited to the app. Adding a framework would
  increase page weight significantly.
- **Removing the SQLite backend** in favour of a REST API — the current direct-PHP
  database pattern is appropriate for a single-device app.
