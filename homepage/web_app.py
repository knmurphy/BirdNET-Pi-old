"""
Field Station OS - FastHTML Web Application

A Python-native web UI for passive acoustic monitoring.
Built with FastHTML for HTMX-based navigation (no iframe, no full page reload).
"""
import os
import shutil
import sqlite3
import logging
import time
from datetime import datetime

from starlette.responses import FileResponse, Response
from fasthtml.common import (
    FastHTML, serve,
    Html, Head, Body, Title, Meta, Link, Style,
    Main, Nav, Header,
    Div, H2, H3, P, A, Audio, Source,
)

# Database path - can be overridden via environment variable
DB_PATH = os.environ.get(
    "BIRDNET_DB_PATH",
    os.path.join(os.path.dirname(__file__), '..', 'scripts', 'birds.db')
)

# Recordings path for disk usage calculation
RECORDINGS_PATH = os.environ.get(
    "BIRDNET_RECORDINGS_PATH",
    os.path.expanduser("~/BirdSongs")
)

# Simple time-based cache for recordings size (expensive os.walk)
_RECORDINGS_SIZE_CACHE: dict = {"value": 0.0, "ts": 0.0}
_RECORDINGS_CACHE_TTL = 300  # seconds


def _get_recordings_size_gb() -> float:
    """Return total size of recordings in GB, cached for 5 minutes."""
    now = time.monotonic()
    if now - _RECORDINGS_SIZE_CACHE["ts"] < _RECORDINGS_CACHE_TTL:
        return _RECORDINGS_SIZE_CACHE["value"]
    total_bytes = 0
    if os.path.exists(RECORDINGS_PATH):
        total_bytes = sum(
            os.path.getsize(os.path.join(dirpath, fname))
            for dirpath, _, fnames in os.walk(RECORDINGS_PATH)
            for fname in fnames
        )
    result = total_bytes / (1024 ** 3)
    _RECORDINGS_SIZE_CACHE["value"] = result
    _RECORDINGS_SIZE_CACHE["ts"] = now
    return result


def get_today_detection_count() -> int:
    """Return the total number of detections today."""
    con = None
    try:
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        today = datetime.now().strftime("%Y-%m-%d")
        cur = con.execute("SELECT COUNT(*) FROM detections WHERE Date = ?", (today,))
        row = cur.fetchone()
        return row[0] if row else 0
    except sqlite3.Error:
        return 0
    finally:
        if con:
            con.close()


def get_today_species_count() -> int:
    """Return the count of distinct species detected today."""
    con = None
    try:
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        today = datetime.now().strftime("%Y-%m-%d")
        cur = con.execute(
            "SELECT COUNT(DISTINCT Com_Name) FROM detections WHERE Date = ?", (today,)
        )
        row = cur.fetchone()
        return row[0] if row else 0
    except sqlite3.Error:
        return 0
    finally:
        if con:
            con.close()


def get_total_detection_count() -> int:
    """Return the total number of detections (all time)."""
    con = None
    try:
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        cur = con.execute("SELECT COUNT(*) FROM detections")
        row = cur.fetchone()
        return row[0] if row else 0
    except sqlite3.Error:
        return 0
    finally:
        if con:
            con.close()


def get_total_species_count() -> int:
    """Return the count of distinct species (all time)."""
    con = None
    try:
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        cur = con.execute("SELECT COUNT(DISTINCT Com_Name) FROM detections")
        row = cur.fetchone()
        return row[0] if row else 0
    except sqlite3.Error:
        return 0
    finally:
        if con:
            con.close()


def get_latest_detection() -> dict | None:
    """Return the most recent detection, or None if unavailable."""
    con = None
    try:
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        con.row_factory = sqlite3.Row
        cur = con.execute(
            "SELECT Com_Name, Sci_Name, Date, Time, Confidence, File_Name "
            "FROM detections ORDER BY Date DESC, Time DESC LIMIT 1"
        )
        row = cur.fetchone()
        if row:
            return {
                "com_name": row["Com_Name"],
                "sci_name": row["Sci_Name"],
                "date": row["Date"],
                "time": row["Time"],
                "confidence": row["Confidence"],
                "file_name": row["File_Name"],
            }
        return None
    except sqlite3.Error:
        return None
    finally:
        if con:
            con.close()


def get_hourly_detections() -> dict:
    """Return a dict mapping hour (int 0-23) to detection count for today."""
    con = None
    try:
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        today = datetime.now().strftime("%Y-%m-%d")
        cur = con.execute(
            "SELECT CAST(strftime('%H', Time) AS INTEGER) as hour, COUNT(*) "
            "FROM detections WHERE Date = ? GROUP BY hour",
            (today,)
        )
        rows = cur.fetchall()
        return {int(row[0]): row[1] for row in rows}
    except sqlite3.Error:
        return {}
    finally:
        if con:
            con.close()


def get_system_health() -> dict:
    """Return system health metrics including disk, database, and recordings size."""
    try:
        disk = shutil.disk_usage("/")
        disk_used_gb = (disk.total - disk.free) / (1024 ** 3)
        disk_total_gb = disk.total / (1024 ** 3)
        disk_percent = (disk_used_gb / disk_total_gb * 100) if disk_total_gb > 0 else 0.0

        db_path = os.path.abspath(DB_PATH)
        db_size_mb = os.path.getsize(db_path) / (1024 ** 2) if os.path.exists(db_path) else 0.0

        recordings_gb = _get_recordings_size_gb()

        return {
            "disk_used_gb": disk_used_gb,
            "disk_total_gb": disk_total_gb,
            "disk_percent": disk_percent,
            "db_size_mb": db_size_mb,
            "recordings_gb": recordings_gb,
        }
    except Exception:
        return {
            "disk_used_gb": 0.0,
            "disk_total_gb": 0.0,
            "disk_percent": 0.0,
            "db_size_mb": 0.0,
            "recordings_gb": 0.0,
        }


# Design System - Dark Theme
APP_CSS = """
:root {
  /* Color Palette - Dark Theme (default) */
  --bg: #0D0F0B;
  --bg2: #141610;
  --bg3: #1A1D16;
  --border: #252820;
  --text: #F0EAD2;
  --text2: #9A9B8A;
  --text3: #5A5C4E;
  --accent: #C8E6A0;
  --amber: #E8C547;
  --red: #E05252;

  /* Spacing Scale (4px base) */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;

  /* Border Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 9999px;

  /* Typography */
  --font-mono: 'DM Mono', monospace;
  --font-display: 'Fraunces', serif;
  --font-body: 'Source Serif 4', Georgia, serif;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.5);
}

/* Reset */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

/* Base styles */
html { font-size: 16px; }
body {
  font-family: var(--font-body);
  background: var(--bg);
  color: var(--text);
  line-height: 1.5;
  min-height: 100dvh;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }

/* App Shell */
.app-shell {
  display: flex;
  flex-direction: column;
  min-height: 100dvh;
}

/* Topbar / Header */
.topbar {
  background: var(--bg2);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  font-family: var(--font-mono);
  font-size: 12px;
}

/* Main content area */
#content {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-4);
}

/* Bottom navigation (mobile) */
.bottom-nav {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: var(--bg2);
  border-top: 1px solid var(--border);
  justify-content: space-around;
  padding: var(--space-2) 0;
}
.bottom-nav a {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-2) var(--space-1);
  font-size: 11px;
  font-family: var(--font-mono);
  color: var(--text2);
  text-decoration: none;
  flex: 1;
  transition: color var(--transition-fast, 150ms ease);
}
.bottom-nav a:hover, .bottom-nav a.active {
  color: var(--accent);
}

/* Widget grid */
.widget-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

/* Widget cards */
.widget {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  box-shadow: var(--shadow-sm);
}
.widget:hover {
  box-shadow: var(--shadow-md);
}
.widget-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text2);
  font-family: var(--font-mono);
  margin-bottom: var(--space-2);
}
.widget-value {
  font-size: 28px;
  font-weight: bold;
  color: var(--accent);
  font-family: var(--font-display);
}

/* Confidence color coding */
.conf-high { color: var(--accent); }
.conf-medium { color: var(--amber); }
.conf-low { color: var(--red); }

/* Hourly activity chart */
.hourly-chart {
  margin-bottom: var(--space-4);
}
.hourly-bar-row {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-1);
  font-family: var(--font-mono);
  font-size: 12px;
}
.hourly-label {
  width: 40px;
  color: var(--text2);
  text-align: right;
  flex-shrink: 0;
}
.hourly-bar-container {
  flex: 1;
  height: 16px;
  background: var(--bg3);
  border-radius: var(--radius-sm);
  overflow: hidden;
}
.hourly-bar {
  height: 100%;
  background: var(--accent);
  border-radius: var(--radius-sm);
  transition: width 0.3s ease;
}
.hourly-count {
  width: 40px;
  color: var(--text);
  text-align: right;
  flex-shrink: 0;
}

/* System health section */
.health-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: var(--space-3);
  margin-top: var(--space-4);
}
.health-item {
  background: var(--bg3);
  padding: var(--space-3);
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
}
.health-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text2);
  font-family: var(--font-mono);
  margin-bottom: var(--space-1);
}
.health-value {
  font-size: 18px;
  font-weight: bold;
  color: var(--accent);
  font-family: var(--font-display);
}
.health-detail {
  font-size: 11px;
  color: var(--text3);
  margin-top: var(--space-1);
}

/* Error state */
.error-message {
  color: var(--red);
  font-family: var(--font-mono);
  font-size: 12px;
  padding: var(--space-3);
  background: var(--bg3);
  border-radius: var(--radius-md);
  border: 1px solid var(--red);
}

/* Responsive */
@media (max-width: 640px) {
  .bottom-nav { display: flex; }
  #content { padding-bottom: 72px; }
  .widget-grid { grid-template-columns: 1fr 1fr; }
  .widget-value { font-size: 22px; }
}
"""


# Create the FastHTML application
app = FastHTML()


@app.get("/audio/{file_name:path}")
def serve_audio(file_name: str):
    """Serve a recording audio file, guarding against path traversal."""
    recordings_dir = os.path.realpath(RECORDINGS_PATH)
    requested = os.path.realpath(os.path.join(recordings_dir, file_name))
    # Only allow paths strictly inside the recordings directory
    if not requested.startswith(recordings_dir + os.sep):
        return Response(status_code=404)
    if not os.path.isfile(requested):
        return Response(status_code=404)
    return FileResponse(requested, media_type="audio/wav")


@app.get("/app/dashboard")
def dashboard():
    """Render the dashboard page."""
    return _shell(_dashboard_content(), "/app/dashboard")


def _dashboard_content():
    """Generate the dashboard content using direct database queries."""
    today_count = get_today_detection_count()
    species_count = get_today_species_count()
    latest = get_latest_detection()

    if latest:
        latest_widget = Div(
            Div("Latest Detection", cls="widget-label"),
            Div(latest["com_name"], cls="widget-value", style="font-size: 14px;"),
            cls="widget"
        )
    else:
        latest_widget = Div(
            Div("Latest Detection", cls="widget-label"),
            Div("No detections yet", cls="widget-value", style="font-size: 14px;"),
            cls="widget"
        )

    return Div(
        H2("Dashboard"),
        Div(
            Div("Today's Detections", cls="widget-label"),
            Div(str(today_count), cls="widget-value"),
            cls="widget"
        ),
        Div(
            Div("Today's Species", cls="widget-label"),
            Div(str(species_count), cls="widget-value"),
            cls="widget"
        ),
        latest_widget,
        cls="widget-grid"
    )


def _shell(content, current_path: str = "/app/dashboard"):
    """Wrap content in the app shell with header and navigation."""
    current_time = datetime.now().strftime("%H:%M:%S")

    tabs = [
        ("Dashboard", "/app/dashboard"),
        ("Detections", "/app/detections"),
        ("Species", "/app/species"),
        ("Stats", "/app/stats"),
        ("Settings", "/app/settings"),
    ]

    nav_links = [
        A(name, href=path, cls="active" if current_path == path else "")
        for name, path in tabs
    ]

    return Html(
        Head(
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            Link(rel="preconnect", href="https://fonts.googleapis.com"),
            Link(rel="preconnect", href="https://fonts.gstatic.com", crossorigin=""),
            Link(
                rel="stylesheet",
                href=(
                    "https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500"
                    "&family=Fraunces:wght@400;700"
                    "&family=Source+Serif+4:ital,wght@0,400;1,400&display=swap"
                ),
            ),
            Title("Field Station"),
            Style(APP_CSS),
        ),
        Body(
            Div(
                Header(
                    f"Field Station - {current_time}",
                    cls="topbar",
                ),
                Main(content, id="content"),
                Nav(*nav_links, cls="bottom-nav"),
                cls="app-shell",
            ),
        ),
    )


@app.get("/app/detections")
def detections():
    """Render the detections page."""
    return _shell(_detections_content(), "/app/detections")


def _confidence_class(confidence: float) -> str:
    """Return the appropriate confidence color class."""
    if confidence >= 0.80:
        return "conf-high"
    elif confidence >= 0.50:
        return "conf-medium"
    else:
        return "conf-low"


def _detections_content():
    """Generate the detections list content using direct database queries."""
    con = None
    rows = None
    try:
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        today = datetime.now().strftime("%Y-%m-%d")
        cur = con.execute(
            "SELECT Com_Name, Sci_Name, Time, Confidence, File_Name "
            "FROM detections WHERE Date = ? ORDER BY Time DESC LIMIT 50",
            (today,)
        )
        rows = cur.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Database error in _detections_content: {e}")
        return Div(
            H2("Today's Detections"),
            P("Unable to load detections", cls="error-message"),
        )
    finally:
        if con:
            con.close()

    if not rows:
        return Div(H2("Today's Detections"), P("No detections yet today."))

    items = []
    for row in rows:
        com_name, sci_name, time, confidence, file_name = row
        conf_class = _confidence_class(confidence or 0.0)
        audio_el = Audio(
            Source(src=f"/audio/{file_name}", type="audio/wav"),
            controls=True,
        ) if file_name else P("(no audio)")
        items.append(
            Div(
                Div(f"{com_name} ({sci_name}) — {time} — {(confidence or 0)*100:.0f}%",
                    cls=conf_class),
                audio_el,
                cls="detection-item"
            )
        )

    return Div(H2("Today's Detections"), *items)


@app.get("/app/species")
def species():
    """Render the species page."""
    return _shell(_species_content(), "/app/species")


def _species_content():
    """Generate the species list content using direct database queries."""
    con = None
    rows = None
    try:
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        today = datetime.now().strftime("%Y-%m-%d")
        cur = con.execute(
            "SELECT Com_Name, Sci_Name, COUNT(*) as cnt, MAX(Confidence) as max_conf "
            "FROM detections WHERE Date = ? GROUP BY Sci_Name ORDER BY Com_Name ASC",
            (today,)
        )
        rows = cur.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Database error in _species_content: {e}")
        return Div(
            H2("Today's Species"),
            P("Error loading species", cls="error-message"),
        )
    finally:
        if con:
            con.close()

    if not rows:
        return Div(H2("Today's Species"), P("No species detected today."))

    items = [
        Div(
            f"{row[0]} ({row[1]}) — {row[2]} detections (max: {(row[3] or 0)*100:.0f}%)",
            cls=_confidence_class(row[3] or 0.0)
        )
        for row in rows
    ]
    return Div(H2("Today's Species"), *items)


@app.get("/app/stats")
def stats():
    """Render the stats page."""
    return _shell(_stats_content(), "/app/stats")


def _hourly_activity_section() -> Div:
    """Generate hourly activity bar chart for today using database data."""
    hourly_data = get_hourly_detections()

    if not hourly_data:
        return Div(
            H3("Today's Activity"),
            P("No detections yet today.", cls="text2"),
            cls="hourly-chart"
        )

    max_count = max(hourly_data.values()) if hourly_data else 1

    bar_rows = []
    for hour in range(24):
        count = hourly_data.get(hour, 0)
        bar_width = (count / max_count * 100) if max_count > 0 else 0
        bar_rows.append(
            Div(
                Div(f"{hour:02d}:00", cls="hourly-label"),
                Div(
                    Div(cls="hourly-bar", style=f"width: {bar_width:.1f}%"),
                    cls="hourly-bar-container"
                ),
                Div(str(count), cls="hourly-count"),
                cls="hourly-bar-row"
            )
        )

    return Div(
        H3("Today's Activity"),
        Div(*bar_rows),
        cls="hourly-chart",
    )


def _system_health_section() -> Div:
    """Generate system health widgets using direct system queries."""
    health = get_system_health()

    return Div(
        H3("System Health"),
        Div(
            Div(
                Div("Disk Usage", cls="health-label"),
                Div(f"{health['disk_used_gb']:.1f} / {health['disk_total_gb']:.0f} GB", cls="health-value"),
                Div(f"{health['disk_percent']:.1f}% used", cls="health-detail"),
                cls="health-item"
            ),
            Div(
                Div("Database", cls="health-label"),
                Div(f"{health['db_size_mb']:.1f} MB", cls="health-value"),
                cls="health-item"
            ),
            Div(
                Div("Recordings", cls="health-label"),
                Div(f"{health['recordings_gb']:.2f} GB", cls="health-value"),
                cls="health-item"
            ),
            cls="health-grid"
        ),
    )


def _stats_content():
    """Generate the stats content using direct database queries."""
    today_count = get_today_detection_count()
    total_count = get_total_detection_count()
    today_species = get_today_species_count()
    total_species = get_total_species_count()

    return Div(
        H2("Statistics"),
        Div(
            Div("Today's Detections", cls="widget-label"),
            Div(f"{today_count:,}", cls="widget-value"),
            cls="widget"
        ),
        Div(
            Div("Total Detections", cls="widget-label"),
            Div(f"{total_count:,}", cls="widget-value"),
            cls="widget"
        ),
        Div(
            Div("Today's Species", cls="widget-label"),
            Div(f"{today_species:,}", cls="widget-value"),
            cls="widget"
        ),
        Div(
            Div("Total Species", cls="widget-label"),
            Div(f"{total_species:,}", cls="widget-value"),
            cls="widget"
        ),
        _hourly_activity_section(),
        _system_health_section(),
    )


@app.get("/app/settings")
def settings():
    """Render the settings page."""
    return _shell(_settings_content(), "/app/settings")


def _settings_content():
    """Generate the settings content."""
    return Div(
        H2("Settings"),
        P("Settings are managed via the BirdNET-Pi configuration file.", cls="text2"),
    )


if __name__ == "__main__":
    serve(port=8502)
