# BirdNET-Pi UI Improvement Proposal

## TL;DR — The "Two Birds, One Stone" Answer

**FastHTML** (Python).

Here is why it solves both problems simultaneously:

| Problem | How FastHTML solves it |
|---------|----------------------|
| **Slow, iframe-based navigation** | FastHTML uses HTMX under the hood — every nav click is a partial-page swap, no iframe, no full-page reload. |
| **PHP codebase the maintainer wants to replace** | FastHTML _is_ Python. It aligns directly with Nachtzuster's stated goal: "I would like an overhaul that does away with the PHP code and moves to some Python web framework (flask, FastHTML, …)." |

Additional reasons it fits this specific project:

- **Python is already the backend language.** `server.py` (TFLite inference), `plotly_streamlit.py` (charts), `utils/notifications.py` (Apprise) — the entire processing stack is Python. FastHTML makes the web tier match.
- **No build toolchain.** No Node.js, no npm, no Webpack. `pip install python-fasthtml` and you are running. This matters on a Raspberry Pi.
- **Same SQLite database.** FastHTML routes connect to `~/BirdNET-Pi/scripts/birds.db` directly using the standard `sqlite3` module — no schema changes, no migration.
- **Proven by BirdNET-Go.** BirdNET-Go ran HTMX (the same engine FastHTML uses) before migrating to Svelte 5. The HTMX approach is proven for this class of app.
- **Incremental migration.** The PHP app continues to run. FastHTML starts at `/app/*`; Caddy routes both. Replace view-by-view. Roll back anytime.
- **A concrete proof-of-concept is already in this branch** — see `homepage/web_app.py`.

### What the migration looks like

```
# Step 1: add one line to the Caddyfile (everything else stays the same)
reverse_proxy /app* localhost:8502

# Step 2: run the FastHTML app
pip install python-fasthtml
python3 homepage/web_app.py   # or add a systemd service

# Step 3: point users to /app instead of /
# The PHP app at / is still fully functional until you are ready to remove it
```

---

## Would Svelte Be an Advantage?

**Short answer: yes, for the _frontend_ — but only after Python owns the backend.**

Svelte is not a competing alternative to FastHTML. It is a different layer of the
stack entirely, and whether it is an advantage depends entirely on which problem you
are trying to solve next.

### What Svelte genuinely does better

BirdNET-Go chose Svelte 5 for the same use case this project has. That is not a
coincidence. Svelte has real advantages for a real-time bird detection dashboard:

**1. True reactive real-time updates (no polling required)**

With FastHTML/HTMX the UI refreshes by repeatedly asking the server
"anything new?" (polling every N seconds). With Svelte + a WebSocket, the
server _pushes_ new detections to every connected browser instantly when they
happen — a bird appears in the list the moment it is detected, with no delay
and no wasted requests.

For a system that detects birds every 15 seconds this matters: a 30-second
poll means the average detection is 15 seconds stale on screen.

**2. Genuinely smooth animations and transitions**

Svelte's built-in `transition:` and `animate:` directives (used extensively in
BirdNET-Go's detection list) make new birds slide in, confidence bars fill
smoothly, and the dashboard feel alive. These are impossible to replicate
naturally in server-rendered HTML without significant custom JavaScript.

**3. Smallest JS bundle of any major framework**

Svelte compiles to vanilla JS at build time — there is no Svelte runtime shipped
to the browser. A typical Svelte app ships less JS than the equivalent HTMX app
(which still requires htmx.min.js) and far less than React or Vue. On a slow Pi
Wi-Fi connection, this matters for time-to-interactive.

**4. Component architecture**

A `<DetectionCard>`, `<AudioPlayer>`, `<SpeciesChart>`, `<SpectrogramViewer>`
Svelte component written once is reused across every page. Changes to the audio
player update everywhere. This is harder in server-rendered HTML fragments.

**5. Type safety throughout the frontend**

Svelte natively supports TypeScript. When the Python API returns a bird detection
object, the Svelte component can be typed against that shape — catching bugs at
build time rather than at runtime on the Pi.

---

### Why Svelte is not the right _first_ step for this project

Svelte is a **frontend** framework. It does not replace the backend. Choosing Svelte
means choosing:

```
Python backend (FastHTML or Flask)  ←  this choice still has to be made
         ↕  JSON API
Svelte frontend  ←  this is what Svelte replaces (HTMX HTML fragments)
         ↕  browser
```

Adding Svelte before the Python backend migration is complete means:
1. The PHP API endpoints must be converted to JSON-returning Python endpoints first.
2. A Node.js build toolchain is required — on a development machine, not the Pi,
   since `npm run build` is too heavy for the Pi to run reliably.
3. The built assets (`dist/`) must be deployed to the Pi separately from the Python
   source. This complicates the `git pull && restart` update story.
4. Contributors now need to know both Python (backend) and JavaScript/TypeScript
   (frontend).

At this stage of the project the backend is still PHP/Python in transition. Adding
a JS build layer on top of an unsettled backend would mean maintaining three
languages simultaneously (PHP, Python, TypeScript/JS).

---

### The two-phase path that uses Svelte correctly

**Phase 1 (now — FastHTML):** Replace PHP web tier with Python. Establish stable
Python API endpoints. The HTMX navigation is good enough and needs no build toolchain.

```
Python FastHTML  →  HTML fragments via HTMX  →  browser
```

**Phase 2 (once Python backend is stable — optional Svelte frontend):** Keep the
Python backend but replace the HTMX HTML responses with JSON responses, and replace
the HTMX navigation with a Svelte SPA built once and served as static files by Caddy.

```
Python FastAPI/Flask  →  JSON  →  Svelte SPA (compiled, served as static files)
```

At Phase 2 the Python backend is already clean and tested. Converting FastHTML route
handlers to return JSON instead of HTML is a small change per route. The Svelte
frontend can then be developed and iterated on a development machine, compiled, and
the `dist/` directory deployed to the Pi — the same pattern BirdNET-Go uses.

---

### Summary: FastHTML now, Svelte optionally later

| Criterion | FastHTML (now) | Svelte (later) |
|-----------|---------------|---------------|
| Requires build toolchain | ✗ No | ✓ Yes (Node.js + Vite) |
| Can replace PHP backend | ✓ Yes | ✗ No (frontend only) |
| Real-time WebSocket push | ✗ No (poll-based) | ✓ Yes |
| Smooth enter/exit animations | ✗ Limited | ✓ Native |
| Bundle size in browser | ~14 KB (HTMX) | ~10–30 KB compiled (no runtime) |
| Contributors need JS knowledge | ✗ No | ✓ Yes |
| Incremental migration from PHP | ✓ Easy | ✗ Requires JSON API first |
| Modelled by BirdNET-Go | Transitional step | ✓ Final state |
| Right time in this project | ✓ Now | Later — after Python backend is stable |

The recommendation stays **FastHTML as the first move** because it solves the
PHP→Python migration and the navigation performance problem simultaneously with the
least added complexity. Svelte is the realistic evolution _after_ that migration
is complete if the project wants BirdNET-Go-level UI polish.

---

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

### Option A — FastHTML (Python + HTMX) ⭐ Recommended

[FastHTML](https://fastht.ml) is a Python micro-framework that generates HTML
directly from Python functions and wires HTMX navigation in automatically.

**How it works:**

```python
from fasthtml.common import FastHTML, Div, H2, serve

app = FastHTML()

@app.get("/app/dashboard")
def dashboard():
    return Div(H2("Dashboard"), ...)   # returned as HTML fragment via HTMX
```

- The outer shell (`<html>/<head>/<body>`) is sent once.
- Every nav click fires an HTMX `GET` that swaps only `<main id="content">`.
- No iframe, no full-page reload.

**The proof-of-concept** — `homepage/web_app.py` in this branch — already implements:
- Dashboard with KPI widgets (auto-refresh spectrogram, today's chart)
- Today's Detections table with audio playback
- Species list (recordings)
- Per-species detail page
- Mobile bottom nav bar (CSS-only, no JS)
- All connected to the existing SQLite database

**Pros:**
- Kills both birds: Python backend migration + HTMX navigation in one move.
- No Node.js, no npm, no build step.
- Works alongside the PHP app during migration (different path prefix).
- The Python venv (`~/BirdNET-Pi/birdnet/`) is already on the Pi.

**Cons:**
- `python-fasthtml` is a new pip dependency.
- Requires a new systemd service + one Caddy `reverse_proxy` line.
- Full feature parity with PHP takes time (view-by-view migration).

**Effort estimate:** Low to start (PoC is done); Medium for full feature parity.

---

### Option B — HTMX migration of the PHP codebase

[HTMX](https://htmx.org) is a ~14 KB JavaScript library that replaces iframes and
full-page navigations with declarative AJAX partial-page swaps. No build step. No
Node.js. Works directly with the existing PHP templates.

This fixes the iframe performance problem without touching the PHP code.

**Pros:**
- Backend PHP stays almost identical — minor change per view file.
- ~14 KB dependency, no build toolchain, works on PHP 7/8.
- Fixes the Nachtzuster issue #556 scroll bug as a side-effect.

**Cons:**
- PHP stays as the web tier — not aligned with the Python migration direction.
- Inline `<script>` blocks in view files need adjustment (HTMX swap events).
- Still two languages to maintain (PHP + Python).

**Recommendation:** Valid intermediate step; superseded by Option A if Python is the
long-term goal.

---

### Option C — Cherry-pick from cpieper/BirdNET-Pibird

cpieper submitted a "Modernize v1" PR (562) to Nachtzuster in Jan 2026 with 421
additions / 309 deletions and it was closed without review. Their fork
([BirdNET-Pibird](https://github.com/cpieper/BirdNET-Pibird)) contains the rejected
modernisation work and is actively continued. The changes are PHP-only — safe to
cherry-pick.

**Pros:** Real, tested work. Zero new dependencies.

**Cons:** Doesn't fix the iframe root cause. Doesn't move toward Python.

**Recommendation:** Cherry-pick only if staying entirely in PHP.

---

### Option D — Python backend with Flask

Flask is more established than FastHTML; more community resources available.

**Pros:** More contributors know Flask; extensive documentation; Jinja2 templates.

**Cons:**
- Navigation still needs HTMX (or something else) bolted on separately.
- Jinja2 templates are a separate language from Python code.
- More boilerplate than FastHTML for this use case.

**Recommendation:** FastHTML is Flask + HTMX in one, minus the boilerplate.

---

### Option E — Svelte SPA frontend (long-term evolution)

Svelte 5 is the frontend technology [BirdNET-Go](https://github.com/tphakala/birdnet-go)
uses. It compiles to vanilla JS (no runtime), supports native WebSocket reactivity,
and produces genuinely smooth, mobile-first UIs with built-in transition animations.

**Architecture when this makes sense:**

```
Python backend (FastHTML routes return JSON instead of HTML)
        ↓
Svelte SPA (compiled by Vite on a dev machine, dist/ deployed to Pi)
        ↓
Caddy serves dist/ as static files; API calls proxy to Python backend
```

**Pros:**
- Real-time WebSocket push (new detections appear instantly, no polling).
- Built-in `transition:` and `animate:` directives for fluid UI.
- Smallest compiled JS of any major framework (no runtime overhead).
- TypeScript support for safer API contracts.
- Modular components (`<DetectionCard>`, `<AudioPlayer>`, `<SpeciesChart>`).

**Cons:**
- Frontend-only: still requires a Python (or other) backend.
- Requires Node.js + Vite build toolchain on a development machine (not on the Pi).
- `dist/` directory must be deployed separately from Python source.
- Contributors need JavaScript/TypeScript knowledge in addition to Python.
- Not practical until the Python API layer is stable and serving JSON.

**Recommendation:** The right evolution _after_ the FastHTML migration (Option A) is
complete. At that point the FastHTML routes can return JSON instead of HTML fragments
with minimal code change, and Svelte handles the frontend. This is exactly the path
BirdNET-Go took (HTMX → Svelte 5).

---

### Option F — Continue with PHP + vanilla JS (status quo)

Keep the iframe architecture and improve it incrementally.

**Pros:** Zero new dependencies, purely additive.

**Cons:** Does not fix the root problem. The iframe overhead remains. Not aligned
with the Python migration direction.

---

## Recommended Path Forward

### Phase 1 — FastHTML proof-of-concept → incremental migration (in progress)

1. ✅ `homepage/web_app.py` — FastHTML PoC serving dashboard, detections,
   recordings, and species detail pages at `/app/*`. Reads the live SQLite DB.
2. Add `python-fasthtml` to `requirements.txt`.
3. Add a `web_app.service` systemd unit (mirrors the pattern of `birdnet_stats.service`).
4. Add `reverse_proxy /app* localhost:8502` to the Caddyfile template in
   `scripts/install_services.sh`.
5. ~~Move the `git fetch` update-check to an async background process.~~ *(Done —
   the fetch now runs non-blocking at most once/hr.)*

**Expected outcome:** Users can navigate to `/app/dashboard` and get a fast,
iframe-free, mobile-responsive UI. The PHP app at `/` continues working untouched.

---

### Phase 2 — Parity + replace PHP views one-by-one

Port the remaining PHP views to FastHTML:
- `spectrogram.php` → `/app/spectrogram`
- `history.php` (Daily Charts) → `/app/charts` (already uses the Streamlit embed)
- `play.php` (Recordings browser) → `/app/recordings/{date}`
- `stats.php` (Best Recordings / Species Stats) → already done as `/app/species/{slug}`
- Admin views (Settings, Services, System Controls) — last to migrate; PHP is fine
  for these until parity is solid.

---

### Phase 3 — Remove PHP dependency

Once all public views are in FastHTML:
1. Remove `php php-fpm php-sqlite3 php-curl` from `install_services.sh`.
2. Replace `php_fastcgi` in the Caddyfile with `reverse_proxy /app* localhost:8502`.
3. Redirect `/` → `/app/dashboard`.

---

### Phase 4 — Polish (informed by BirdNET-Go's feature set)

- Dark mode via `prefers-color-scheme: dark` CSS variables.
- Per-detection first-occurrence-today badge.
- PWA `manifest.json` + minimal Service Worker (install to home screen).
- Multi-language support (Jinja2-style templates make i18n straightforward).
- Notification badge on the nav when a new species is detected for the first time today.

### Phase 5 — Optional: Svelte frontend (if real-time push is a priority)

Once the Python backend is stable and all views serve JSON, the HTMX HTML-fragment
responses can be swapped for a Svelte SPA:

1. Add `content_type="application/json"` to FastHTML route handlers (one line each).
2. Scaffold a Svelte 5 + Vite frontend in `frontend/` on a development machine.
3. Build: `npm run build` → `frontend/dist/` → deploy to Pi.
4. Add `root * /home/pi/BirdNET-Pi/frontend/dist` to the Caddyfile;
   `reverse_proxy /api* localhost:8502` for the Python backend.

This is the same split BirdNET-Go uses (Go backend + Svelte frontend). The advantage
at this stage is real-time WebSocket push (detections appear instantly) and smooth
animated transitions. See the "Would Svelte Be an Advantage?" section above for the
full trade-off analysis.

---

## What Has Already Been Done in This Branch

| Change | File | Status |
|--------|------|--------|
| Stats widget dashboard (card grid) | `homepage/dashboard.php` | ✅ done (PHP) |
| Dashboard CSS (responsive grid, widget cards) | `homepage/style.css` | ✅ done |
| Dashboard as default view; nav item added | `homepage/views.php` | ✅ done |
| Non-blocking git fetch (1-hour file cache) | `homepage/views.php` | ✅ done |
| FastHTML PoC with dashboard, detections, recordings, species | `homepage/web_app.py` | ✅ done |
| Root-cause analysis + ecosystem research + FastHTML recommendation | `docs/ui-improvement-proposal.md` | ✅ this file |

---

## What This Proposal Does NOT Recommend Doing Now

- **A purely visual CSS overhaul of the PHP codebase** — Nachtzuster's maintainer
  has explicitly said this is not a priority. Invest in FastHTML instead.
- **Svelte as the first step** — Svelte is frontend-only; it cannot replace PHP
  on its own. The Python backend must be established first. See the "Would Svelte
  Be an Advantage?" section and Phase 5 in the roadmap for when it does make sense.
- **A full SPA rewrite before the backend is stable** — jumping straight to a
  Svelte SPA while the backend is still PHP would mean maintaining three languages
  simultaneously (PHP, Python, TypeScript/JS) with no clear migration path.
- **Switching to a CSS framework like Bootstrap or Tailwind** — the current
  hand-written CSS is small and well-suited. A framework would increase page weight.

