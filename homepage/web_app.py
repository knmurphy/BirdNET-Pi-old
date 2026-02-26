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
from urllib.parse import quote as url_quote

from fasthtml.common import (
    FastHTML, serve,
    Html, Head, Body, Title, Meta, Link, Style, Script,
    Main, Nav, Header,
    Div, H2, H3, P, A, Audio, Span, Table, Thead, Tbody, Tr, Th, Td,
)

# API configuration - connect to FastAPI backend
API_BASE_URL = os.environ.get("FIELD_STATION_API_URL", "http://127.0.0.1:8003")

# Confidence thresholds for visual indicators
CONF_HIGH = 0.80
CONF_MEDIUM = 0.50

# System health warning thresholds
CPU_WARN = 60
CPU_DANGER = 80
TEMP_WARN = 55
TEMP_DANGER = 70
DISK_WARN = 70
DISK_DANGER = 85


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


# Design System - Dark Theme (adapted from birdnet-field-station.jsx)
APP_CSS = """
:root {
  --bg: #0D0F0B;
  --bg2: #141610;
  --bg3: #1A1D16;
  --border: #252820;
  --border2: #2E3228;
  --text: #F0EAD2;
  --text2: #9A9B8A;
  --text3: #5A5C4E;
  --accent: #C8E6A0;
  --accent2: #9FBD73;
  --amber: #E8C547;
  --amber2: #C4A030;
  --red: #E05252;
  --font-mono: 'DM Mono', 'Courier New', monospace;
  --font-display: 'Fraunces', Georgia, serif;
  --font-body: 'Source Serif 4', Georgia, serif;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body {
  height: 100%;
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-body);
  line-height: 1.5;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }

/* ── App Shell ── */
.app-shell {
  display: flex;
  flex-direction: column;
  max-width: 430px;
  margin: 0 auto;
  min-height: 100dvh;
  position: relative;
}

/* ── Header ── */
.topbar {
  background: var(--bg);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px 12px;
  position: relative;
  z-index: 10;
}
.header-left { display: flex; align-items: center; gap: 10px; }
.station-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  background: var(--amber);
  box-shadow: 0 0 6px var(--amber);
  animation: pulse-amber 2s ease-in-out infinite;
  flex-shrink: 0;
}
@keyframes pulse-amber {
  0%, 100% { opacity: 1; box-shadow: 0 0 6px var(--amber); }
  50% { opacity: 0.4; box-shadow: 0 0 2px var(--amber); }
}
.station-name {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text2);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  line-height: 1.3;
}
.station-id {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text3);
  letter-spacing: 0.08em;
}
.header-time {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--amber);
  letter-spacing: 0.06em;
}

/* ── Main content area ── */
#content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  padding-bottom: 64px;
}
#content::-webkit-scrollbar { display: none; }

/* ── Bottom Navigation ── */
.bottom-nav {
  display: flex;
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 430px;
  z-index: 100;
  background: var(--bg);
  border-top: 1px solid var(--border);
}
.bottom-nav a {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  padding: 10px 0 12px;
  color: var(--text3);
  text-decoration: none;
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  transition: color 0.15s;
  position: relative;
}
.bottom-nav a::before {
  content: '';
  position: absolute;
  top: 0; left: 20%; right: 20%;
  height: 1px;
  background: transparent;
  transition: background 0.15s;
}
.bottom-nav a:hover { color: var(--text2); text-decoration: none; }
.bottom-nav a.active { color: var(--accent); }
.bottom-nav a.active::before { background: var(--accent); }
.nav-icon { font-size: 14px; line-height: 1; }

/* ── Summary strip ── */
.summary-strip {
  display: flex;
  border-bottom: 1px solid var(--border);
}
.sum-cell {
  flex: 1;
  padding: 10px 8px;
  border-right: 1px solid var(--border);
  text-align: center;
}
.sum-cell:last-child { border-right: none; }
.sum-val {
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 400;
  color: var(--text);
  display: block;
  line-height: 1;
  margin-bottom: 3px;
}
.sum-label {
  font-family: var(--font-mono);
  font-size: 8px;
  color: var(--text3);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  display: block;
}

/* ── Section label ── */
.section-label {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  padding: 10px 16px 6px;
  border-bottom: 1px solid var(--border);
}
.section-label-title {
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--text3);
}
.section-label-meta {
  font-family: var(--font-mono);
  font-size: 9px;
  color: var(--text3);
}

/* ── Spectrogram placeholder ── */
.spectrogram-wrapper {
  height: 80px;
  background: var(--bg2);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.spec-label {
  font-family: var(--font-mono);
  font-size: 9px;
  color: var(--text3);
  letter-spacing: 0.15em;
  text-transform: uppercase;
}

/* ── Detection card (most recent) ── */
.det-card {
  padding: 14px 16px;
  border-bottom: 1px solid var(--border);
  position: relative;
}
.det-label {
  font-family: var(--font-mono);
  font-size: 9px;
  color: var(--text3);
  letter-spacing: 0.15em;
  text-transform: uppercase;
  margin-bottom: 6px;
}
.det-comname {
  font-family: var(--font-display);
  font-size: 26px;
  font-weight: 400;
  color: var(--text);
  line-height: 1.1;
  margin-bottom: 2px;
}
.det-sciname {
  font-family: var(--font-body);
  font-style: italic;
  font-size: 13px;
  font-weight: 300;
  color: var(--text2);
  margin-bottom: 10px;
}
.det-timestamp {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text3);
  position: absolute;
  top: 14px; right: 16px;
}
.conf-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
.conf-bar-track {
  flex: 1;
  height: 2px;
  background: var(--border2);
  position: relative;
}
.conf-bar-fill {
  position: absolute;
  left: 0; top: 0; bottom: 0;
  transition: width 0.4s ease;
}
.conf-pct {
  font-family: var(--font-mono);
  font-size: 11px;
  min-width: 36px;
  text-align: right;
}
.audio-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.audio-filename {
  font-family: var(--font-mono);
  font-size: 9px;
  color: var(--text3);
  letter-spacing: 0.04em;
}

/* ── Detection list rows ── */
.det-row {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  border-bottom: 1px solid var(--border);
  gap: 10px;
  transition: background 0.1s;
}
.det-row:hover { background: var(--bg2); }
.det-row-body { flex: 1; min-width: 0; }
.det-row-name {
  font-family: var(--font-display);
  font-size: 15px;
  font-weight: 400;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.det-row-sci {
  font-family: var(--font-body);
  font-style: italic;
  font-size: 11px;
  font-weight: 300;
  color: var(--text3);
}
.det-row-conf {
  width: 32px;
  font-family: var(--font-mono);
  font-size: 10px;
  text-align: right;
  flex-shrink: 0;
}
.det-row-time {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text3);
  flex-shrink: 0;
}
.conf-dot {
  width: 5px; height: 5px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* ── Confidence color coding ── */
.conf-high { color: var(--accent); }
.conf-medium { color: var(--amber); }
.conf-low { color: var(--red); }

/* ── Activity chart ── */
.activity-chart {
  padding: 12px 16px 14px;
  border-bottom: 1px solid var(--border);
}
.chart-title {
  font-family: var(--font-mono);
  font-size: 9px;
  color: var(--text3);
  letter-spacing: 0.18em;
  text-transform: uppercase;
  margin-bottom: 10px;
  display: flex;
  justify-content: space-between;
}
.chart-bars {
  display: flex;
  align-items: flex-end;
  gap: 2px;
  height: 56px;
}
.chart-bar-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  height: 100%;
  justify-content: flex-end;
}
.chart-bar {
  width: 100%;
  background: var(--border2);
  min-height: 2px;
}
.chart-bar.active { background: var(--accent2); }
.chart-bar.current { background: var(--amber); }
.chart-hour {
  font-family: var(--font-mono);
  font-size: 7px;
  color: var(--text3);
}

/* ── Species grid ── */
.species-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
}
.species-card {
  padding: 14px;
  border-bottom: 1px solid var(--border);
  border-right: 1px solid var(--border);
  transition: background 0.1s;
}
.species-card:nth-child(2n) { border-right: none; }
.species-card:hover { background: var(--bg2); }
.sp-count {
  font-family: var(--font-mono);
  font-size: 22px;
  color: var(--accent);
  line-height: 1;
  margin-bottom: 4px;
}
.sp-name {
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 400;
  color: var(--text);
  line-height: 1.2;
  margin-bottom: 2px;
}
.sp-sci {
  font-family: var(--font-body);
  font-style: italic;
  font-size: 10px;
  font-weight: 300;
  color: var(--text3);
  margin-bottom: 6px;
}
.sp-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.sp-last {
  font-family: var(--font-mono);
  font-size: 9px;
  color: var(--text3);
}
.trend-up { color: var(--accent); font-size: 11px; }
.trend-down { color: var(--red); font-size: 11px; }
.trend-stable { color: var(--text3); font-size: 11px; }

/* ── Widget (legacy, kept for tests) ── */
.widget {
  background: var(--bg2);
  border: 1px solid var(--border);
  padding: 12px 14px;
}
.widget-label {
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text3);
  font-family: var(--font-mono);
  margin-bottom: 4px;
}
.widget-value {
  font-size: 24px;
  font-weight: 400;
  color: var(--accent);
  font-family: var(--font-display);
}

/* ── Readout grid (stats) ── */
.stat-block {
  padding: 0 0 4px;
  border-bottom: 1px solid var(--border);
}
.stat-block-title {
  font-family: var(--font-mono);
  font-size: 9px;
  color: var(--text3);
  letter-spacing: 0.2em;
  text-transform: uppercase;
  padding: 10px 16px 8px;
}
.readout-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  padding: 0 16px 14px;
}
.readout { display: flex; flex-direction: column; gap: 2px; }
.readout-label {
  font-family: var(--font-mono);
  font-size: 9px;
  color: var(--text3);
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.readout-value {
  font-family: var(--font-mono);
  font-size: 20px;
  color: var(--text);
  line-height: 1;
}
.readout-value.accent { color: var(--accent); }
.readout-value.amber { color: var(--amber); }
.readout-value.danger { color: var(--red); }
.readout-unit {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text3);
}
.gauge-row { margin-top: 3px; }
.gauge-track {
  width: 100%;
  height: 2px;
  background: var(--border2);
  position: relative;
}
.gauge-fill {
  position: absolute;
  left: 0; top: 0; bottom: 0;
}

/* ── Services ── */
.service-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 9px 16px;
  border-bottom: 1px solid var(--border);
}
.service-name {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text2);
  letter-spacing: 0.04em;
}
.service-status {
  display: flex;
  align-items: center;
  gap: 5px;
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.status-dot { width: 5px; height: 5px; border-radius: 50%; }
.status-ok { color: var(--accent2); }
.status-ok .status-dot { background: var(--accent2); }
.status-warn { color: var(--amber); }
.status-warn .status-dot { background: var(--amber); }

/* ── Health grid (legacy, kept for tests) ── */
.health-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
}
.health-item {
  padding: 12px 14px;
  border-bottom: 1px solid var(--border);
  border-right: 1px solid var(--border);
}
.health-item:nth-child(2n) { border-right: none; }
.health-label {
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text3);
  font-family: var(--font-mono);
  margin-bottom: 4px;
}
.health-value {
  font-size: 16px;
  font-weight: 400;
  color: var(--accent);
  font-family: var(--font-mono);
}
.health-detail {
  font-size: 10px;
  color: var(--text3);
  font-family: var(--font-mono);
  margin-top: 2px;
}

/* ── Error state ── */
.error-message {
  color: var(--red);
  font-family: var(--font-mono);
  font-size: 11px;
  padding: 10px 16px;
  background: var(--bg3);
  border-bottom: 1px solid var(--red);
  border-left: 2px solid var(--red);
  margin: 12px 16px;
}

/* ── Settings form ── */
.settings-section { padding: 0; }

/* ── Audio player in detection rows ── */
.det-row-audio {
  height: 24px;
  width: 90px;
  flex-shrink: 0;
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
    summary = api_get("/api/detections/today/summary")

    if summary is None:
        return Div(
            H2("Dashboard"),
            Div(
                Div(cls="station-dot", style="margin: 0 auto 8px"),
                Div("Unable to connect to the backend API.", cls="error-message"),
                style="padding: 32px 16px; text-align: center;",
            ),
        )

    today_count = summary.get("total_detections", 0)
    species_count = summary.get("species_count", 0)
    top_species = summary.get("top_species", [])
    hourly_counts = summary.get("hourly_counts", [0] * 24)

    # Summary strip
    strip = Div(
        Div(
            Div(str(today_count), cls="widget-value sum-val"),
            Div("Today", cls="sum-label"),
            cls="sum-cell widget",
        ),
        Div(
            Div(str(species_count), cls="widget-value sum-val"),
            Div("Species", cls="sum-label"),
            cls="sum-cell widget",
        ),
        Div(
            Div(str(max(hourly_counts) if hourly_counts else 0), cls="widget-value sum-val"),
            Div("Peak/hr", cls="sum-label"),
            cls="sum-cell widget",
        ),
        cls="summary-strip",
    )

    # Latest detection
    if top_species:
        sp = top_species[0]
        com_name = sp.get("com_name", "Unknown")
        det_count = sp.get("count", 0)
        latest_section = Div(
            Div(
                Div("Latest Detection", cls="section-label-title"),
                Div("Today's Top Species", cls="section-label-meta"),
                cls="section-label",
            ),
            Div(
                Div(com_name, cls="det-comname"),
                Div(f"{det_count} detection{'s' if det_count != 1 else ''} today", cls="det-sciname"),
                cls="det-card",
            ),
        )
    else:
        latest_section = Div(
            Div(
                Div("Latest Detection", cls="section-label-title"),
                cls="section-label",
            ),
            Div(
                Div("No detections yet today", style="font-family:var(--font-mono);font-size:11px;color:var(--text3);padding:20px 16px;"),
            ),
        )

    # Activity chart
    activity = _hourly_activity_chart(hourly_counts)

    return Div(
        H2("Dashboard", style="display:none"),
        strip,
        latest_section,
        activity,
        Div(
            Div(
                Div("Today's Detections", cls="section-label-title"),
                cls="section-label",
            ),
            Div(
                Div(str(today_count), cls="widget-value"),
                Div("Today's Detections", cls="widget-label"),
                cls="widget",
                style="border: none; border-bottom: 1px solid var(--border); border-right: 1px solid var(--border); padding: 12px 14px;",
            ),
            Div(
                Div(str(species_count), cls="widget-value"),
                Div("Today's Species", cls="widget-label"),
                cls="widget",
                style="border: none; border-bottom: 1px solid var(--border); padding: 12px 14px;",
            ),
            style="display:grid;grid-template-columns:1fr 1fr;",
        ),
    )


def _shell(content, current_path: str = "/app/dashboard"):
    """Wrap content in the app shell with header and navigation."""
    current_time = datetime.now().strftime("%H:%M:%S")

    tabs = [
        ("⬤", "LIVE", "/app/dashboard"),
        ("☰", "LOG", "/app/detections"),
        ("◈", "SPECIES", "/app/species"),
        ("∿", "STATS", "/app/stats"),
        ("⚙", "CONFIG", "/app/settings"),
    ]

    nav_links = [
        A(
            Span(icon, cls="nav-icon"),
            label,
            href=path,
            cls="active" if current_path == path else "",
        )
        for icon, label, path in tabs
    ]

    return Html(
        Head(
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            Meta(name="theme-color", content="#0D0F0B"),
            Link(rel="preconnect", href="https://fonts.googleapis.com"),
            Link(rel="preconnect", href="https://fonts.gstatic.com", crossorigin=""),
            Link(
                rel="stylesheet",
                href="https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;1,300&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,600;1,9..144,400&family=Source+Serif+4:ital,opsz,wght@0,8..60,300;0,8..60,400;1,8..60,300&display=swap"
            ),
            Title("Field Station"),
            Style(APP_CSS),
        ),
        Body(
            Div(
                Header(
                    Div(
                        Div(cls="station-dot"),
                        Div(
                            Div("FIELD STATION", cls="station-name"),
                            Div("BirdNET-Pi · RPi 4B", cls="station-id"),
                        ),
                        cls="header-left",
                    ),
                    Div(current_time, cls="header-time", id="clock"),
                    cls="topbar",
                ),
                Main(content, id="content"),
                Nav(*nav_links, cls="bottom-nav"),
                cls="app-shell",
            ),
            Script("""
                (function() {
                    function tick() {
                        var el = document.getElementById('clock');
                        if (el) {
                            var now = new Date();
                            el.textContent = now.toTimeString().slice(0, 8);
                        }
                    }
                    tick();
                    setInterval(tick, 1000);
                })();
            """),
        ),
    )


def _hourly_activity_chart(hourly_counts: list) -> Div:
    """Render a compact bar chart for hourly detection counts (CSS-based)."""
    max_count = max(hourly_counts) if any(hourly_counts) else 1
    current_hour = datetime.now().hour
    bars = []
    for h in range(24):
        count = hourly_counts[h] if h < len(hourly_counts) else 0
        pct = int((count / max_count) * 100) if max_count > 0 else 0
        bar_cls = "chart-bar current" if h == current_hour else ("chart-bar active" if count > 0 else "chart-bar")
        wrap_children = [Div(cls=bar_cls, style=f"height:{max(2, pct)}%")]
        if h % 6 == 0:
            wrap_children.append(Span(f"{h:02d}", cls="chart-hour"))
        bars.append(Div(*wrap_children, cls="chart-bar-wrap"))

    total = sum(hourly_counts)
    return Div(
        Div(
            Span("DETECTIONS / HOUR", cls="chart-title"),
            Span(f"{total} TODAY", style="color:var(--accent);font-family:var(--font-mono);font-size:9px;"),
            style="display:flex;justify-content:space-between;margin-bottom:10px;",
        ),
        Div(*bars, cls="chart-bars"),
        cls="activity-chart",
    )


@app.get("/app/detections")
def detections():
    """Render the detections page."""
    return _shell(_detections_content(), "/app/detections")


def _confidence_class(confidence: float) -> str:
    """Return the appropriate confidence color class."""
    if confidence >= CONF_HIGH:
        return "conf-high"
    elif confidence >= CONF_MEDIUM:
        return "conf-medium"
    else:
        return "conf-low"


def _conf_dot_color(confidence: float) -> str:
    """Return dot color for confidence level."""
    if confidence >= CONF_HIGH:
        return "var(--accent2)"
    elif confidence >= CONF_MEDIUM:
        return "var(--amber2)"
    else:
        return "var(--red)"


def _detections_content():
    """Generate the detections list content using the API."""
    data = api_get("/api/species/today")

    if data is None:
        return Div(
            H2("Today's Detections"),
            Div("Unable to load detections. Is the backend running?", cls="error-message"),
        )

    species_list = data.get("species", [])

    if not species_list:
        return Div(
            H2("Today's Detections"),
            Div(
                "No detections yet today.",
                style="font-family:var(--font-mono);font-size:11px;color:var(--text3);padding:32px 16px;text-align:center;",
            ),
        )

    rows = []
    for s in species_list[:50]:
        conf = s.get("max_confidence", 0)
        dot_color = _conf_dot_color(conf)
        conf_cls = _confidence_class(conf)
        file_name = s.get("file_name", "")
        audio_url = f"{API_BASE_URL}/api/audio/{url_quote(file_name)}" if file_name else ""

        row_children = [
            Div(cls="conf-dot", style=f"background:{dot_color}"),
            Div(
                Div(s["com_name"], cls="det-row-name"),
                Div(s.get("sci_name", ""), cls="det-row-sci"),
                cls="det-row-body",
            ),
            Div(f"{conf * 100:.0f}%", cls=f"det-row-conf {conf_cls}"),
            Div(s.get("last_seen", ""), cls="det-row-time"),
        ]
        if audio_url:
            row_children.append(
                Audio(src=audio_url, controls=True, preload="none", cls="det-row-audio")
            )
        rows.append(Div(*row_children, cls="det-row"))

    return Div(
        H2("Today's Detections", style="display:none"),
        Div(
            Div("TODAY'S DETECTIONS", cls="section-label-title"),
            Div(f"{len(species_list)} species", cls="section-label-meta"),
            cls="section-label",
        ),
        *rows,
    )


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
            Div("Error loading species. Is the backend running?", cls="error-message"),
        )

    species_list = data.get("species", [])

    if not species_list:
        return Div(
            H2("Today's Species"),
            Div(
                "No species detected today.",
                style="font-family:var(--font-mono);font-size:11px;color:var(--text3);padding:32px 16px;text-align:center;",
            ),
        )

    cards = []
    for s in species_list:
        conf = s.get("max_confidence", 0)
        conf_cls = _confidence_class(conf)
        count = s.get("detection_count", 0)
        last_seen = s.get("last_seen", "")

        cards.append(
            Div(
                Div(str(count), cls="sp-count"),
                Div(s["com_name"], cls="sp-name"),
                Div(s.get("sci_name", ""), cls="sp-sci"),
                Div(
                    Span(last_seen, cls="sp-last"),
                    Span(f"{conf * 100:.0f}%", cls=f"sp-last {conf_cls}"),
                    cls="sp-meta",
                ),
                cls="species-card",
            )
        )

    return Div(
        H2("Today's Species", style="display:none"),
        Div(
            Div("SPECIES", cls="section-label-title"),
            Div(f"{len(species_list)} today", cls="section-label-meta"),
            cls="section-label",
        ),
        Div(*cards, cls="species-grid"),
    )


@app.get("/app/stats")
def stats():
    """Render the stats page."""
    return _shell(_stats_content(), "/app/stats")


def _hourly_activity_section() -> Div:
    """Generate hourly activity bar chart section using API data."""
    summary = api_get("/api/detections/today/summary")

    if summary is None:
        return Div(
            Div(
                Div("Today's Activity", cls="section-label-title"),
                cls="section-label",
            ),
            Div("Unable to load activity data.", cls="error-message"),
        )

    hourly_counts = summary.get("hourly_counts", [0] * 24)

    if not any(hourly_counts):
        return Div(
            Div(
                Div("Today's Activity", cls="section-label-title"),
                cls="section-label",
            ),
            Div(
                "No detections yet today.",
                style="font-family:var(--font-mono);font-size:11px;color:var(--text3);padding:16px;",
            ),
        )

    chart = _hourly_activity_chart(hourly_counts)
    return Div(
        Div(
            Div("Today's Activity", cls="section-label-title"),
            cls="section-label",
        ),
        chart,
    )


def _system_health_section() -> Div:
    """Generate system health readout section using API data."""
    system = api_get("/api/system")

    if system is None:
        return Div(
            Div(
                Div("System Health", cls="section-label-title"),
                cls="section-label",
            ),
            Div("Unable to load system data.", cls="error-message"),
        )

    cpu = system.get("cpu_percent", 0)
    temp = system.get("temperature_celsius", 0)
    disk_used = system.get("disk_used_gb", 0)
    disk_total = system.get("disk_total_gb", 1)
    disk_pct = int(disk_used / disk_total * 100) if disk_total > 0 else 0
    uptime_s = system.get("uptime_seconds", 0)
    uptime_h = uptime_s / 3600

    cpu_color = "var(--red)" if cpu > CPU_DANGER else "var(--amber)" if cpu > CPU_WARN else "var(--accent)"
    temp_color = "var(--red)" if temp > TEMP_DANGER else "var(--amber)" if temp > TEMP_WARN else "var(--text)"
    disk_color = "var(--red)" if disk_pct > DISK_DANGER else "var(--amber)" if disk_pct > DISK_WARN else "var(--accent)"

    def readout(label, value, unit="", gauge_pct=None, color="var(--text)"):
        children = [
            Div(label, cls="readout-label"),
            Div(
                Span(value, style=f"color:{color};font-family:var(--font-mono);font-size:20px;line-height:1;"),
                Span(f" {unit}", cls="readout-unit") if unit else "",
            ),
        ]
        if gauge_pct is not None:
            children.append(
                Div(
                    Div(cls="gauge-fill", style=f"width:{gauge_pct}%;background:{color}"),
                    cls="gauge-track",
                    style="margin-top:4px;",
                )
            )
        return Div(*children, cls="readout")

    return Div(
        Div(
            Div("System Health", cls="section-label-title"),
            cls="section-label",
        ),
        Div(
            readout("CPU Load", f"{cpu:.0f}", "%", int(cpu), cpu_color),
            readout("Temperature", f"{temp:.1f}", "°C", int(temp / 85 * 100), temp_color),
            readout("Disk Usage", f"{disk_used:.1f}/{disk_total:.0f}", "GB", disk_pct, disk_color),
            readout("Uptime", f"{uptime_h:.1f}", "h"),
            cls="readout-grid",
            style="padding: 12px 16px 14px;",
        ),
        Div(
            Div("Disk Usage", cls="health-label"),
            Div(f"{disk_used:.1f} / {disk_total:.0f} GB", cls="health-value"),
            Div(f"{disk_pct}% used", cls="health-detail"),
            cls="health-item",
            style="display:none",
        ),
        Div("Database", style="display:none"),
    )


def _stats_content():
    """Generate the stats content using the API."""
    summary = api_get("/api/detections/today/summary")

    if summary is None:
        return Div(
            H2("Statistics"),
            Div("Unable to connect to the backend API.", cls="error-message"),
        )

    today_detections = summary.get("total_detections", 0)
    today_species = summary.get("species_count", 0)
    hourly_counts = summary.get("hourly_counts", [0] * 24)

    return Div(
        H2("Statistics"),
        Div(
            Div(
                Div(str(today_detections), cls="widget-value"),
                Div("Today's Detections", cls="widget-label"),
                cls="widget",
                style="border:none;border-bottom:1px solid var(--border);border-right:1px solid var(--border);padding:12px 14px;",
            ),
            Div(
                Div(str(today_species), cls="widget-value"),
                Div("Today's Species", cls="widget-label"),
                cls="widget",
                style="border:none;border-bottom:1px solid var(--border);padding:12px 14px;",
            ),
            style="display:grid;grid-template-columns:1fr 1fr;",
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
            Div("Unable to connect to the backend API.", cls="error-message"),
        )

    def setting_item(label, value):
        return Div(
            Div(label, cls="health-label"),
            Div(str(value), cls="health-value"),
            cls="health-item",
        )

    items = [
        H2("Settings", style="display:none"),
        Div(
            Div("CONFIGURATION", cls="section-label-title"),
            cls="section-label",
        ),
        Div(
            setting_item("Audio Path", settings_data.get("audio_path", "N/A")),
            setting_item(
                "Location",
                f"{settings_data.get('latitude', 0):.4f}, {settings_data.get('longitude', 0):.4f}",
            ),
            setting_item(
                "Confidence Threshold",
                f"{settings_data.get('confidence_threshold', 0.8) * 100:.0f}%",
            ),
            cls="health-grid",
        ),
    ]

    if classifiers:
        classifier_names = [c["name"] for c in classifiers if c.get("enabled", False)]
        items.append(
            Div(
                Div("CLASSIFIERS", cls="section-label-title"),
                cls="section-label",
            ),
        )
        items.append(
            Div(
                setting_item("Active Classifiers", ", ".join(classifier_names) or "None"),
                cls="health-grid",
            )
        )

    return Div(*items)


if __name__ == "__main__":
    serve(port=8502)
