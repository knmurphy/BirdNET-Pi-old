# Field Station OS - FastHTML Implementation

*2026-02-25T13:32:39Z by Showboat 0.6.1*
<!-- showboat-id: 3e735aa7-4f03-4fb7-91a7-d1242ed96ec5 -->

## Overview

Starting fresh with FastHTML per `docs/ui-improvement-proposal.md`.

**Why FastHTML:**
- Python throughout (no Node.js build step)
- HTMX built-in for navigation (no iframe, no full page reload)
- Runs on Pi without build toolchain
- Incremental migration from PHP

**Existing PoC:** `homepage/web_app.py` already implements:
- Dashboard with KPI widgets
- Today's detections table with audio playback
- Species recordings list
- Species detail view
- Charts (Streamlit embed)
- Mobile bottom nav (CSS-only)

**What we need to add:**
- Dark theme (design system from archived React work)
- SSE for real-time updates
- Better typography and visual polish
- Additional views (History, Stats, Settings)

```bash
pip show python-fasthtml 2>/dev/null || echo 'FastHTML not installed'
```

```output
FastHTML not installed
```

```bash
source .venv/bin/activate && pytest tests/test_web_app.py -v
```

```output
============================= test session starts ==============================
platform darwin -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0 -- /Users/knmurphy/Documents/PROJECTS/BirdNET-Pi-old/.venv/bin/python3.14
cachedir: .pytest_cache
rootdir: /Users/knmurphy/Documents/PROJECTS/BirdNET-Pi-old
plugins: anyio-4.12.1, asyncio-1.3.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 4 items

tests/test_web_app.py::TestAppCreation::test_app_exists PASSED           [ 25%]
tests/test_web_app.py::TestAppCreation::test_app_is_fasthtml_instance PASSED [ 50%]
tests/test_web_app.py::TestDashboardRoute::test_dashboard_route_exists PASSED [ 75%]
tests/test_web_app.py::TestDashboardContent::test_dashboard_returns_html_with_title PASSED [100%]

============================== 4 passed in 0.15s ===============================
```



## TDD Cycle 1: App Creation and Dashboard Route

**RED:** Created tests for:
- App exists and is FastHTML instance
- Dashboard route is registered
- Dashboard content contains 'Dashboard' heading

Tests failed: ModuleNotFoundError (module didn't exist)

**GREEN:** Created minimal `homepage/web_app.py`:
- FastHTML app instance
- `/app/dashboard` route
- `_dashboard_content()` returns Div with H2('Dashboard')
- `_shell()` wrapper function (minimal implementation)

All 4 tests passed.



## TDD Cycle 2: Database Query

**RED:** Added test for `get_today_detection_count()` - failed with ImportError

**GREEN:** Delegated to subagent which added:
- Imports: os, sqlite3, date from datetime
- DB_PATH constant
- `get_today_detection_count()` function
- Connects to `~/BirdNET-Pi/scripts/birds.db`, queries today's count

All 5 tests now pass.

