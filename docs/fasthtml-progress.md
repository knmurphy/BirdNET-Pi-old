# Field Station OS - FastHTML Implementation

*2026-02-25T16:55:00Z - Task tracking moved to Beads*
<!-- showboat-id: 3e735aa7-4f03-4fb7-91a7-d1242ed96ec5 -->

## Overview

Starting fresh with FastHTML per `docs/ui-improvement-proposal.md`.

**Why FastHTML:**
- Python throughout (no Node.js build step)
- HTMX built-in for navigation (no iframe, no full page reload)
- Runs on Pi without build toolchain
- Incremental migration from PHP

## Current Status

```bash
source .venv/bin/activate && pytest tests/test_web_app.py -v
```

**21 tests passing** as of 2026-02-25.

## Task Tracking

**All tasks are tracked in Beads.** Run `bd list` to see open tasks.

```bash
bd list          # Show all open tasks
bd ready         # Show unblocked work
bd show <id>     # Show task details
```

## Completed TDD Cycles

1. **App Creation and Dashboard Route** - FastHTML app, `/app/dashboard` route
2. **Database Query** - `get_today_detection_count()`, database connectivity
3. **Settings Route** - `/app/settings` route handler
4. **Design System** - APP_CSS with dark theme, CSS variables, Google Fonts
5. **Navigation and Routes** - All 5 routes with navigation shell
6. **Widget Classes** - Dashboard uses .widget, .widget-label, .widget-value
7. **Confidence Color Coding** - `_confidence_class()` helper applied to detections

## Code Review Findings (2026-02-25)

Tracked in Beads as:
- `BirdNET-Pi-old-otx` - Apply confidence classes to species content (P1)
- `BirdNET-Pi-old-rx0` - Improve test assertions (P1)
- `BirdNET-Pi-old-byw` - Add tests for total count functions (P1)
- `BirdNET-Pi-old-7nx` - Add error logging to database functions (P2)
- `BirdNET-Pi-old-2w7` - Add database error path tests (P2)

## Feature Backlog

Tracked in Beads as:
- `BirdNET-Pi-old-ceo` - Audio playback on detections (P1)
- `BirdNET-Pi-old-cz0` - Hourly activity chart (P2)
- `BirdNET-Pi-old-mkr` - System health metrics (P2)

Future enhancements not yet in Beads:
- SSE for real-time updates
- PWA manifest and service worker
