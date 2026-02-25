# BirdNET-Pi UI Improvement Proposal

## Context

The original issue requested "brainstorming a better UI system — faster, snappier,
better mobile, configurable dashboard." A first pass in this branch added a
`dashboard.php` stats-widget page and made it the default view. That is a useful
incremental step, but it leaves the deepest performance and UX problems untouched.

This document identifies the root causes, evaluates realistic options for a
Pi-hosted PHP application, and recommends a phased path forward.

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

### 2. No browser-side caching of repeated assets

`style.css` is versioned with a hardcoded query string (`?v=1.20.23`) that never
changes. The font (`RobotoFlex-Regular.ttf`, ~700 KB) is re-downloaded or not
cached consistently. No `Cache-Control` headers are set on static assets.

### 3. Blocking `shell_exec` calls on every page load

`views.php` runs `git fetch` (a network call!) on every single request to check
for updates, blocking the response until git finishes. On a slow network this
adds multiple seconds to every page load.

### 4. Mobile navigation UX

The hamburger-dropdown approach works but feels dated. On phones, users expect
either a bottom navigation bar (iOS/Android pattern) or a slide-in drawer, not a
dropdown that appears in the middle of the page and requires a second tap.

### 5. No at-a-glance summary

The Overview page requires loading the iframe, which fetches the latest detection,
renders a chart, and fires several XHR requests before anything meaningful appears.
A lighter, always-visible dashboard panel would address this.

---

## Options Evaluated

### Option A — HTMX (recommended core change)

[HTMX](https://htmx.org) is a ~14 KB JavaScript library that replaces iframes and
full-page navigations with declarative AJAX partial-page swaps. No build step. No
Node.js. Works directly with the existing PHP templates.

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

**Cons:**
- Requires refactoring `index.php` / `views.php` to remove the iframe shell.
- Inline `<script>` blocks in view files need slight adjustment (scripts inside
  HTMX-swapped content must use `htmx:afterSwap` events or be moved to the shell).

**Effort estimate:** Medium — 1–2 days for a careful migration.

---

### Option B — Continue with PHP + vanilla JS (current trajectory)

Keep the iframe architecture and improve it incrementally:
- Add `loading="lazy"` to the iframe.
- Use `postMessage` to avoid iframe height hacks.
- Add `Cache-Control` headers for assets.

**Pros:** Zero new dependencies, purely additive.

**Cons:** Does not fix the root problem. The iframe overhead remains. The "snappy"
feeling the issue asked for is not achievable within an iframe model.

---

### Option C — Full SPA rewrite (React / Vue / Svelte)

Replace the PHP frontend with a modern JS framework that calls PHP API endpoints.

**Pros:** Best possible interactivity; component-based; excellent mobile tooling.

**Cons:**
- Requires a Node.js build toolchain on the Pi or a separate build machine.
- Major rewrite of all frontend templates.
- PHP becomes a pure JSON API layer — significant refactoring.
- Overkill for a single-user household device.
- JavaScript bundles are large unless carefully tree-shaken.

**Recommendation:** Not appropriate for the current stage of the project.

---

### Option D — Progressive Web App (PWA) layer

Add a `manifest.json` and a Service Worker so users can install BirdNET-Pi to
their phone's home screen and get push notifications on new detections.

**Pros:** High-impact mobile improvement; works on top of any of the other options.

**Cons:** On its own, does not fix navigation performance.

**Recommendation:** Implement as a complement to Option A in Phase 2.

---

## Recommended Path Forward

### Phase 1 — Fix the structural bottleneck (HTMX migration)

1. Add HTMX (self-hosted, no CDN dependency) to `homepage/static/`.
2. Refactor `index.php` to remove the `<iframe>`. The outer shell loads once;
   the inner `<main id="content">` is swapped by HTMX on navigation.
3. Adapt each view PHP file to return a plain HTML fragment (most already do).
4. Move the `git fetch` update-check to an async background process or a
   separate AJAX call that fires after the page has already rendered.
5. Add proper `Cache-Control: public, max-age=31536000, immutable` headers for
   the font and static assets (via Caddy config or a PHP header).

**Expected outcome:** Page navigation feels instant. No more scroll-position resets.
Back button works. The Pi's CPU is not blocked by a git network call on every load.

---

### Phase 2 — Dashboard and mobile UX

The `dashboard.php` added in the previous commit is a good starting point. Refine it:

1. **Replace the hamburger dropdown with a bottom navigation bar on mobile.**
   On screens ≤ 640 px, show 4–5 icon+label tabs pinned to the bottom edge
   (Dashboard / Detections / Recordings / Tools). This matches the native mobile
   app pattern users already know.

2. **Add a PWA manifest** (`manifest.json`) and minimal Service Worker that
   caches the shell, CSS, font, and icons. This enables "Add to Home Screen" and
   makes the first paint nearly instant on repeat visits.

3. **Refine the dashboard widgets** based on what bird-watchers actually want to
   see at a glance:
   - Today's detection count + sparkline of detections-per-hour
   - Most recent detection (species name + confidence + audio player)
   - Species count today vs. all-time
   - System health (disk usage, service status) — one small badge, not a full table

---

### Phase 3 — Polish

- Dark mode (`prefers-color-scheme: dark`) CSS variables.
- Swipe gestures on mobile to navigate between main views (HTMX makes this
  easy to add with a small Hammer.js or pointer-events handler).
- Notification badge on the nav when a new species is detected for the first time today.

---

## What Has Already Been Done

| Change | File | Status |
|--------|------|--------|
| Stats widget dashboard (card grid) | `homepage/dashboard.php` | ✅ merged |
| Dashboard CSS (responsive grid, widget cards) | `homepage/style.css` | ✅ merged |
| Dashboard as default view; nav item added | `homepage/views.php` | ✅ merged |

---

## What This Proposal Does NOT Recommend

- Switching PHP for a different backend language (Python/Node). The existing PHP
  is functional and runs well on the Pi. Switching languages would be a massive
  refactor with no user-visible benefit.
- Using a CSS framework like Bootstrap or Tailwind. The current hand-written CSS
  is small and well-suited to the app. Adding a framework would increase page
  weight significantly.
- Removing the SQLite backend in favour of a REST API. The current direct-PHP
  database pattern is appropriate for a single-device app.
