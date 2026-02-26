"""
Field Station OS - FastHTML Web Application

A Python-native web UI for passive acoustic monitoring.
Built with FastHTML for HTMX-based navigation (no iframe, no full page reload).

Following TDD: This code is written to pass tests, then refactored.
"""
import os
import shutil
import sqlite3
import logging
import time
from datetime import date, datetime

from fasthtml.common import (
    FastHTML, serve,
    Html, Head, Body, Title, Meta, Link, Style,
    Main, Nav, Header,
    Div, H2, H3, P, A, Audio,
)

# Database configuration
DB_PATH = os.path.join(os.path.expanduser("~"), "BirdNET-Pi", "scripts", "birds.db")


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

/* Responsive */
@media (max-width: 640px) {
  .bottom-nav { display: flex; }
  #content { padding-bottom: 72px; }
  .widget-grid { grid-template-columns: 1fr 1fr; }
  .widget-value { font-size: 22px; }
}
"""


def get_today_detection_count() -> int:
    """Query today's detection count from the database."""
    today = date.today().isoformat()
    try:
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        cursor = con.execute(
            "SELECT COUNT(*) FROM detections WHERE Date = ?",
            (today,)
        )
        count = cursor.fetchone()[0]
        con.close()
        return count
    except Exception as e:
        logging.error(f"Error getting today's detection count: {e}")
        return 0


def get_today_species_count() -> int:
    """Query count of distinct species detected today."""
    today = date.today().isoformat()
    try:
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        cursor = con.execute(
            "SELECT COUNT(DISTINCT Com_Name) FROM detections WHERE Date = ?",
            (today,)
        )
        count = cursor.fetchone()[0]
        con.close()
        return count
    except Exception as e:
        logging.error(f"Error getting today's species count: {e}")
        return 0


def get_latest_detection():
    """Get the most recent detection."""
    try:
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        con.row_factory = sqlite3.Row
        cursor = con.execute(
            "SELECT Com_Name, Time, Confidence FROM detections ORDER BY Date DESC, Time DESC LIMIT 1"
        )
        row = cursor.fetchone()
        con.close()
        if row:
            return dict(row)
        return None
    except Exception as e:
        logging.error(f"Error getting latest detection: {e}")
        return None


# Create the FastHTML application
app = FastHTML()


@app.get("/app/dashboard")
def dashboard():
    """Render the dashboard page."""
    return _shell(_dashboard_content(), "/app/dashboard")


def _dashboard_content():
    """Generate the dashboard content."""
    today_count = get_today_detection_count()
    species_count = get_today_species_count()
    latest = get_latest_detection()

    widgets = [
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
    ]

    if latest:
        widgets.append(
            Div(
                Div("Latest Detection", cls="widget-label"),
                Div(f"{latest['Com_Name']} ({latest['Time']})", cls="widget-value"),
                cls="widget"
            )
        )
    else:
        widgets.append(
            Div(
                Div("Latest Detection", cls="widget-label"),
                Div("No detections yet", cls="widget-value"),
                cls="widget"
            )
        )

    return Div(*widgets, cls="widget-grid")


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
                href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Fraunces:wght@400;700&family=Source+Serif+4:ital,wght@0,400;1,400&display=swap"
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
    """Generate the detections list content."""
    today = date.today().isoformat()
    try:
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        con.row_factory = sqlite3.Row
        cursor = con.execute(
            "SELECT Com_Name, Sci_Name, Time, Confidence, File_Name FROM detections WHERE Date = ? ORDER BY Time DESC LIMIT 50",
            (today,)
        )
        rows = cursor.fetchall()
        con.close()

        if not rows:
            return Div(H2("Today's Detections"), P("No detections yet today."))

        items = [
            Div(
                f"{row['Time']} - {row['Com_Name']} ({float(row['Confidence'])*100:.0f}%%)",
                Audio(controls=True, preload="none", src=row['File_Name']),
                cls=_confidence_class(float(row['Confidence']))
            )
            for row in rows
        ]
        return Div(H2("Today's Detections"), *items)
    except Exception as e:
        logging.error(f"Error loading detections: {e}")
        return Div(H2("Today's Detections"), P("Unable to load detections."))


@app.get("/app/species")
def species():
    """Render the species page."""
    return _shell(_species_content(), "/app/species")


def _species_content():
    """Generate the species list content."""
    today = date.today().isoformat()
    try:
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        con.row_factory = sqlite3.Row
        cursor = con.execute(
            """SELECT Com_Name, Sci_Name, COUNT(*) as count,
                 MAX(Confidence) as max_conf, MAX(Time) as last_seen
                 FROM detections WHERE Date = ?
                 GROUP BY Com_Name ORDER BY count DESC""",
            (today,)
        )
        rows = cursor.fetchall()
        con.close()

        if not rows:
            return Div(H2("Today's Species"), P("No species detected today."))

        items = [
            Div(
                f"{r['Com_Name']} - {r['count']} detections (max: {float(r['max_conf'])*100:.0f}%%)",
                cls=_confidence_class(float(r['max_conf']))
            )
            for r in rows
        ]
        return Div(H2("Today's Species"), *items)
    except Exception as e:
        logging.error(f"Error loading species: {e}")
        return Div(H2("Today's Species"), P("Error loading species."))


def get_total_detection_count() -> int:
    """Get total detections (all time)."""
    try:
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        cursor = con.execute("SELECT COUNT(*) FROM detections")
        count = cursor.fetchone()[0]
        con.close()
        return count
    except Exception as e:
        logging.error(f"Error getting total detection count: {e}")
        return 0


def get_total_species_count() -> int:
    """Get total distinct species (all time)."""
    try:
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        cursor = con.execute("SELECT COUNT(DISTINCT Com_Name) FROM detections")
        count = cursor.fetchone()[0]
        con.close()
        return count
    except Exception as e:
        logging.error(f"Error getting total species count: {e}")
        return 0


def get_hourly_detections() -> dict:
    """Get count of detections per hour for today."""
    today = date.today().isoformat()
    try:
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        try:
            cursor = con.execute(
                "SELECT CAST(SUBSTR(Time, 1, 2) AS INTEGER) as hour, COUNT(*) "
                "FROM detections WHERE Date = ? GROUP BY hour",
                (today,)
            )
            rows = cursor.fetchall()
        finally:
            con.close()
        return {int(row[0]): row[1] for row in rows}
    except Exception as e:
        logging.error(f"Error getting hourly detections: {e}")
        return {}


_HEALTH_CACHE: dict = {}
_HEALTH_CACHE_TTL = 60  # seconds


def get_system_health() -> dict:
    """Get system health metrics from filesystem, cached for 60 seconds."""
    now = time.monotonic()
    if _HEALTH_CACHE.get('expires', 0) > now:
        return _HEALTH_CACHE['data']

    try:
        db_size_mb = os.path.getsize(DB_PATH) / (1024 * 1024) if os.path.exists(DB_PATH) else 0.0
    except Exception:
        db_size_mb = 0.0

    audio_path = os.path.join(os.path.expanduser("~"), "BirdSongs")
    try:
        recordings_bytes = sum(
            os.path.getsize(os.path.join(dp, f))
            for dp, _, filenames in os.walk(audio_path)
            for f in filenames
        ) if os.path.exists(audio_path) else 0
        recordings_gb = recordings_bytes / (1024 ** 3)
    except Exception:
        recordings_gb = 0.0

    try:
        usage = shutil.disk_usage(os.path.expanduser("~"))
        disk_total_gb = usage.total / (1024 ** 3)
        disk_used_gb = usage.used / (1024 ** 3)
        disk_percent = (usage.used / usage.total) * 100
    except Exception:
        disk_total_gb = disk_used_gb = disk_percent = 0.0

    result = {
        'disk_used_gb': disk_used_gb,
        'disk_total_gb': disk_total_gb,
        'disk_percent': disk_percent,
        'db_size_mb': db_size_mb,
        'recordings_gb': recordings_gb,
    }
    _HEALTH_CACHE['data'] = result
    _HEALTH_CACHE['expires'] = now + _HEALTH_CACHE_TTL
    return result


def _hourly_activity_section() -> Div:
    """Generate hourly activity bar chart for today."""
    hourly = get_hourly_detections()

    if not hourly:
        return Div(
            H3("Today's Activity"),
            P("No detections yet today."),
            cls="hourly-chart"
        )

    max_count = max(hourly.values())
    bar_rows = []
    for hour in range(24):
        count = hourly.get(hour, 0)
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
    """Generate system health widgets."""
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


@app.get("/app/stats")
def stats():
    """Render the stats page."""
    return _shell(_stats_content(), "/app/stats")


def _stats_content():
    """Generate the stats content."""
    total_detections = get_total_detection_count()
    total_species = get_total_species_count()

    return Div(
        H2("Statistics"),
        Div(
            Div(
                Div("Total Detections", cls="widget-label"),
                Div(f"{total_detections:,}", cls="widget-value"),
                cls="widget"
            ),
            Div(
                Div("Total Species", cls="widget-label"),
                Div(f"{total_species:,}", cls="widget-value"),
                cls="widget"
            ),
            cls="widget-grid"
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
        P("System configuration coming soon..."),
    )


if __name__ == "__main__":
    serve(port=8502)
