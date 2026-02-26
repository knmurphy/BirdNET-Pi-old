"""
Field Station OS - FastHTML Web Application

A Python-native web UI for passive acoustic monitoring.
Built with FastHTML for HTMX-based navigation (no iframe, no full page reload).

This version uses the FastAPI backend for data instead of direct database queries.
"""
import os
import logging
import httpx
from datetime import datetime

from fasthtml.common import (
    FastHTML, serve,
    Html, Head, Body, Title, Meta, Link, Style,
    Main, Nav, Header,
    Div, H2, H3, P, A, Audio,
)

# API configuration - connect to FastAPI backend
API_BASE_URL = os.environ.get("FIELD_STATION_API_URL", "http://127.0.0.1:8003")


def api_get(endpoint: str) -> dict | None:
    """Make a GET request to the FastAPI backend."""
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{API_BASE_URL}{endpoint}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logging.error(f"API request failed for {endpoint}: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error calling API {endpoint}: {e}")
        return None


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


@app.get("/app/dashboard")
def dashboard():
    """Render the dashboard page."""
    return _shell(_dashboard_content(), "/app/dashboard")


def _dashboard_content():
    """Generate the dashboard content using the API."""
    # Fetch today's summary from API
    summary = api_get("/api/detections/today/summary")
    
    if summary is None:
        return Div(
            H2("Dashboard"),
            P("Unable to connect to API. Is the backend running?", cls="error-message"),
        )
    
    today_count = summary.get("total_detections", 0)
    species_count = summary.get("species_count", 0)
    top_species = summary.get("top_species", [])
    
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
    
    # Show top species if available
    if top_species:
        top_names = ", ".join([s["com_name"] for s in top_species[:3]])
        widgets.append(
            Div(
                Div("Top Species", cls="widget-label"),
                Div(top_names, cls="widget-value", style="font-size: 14px;"),
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
    """Generate the detections list content using the API."""
    # Fetch species data from API
    data = api_get("/api/species/today")
    
    if data is None:
        return Div(
            H2("Today's Detections"),
            P("Unable to connect to API.", cls="error-message"),
        )
    
    species_list = data.get("species", [])
    
    if not species_list:
        return Div(H2("Today's Detections"), P("No detections yet today."))
    
    # Show species with counts (API doesn't return individual detections yet)
    items = [
        Div(
            f"{s['com_name']} - {s['detection_count']} detections (max: {s['max_confidence']*100:.0f}%)",
            cls=_confidence_class(s['max_confidence'])
        )
        for s in species_list[:50]  # Limit to 50
    ]
    return Div(H2("Today's Detections (by species)"), *items)


@app.get("/app/species")
def species():
    """Render the species page."""
    return _shell(_species_content(), "/app/species")


def _species_content():
    """Generate the species list content using the API."""
    data = api_get("/api/species/today")
    
    if data is None:
        return Div(
            H2("Today's Species"),
            P("Unable to connect to API.", cls="error-message"),
        )
    
    species_list = data.get("species", [])
    
    if not species_list:
        return Div(H2("Today's Species"), P("No species detected today."))
    
    items = [
        Div(
            f"{s['com_name']} ({s['sci_name']}) - {s['detection_count']} detections (max: {s['max_confidence']*100:.0f}%)",
            cls=_confidence_class(s['max_confidence'])
        )
        for s in species_list
    ]
    return Div(H2("Today's Species"), *items)


@app.get("/app/stats")
def stats():
    """Render the stats page."""
    return _shell(_stats_content(), "/app/stats")


def _hourly_activity_section() -> Div:
    """Generate hourly activity bar chart for today using API data."""
    summary = api_get("/api/detections/today/summary")
    
    if summary is None:
        return Div(
            H3("Today's Activity"),
            P("Unable to load activity data.", cls="text2"),
            cls="hourly-chart"
        )
    
    hourly_counts = summary.get("hourly_counts", [0] * 24)
    
    if not any(hourly_counts):
        return Div(
            H3("Today's Activity"),
            P("No detections yet today.", cls="text2"),
            cls="hourly-chart"
        )
    
    max_count = max(hourly_counts) if hourly_counts else 1
    
    bar_rows = []
    for hour in range(24):
        count = hourly_counts[hour] if hour < len(hourly_counts) else 0
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
        Div(*bar_rows, cls="hourly-chart"),
    )


def _system_health_section() -> Div:
    """Generate system health widgets using API data."""
    system = api_get("/api/system")
    
    if system is None:
        return Div(
            H3("System Health"),
            P("Unable to load system data.", cls="error-message"),
        )
    
    return Div(
        H3("System Health"),
        Div(
            Div(
                Div("CPU", cls="health-label"),
                Div(f"{system['cpu_percent']:.1f}%", cls="health-value"),
                cls="health-item"
            ),
            Div(
                Div("Temperature", cls="health-label"),
                Div(f"{system['temperature_celsius']:.1f}°C", cls="health-value"),
                cls="health-item"
            ),
            Div(
                Div("Disk Usage", cls="health-label"),
                Div(f"{system['disk_used_gb']:.1f} / {system['disk_total_gb']:.0f} GB", cls="health-value"),
                Div(f"{(system['disk_used_gb']/system['disk_total_gb']*100):.1f}% used", cls="health-detail"),
                cls="health-item"
            ),
            Div(
                Div("Uptime", cls="health-label"),
                Div(f"{system['uptime_seconds']/3600:.1f}h", cls="health-value"),
                cls="health-item"
            ),
            Div(
                Div("SSE Subscribers", cls="health-label"),
                Div(str(system['sse_subscribers']), cls="health-value"),
                cls="health-item"
            ),
            cls="health-grid"
        ),
    )


def _stats_content():
    """Generate the stats content using the API."""
    summary = api_get("/api/detections/today/summary")
    
    if summary is None:
        return Div(
            H2("Statistics"),
            P("Unable to connect to API.", cls="error-message"),
        )
    
    today_detections = summary.get("total_detections", 0)
    today_species = summary.get("species_count", 0)

    return Div(
        H2("Statistics"),
        Div(
            Div("Today's Detections", cls="widget-label"),
            Div(f"{today_detections:,}", cls="widget-value"),
            cls="widget"
        ),
        Div(
            Div("Today's Species", cls="widget-label"),
            Div(f"{today_species:,}", cls="widget-value"),
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
    """Generate the settings content using the API."""
    settings_data = api_get("/api/settings")
    classifiers = api_get("/api/classifiers")
    
    if settings_data is None:
        return Div(
            H2("Settings"),
            P("Unable to connect to API.", cls="error-message"),
        )
    
    items = [
        H2("Settings"),
        Div(
            Div("Audio Path", cls="health-label"),
            Div(settings_data.get("audio_path", "N/A"), cls="health-value"),
            cls="health-item"
        ),
        Div(
            Div("Location", cls="health-label"),
            Div(f"{settings_data.get('latitude', 0):.4f}, {settings_data.get('longitude', 0):.4f}", cls="health-value"),
            cls="health-item"
        ),
        Div(
            Div("Confidence Threshold", cls="health-label"),
            Div(f"{settings_data.get('confidence_threshold', 0.8)*100:.0f}%", cls="health-value"),
            cls="health-item"
        ),
    ]
    
    if classifiers:
        classifier_names = [c["name"] for c in classifiers if c.get("enabled", False)]
        items.append(
            Div(
                Div("Active Classifiers", cls="health-label"),
                Div(", ".join(classifier_names) or "None", cls="health-value"),
                cls="health-item"
            )
        )
    
    return Div(*items, cls="health-grid")


if __name__ == "__main__":
    serve(port=8502)
