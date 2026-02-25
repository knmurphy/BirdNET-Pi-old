"""
BirdNET-Pi FastHTML web application
====================================
A Python-native replacement for the PHP/iframe web interface.

Architecture
------------
FastHTML (https://fastht.ml) generates HTML fragments using Python functions.
Every navigation action is an HTMX partial-page swap — no iframe, no full
page reload.  The outer shell (html/head/body) is sent once; only the
<main id="content"> div is replaced on each click.

Why FastHTML?
- Python throughout: aligns with the existing Python backend (server.py,
  notifications.py, plotly_streamlit.py) and Nachtzuster's stated goal of
  moving from PHP to Python (Flask/FastHTML).
- HTMX built-in: eliminates the iframe architecture that causes the known
  scroll bug and slow navigation without requiring a JavaScript build toolchain.
- Single file: can run alongside the PHP app initially; replace it view-by-view.
- Same SQLite DB: reads ~/BirdNET-Pi/scripts/birds.db directly.

Running
-------
  pip install python-fasthtml
  python3 homepage/web_app.py         # listens on :8502

The existing Caddy config then needs one extra line:
  reverse_proxy /app* localhost:8502
(see docs/ui-improvement-proposal.md for the full migration plan)

During migration the PHP app continues to run unchanged at the root path.
"""

import os
import re
import sqlite3
from datetime import date, datetime
from pathlib import Path

try:
    from fasthtml.common import (
        FastHTML, serve,
        Html, Head, Body, Title, Meta, Link, Script, Style,
        Main, Nav, Header, Footer,
        Div, Span, H1, H2, H3, P, A, Img, Audio, Video, Source,
        Table, Thead, Tbody, Tr, Th, Td,
        Form, Input, Button, Label, Select, Option,
        Ul, Li,
        NotStr,
    )
    FASTHTML_AVAILABLE = True
except ImportError:
    FASTHTML_AVAILABLE = False
    # Stub types so function signatures that reference FastHTML types don't
    # raise NameError when the module is parsed without the library installed.
    class _Stub:
        pass
    (Html, Head, Body, Title, Meta, Link, Script, Style,
     Main, Nav, Header, Footer,
     Div, Span, H1, H2, H3, P, A, Img, Audio, Video, Source,
     Table, Thead, Tbody, Tr, Th, Td,
     Form, Input, Button, Label, Select, Option,
     Ul, Li, NotStr,
     FastHTML, serve) = (_Stub,) * 40

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

USER_DIR = os.path.expanduser("~")
DB_PATH = os.path.join(USER_DIR, "BirdNET-Pi", "scripts", "birds.db")
CONFIG_PATH_CANDIDATES = [
    os.path.join(USER_DIR, "BirdNET-Pi", "scripts", "thisrun.txt"),
    os.path.join(USER_DIR, "BirdNET-Pi", "scripts", "firstrun.ini"),
]
PORT = 8502


def _load_config() -> dict:
    """Load BirdNET-Pi configuration from the first available config file."""
    for path in CONFIG_PATH_CANDIDATES:
        if os.path.exists(path):
            cfg = {}
            with open(path) as fh:
                for line in fh:
                    line = line.strip()
                    if "=" in line and not line.startswith("#"):
                        k, _, v = line.partition("=")
                        cfg[k.strip()] = v.strip().strip('"').strip("'")
            return cfg
    return {}


CONFIG = _load_config()
SITE_NAME = CONFIG.get("SITE_NAME") or "BirdNET-Pi"
try:
    RECORDING_LENGTH = max(1, int(CONFIG.get("RECORDING_LENGTH") or 15))
except (ValueError, TypeError):
    RECORDING_LENGTH = 15


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def _db() -> sqlite3.Connection:
    """Return a read-only SQLite connection (WAL-compatible)."""
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True,
                          check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


def _query(sql: str, params: tuple = ()) -> list:
    try:
        con = _db()
        with con:
            return con.execute(sql, params).fetchall()
    except Exception:
        return []


def _query_one(sql: str, params: tuple = ()):
    rows = _query(sql, params)
    return rows[0] if rows else None


def _scalar(sql: str, params: tuple = (), default=0):
    row = _query_one(sql, params)
    return row[0] if row else default


def _slug(com_name: str) -> str:
    """Consistent URL-safe slug for a species common name used in all views."""
    return com_name.replace(" ", "_").replace("'", "")


def _safe_basename(filename: str) -> str:
    """Return os.path.basename of a DB filename; return '' if it looks like a path traversal."""
    base = os.path.basename(filename or "")
    if ".." in base or "/" in base or "\\" in base:
        return ""
    return base


# ---------------------------------------------------------------------------
# Shared CSS  (mirrors style.css palette; kept inline so the app is self-contained)
# ---------------------------------------------------------------------------

APP_CSS = """
:root {
  --green-light: rgb(219,255,235);
  --green-mid:   rgb(159,226,155);
  --green-dark:  rgb(119,196,135);
  --green-accent:#04AA6D;
  --text: #222;
  font-family: system-ui, 'Roboto Flex', sans-serif;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--green-dark); color: var(--text); }

/* ── Shell ─────────────────────────────────────────────────────────── */
.app-shell { display: flex; flex-direction: column; min-height: 100dvh; }

/* ── Top bar ──────────────────────────────────────────────────────── */
.topbar {
  background: var(--green-mid);
  display: flex; align-items: center; gap: 8px;
  padding: 8px 16px;
  box-shadow: 0 2px 6px rgba(0,0,0,.12);
}
.topbar .site-name { font-size: 1.1rem; font-weight: bold; margin-right: auto; }
.topbar a { text-decoration: none; color: var(--text); }

/* ── Desktop side-nav ─────────────────────────────────────────────── */
.layout { display: flex; flex: 1; overflow: hidden; }
.sidenav {
  width: 168px; flex-shrink: 0;
  background: var(--green-light);
  display: flex; flex-direction: column; gap: 2px;
  padding: 12px 8px;
  overflow-y: auto;
}
.sidenav a {
  display: block; padding: 9px 12px; border-radius: 6px;
  font-weight: 500; color: var(--text); text-decoration: none;
  transition: background .15s;
}
.sidenav a:hover, .sidenav a.active { background: var(--green-mid); }

/* ── Main content ────────────────────────────────────────────────── */
#content {
  flex: 1; overflow-y: auto;
  background: var(--green-dark);
  padding: 16px;
}

/* ── Bottom nav (mobile) ─────────────────────────────────────────── */
.bottom-nav {
  display: none;
  position: fixed; bottom: 0; left: 0; right: 0; z-index: 100;
  background: var(--green-light);
  box-shadow: 0 -2px 6px rgba(0,0,0,.12);
  justify-content: space-around;
}
.bottom-nav a {
  display: flex; flex-direction: column; align-items: center;
  padding: 8px 4px 10px;
  font-size: .7rem; color: var(--text); text-decoration: none;
  flex: 1;
}
.bottom-nav a .icon { font-size: 1.4rem; }
.bottom-nav a.active { color: var(--green-accent); font-weight: bold; }

/* ── Widget grid ─────────────────────────────────────────────────── */
.widget-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(148px, 1fr));
  gap: 12px; margin-bottom: 16px;
}
.widget {
  background: var(--green-light); border-radius: 8px;
  padding: 14px 12px; text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,.09);
  transition: box-shadow .2s;
}
.widget:hover { box-shadow: 0 4px 14px rgba(0,0,0,.14); }
.widget-label {
  font-size: .65rem; text-transform: uppercase; letter-spacing: .6px;
  color: #555; font-weight: bold; margin-bottom: 8px;
}
.widget-value {
  font-size: 2rem; font-weight: bold; color: #2a7a3a; line-height: 1.1;
}
.widget-wide { grid-column: 1 / -1; }
.widget-chart { grid-column: span 2; min-width: 0; }
.widget-meta { font-size: .8rem; color: #666; margin-top: 4px; }
.widget-link {
  font-size: 2rem; font-weight: bold; color: var(--green-accent);
  text-decoration: underline; text-decoration-color: rgba(4,170,109,.35);
  cursor: pointer; background: none; border: none;
}

/* ── Detection table ─────────────────────────────────────────────── */
.det-table { width: 100%; border-collapse: collapse; background: var(--green-light); border-radius: 8px; overflow: hidden; }
.det-table th { background: var(--green-mid); padding: 10px 12px; text-align: left; font-size: .8rem; text-transform: uppercase; }
.det-table td { padding: 10px 12px; border-top: 1px solid var(--green-mid); vertical-align: middle; }
.det-table tr:hover td { background: rgba(159,226,155,.35); }
.conf-badge {
  display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: .8rem; font-weight: bold;
  background: var(--green-mid);
}

/* ── Loading indicator ──────────────────────────────────────────── */
.htmx-indicator { display: none; }
.htmx-request .htmx-indicator { display: inline; }

/* ── Responsive ─────────────────────────────────────────────────── */
@media (max-width: 640px) {
  .sidenav { display: none; }
  .bottom-nav { display: flex; }
  #content { padding-bottom: 72px; }
  .widget-grid { grid-template-columns: 1fr 1fr; }
  .widget-chart { grid-column: 1 / -1; }
  .widget-value, .widget-link { font-size: 1.5rem; }
}
"""

# ---------------------------------------------------------------------------
# HTMX helper: navigation link that swaps #content
# ---------------------------------------------------------------------------

def _nav_link(label: str, path: str, icon: str = "", active_path: str = "") -> A:
    is_active = active_path == path
    return A(
        icon + " " + label if icon else label,
        href=path,
        hx_get=path,
        hx_target="#content",
        hx_push_url="true",
        cls="active" if is_active else "",
    )


# ---------------------------------------------------------------------------
# Page shell (sent once; HTMX swaps #content on navigation)
# ---------------------------------------------------------------------------

def _shell(initial_content, current_path: str = "/app/dashboard"):
    nav_items = [
        ("🏠", "Dashboard",   "/app/dashboard"),
        ("📋", "Detections",  "/app/detections"),
        ("🎵", "Recordings",  "/app/recordings"),
        ("📊", "Charts",      "/app/charts"),
    ]

    sidenav_links = [_nav_link(label, path, icon, current_path) for icon, label, path in nav_items]
    bottom_links = [
        A(Span(icon, cls="icon"), label,
          href=path,
          hx_get=path, hx_target="#content", hx_push_url="true",
          cls="active" if current_path == path else "")
        for icon, label, path in nav_items
    ]

    return Html(
        Head(
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            Title(SITE_NAME),
            Style(APP_CSS),
            # HTMX — served from local static directory.
            # The install script downloads it with:
            #   curl -sL https://unpkg.com/htmx.org@2.0.0/dist/htmx.min.js \
            #        -o $HOME/BirdNET-Pi/homepage/static/htmx.min.js
            Script(src="/static/htmx.min.js"),
        ),
        Body(
            Div(
                # ── Top bar ──────────────────────────────────────────
                Header(
                    Div(SITE_NAME, cls="site-name"),
                    cls="topbar",
                ),
                # ── Body ─────────────────────────────────────────────
                Div(
                    Nav(*sidenav_links, cls="sidenav"),
                    Main(initial_content, id="content"),
                    cls="layout",
                ),
                # ── Mobile bottom nav ────────────────────────────────
                Nav(*bottom_links, cls="bottom-nav"),
                cls="app-shell",
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Dashboard view
# ---------------------------------------------------------------------------

def _dashboard_content():
    today = date.today().isoformat()

    total       = _scalar("SELECT COUNT(*) FROM detections")
    today_count = _scalar("SELECT COUNT(*) FROM detections WHERE Date = ?", (today,))
    hour_count  = _scalar(
        "SELECT COUNT(*) FROM detections WHERE Date = ? AND Time >= TIME('now','localtime','-1 hour')",
        (today,))
    species_today = _scalar(
        "SELECT COUNT(DISTINCT Com_Name) FROM detections WHERE Date = ?", (today,))
    species_total = _scalar("SELECT COUNT(DISTINCT Com_Name) FROM detections")

    latest = _query_one(
        "SELECT Com_Name, Sci_Name, Confidence, Date, Time FROM detections ORDER BY Date DESC, Time DESC LIMIT 1")

    chart_file = f"Combo-{today}.png"
    chart_src = f"/Charts/{chart_file}"

    return Div(
        H2("Dashboard", style="margin-bottom:16px"),

        # ── KPI widgets ──────────────────────────────────────────────
        Div(
            Div(Div("All-Time Detections", cls="widget-label"),
                Div(f"{total:,}", cls="widget-value"),
                cls="widget"),
            Div(Div("Today's Detections", cls="widget-label"),
                Div(
                    A(f"{today_count:,}", href="/app/detections",
                      hx_get="/app/detections", hx_target="#content", hx_push_url="true",
                      cls="widget-link"),
                    cls="widget-value"),
                cls="widget"),
            Div(Div("Last Hour", cls="widget-label"),
                Div(f"{hour_count:,}", cls="widget-value"),
                cls="widget"),
            Div(Div("Species Today", cls="widget-label"),
                Div(f"{species_today:,}", cls="widget-value"),
                cls="widget"),
            Div(Div("Total Species", cls="widget-label"),
                Div(
                    A(f"{species_total:,}", href="/app/recordings",
                      hx_get="/app/recordings", hx_target="#content", hx_push_url="true",
                      cls="widget-link"),
                    cls="widget-value"),
                cls="widget"),
            cls="widget-grid",
        ),

        # ── Latest detection widget ───────────────────────────────────
        Div(
            Div("Latest Detection", cls="widget-label"),
            Div(
                A(latest["Com_Name"],
                  href=f"/app/species/{_slug(latest['Com_Name'])}",
                  hx_get=f"/app/species/{_slug(latest['Com_Name'])}",
                  hx_target="#content", hx_push_url="true",
                  cls="widget-link",
                  style="font-size:1.4rem") if latest else "No detections yet.",
                P(f"{latest['Date']} {latest['Time']} · {round(float(latest['Confidence'])*100)}% confidence",
                  cls="widget-meta") if latest else "",
            ),
            cls="widget widget-wide",
        ) if latest is not None else Div(),

        # ── Chart + spectrogram ────────────────────────────────────────
        Div(
            Div(
                Div("Today's Chart", cls="widget-label"),
                Img(src=chart_src, style="width:100%;border-radius:4px",
                    onerror="this.style.display='none';this.nextSibling.style.display='block'"),
                P("Chart not yet available for today.", style="display:none;color:#777;font-style:italic"),
                cls="widget widget-chart",
            ),
            Div(
                Div("Live Spectrogram", cls="widget-label"),
                Img(id="dash-spectrogram", src="/spectrogram.png",
                    style="width:100%;border-radius:4px"),
                cls="widget widget-chart",
            ),
            cls="widget-grid",
        ),

        # ── Auto-refresh spectrogram ────────────────────────────────────
        Script(f"""
          setInterval(function(){{
            var img = document.getElementById('dash-spectrogram');
            if(img) img.src = '/spectrogram.png?t=' + Date.now();
          }}, {RECORDING_LENGTH} * 1000);
        """),
    )


# ---------------------------------------------------------------------------
# Today's Detections view
# ---------------------------------------------------------------------------

def _detections_content(limit: int = 50, offset: int = 0):
    today = date.today().isoformat()
    rows = _query(
        "SELECT Time, Com_Name, Sci_Name, Confidence, File_Name "
        "FROM detections WHERE Date = ? ORDER BY Time DESC LIMIT ? OFFSET ?",
        (today, limit, offset))

    if not rows:
        return Div(H2("Today's Detections", style="margin-bottom:16px"),
                   P("No detections yet today.", style="color:#555"))

    table_rows = []
    for r in rows:
        conf_pct = round(float(r["Confidence"]) * 100)
        com_name_slug = _slug(r["Com_Name"])
        safe_file = _safe_basename(r["File_Name"])
        if not safe_file:
            continue
        filename = f"/By_Date/{today}/{com_name_slug}/{safe_file}"
        table_rows.append(Tr(
            Td(r["Time"]),
            Td(A(r["Com_Name"],
                 href=f"/app/species/{com_name_slug}",
                 hx_get=f"/app/species/{com_name_slug}",
                 hx_target="#content", hx_push_url="true")),
            Td(Span(r["Sci_Name"], style="font-style:italic")),
            Td(Span(f"{conf_pct}%", cls="conf-badge")),
            Td(Audio(Source(src=filename, type="audio/mpeg"),
                     controls=True, preload="none",
                     style="max-width:200px")),
        ))

    return Div(
        H2("Today's Detections", style="margin-bottom:16px"),
        Table(
            Thead(Tr(Th("Time"), Th("Species"), Th("Scientific Name"),
                     Th("Confidence"), Th("Audio"))),
            Tbody(*table_rows),
            cls="det-table",
        ),
    )


# ---------------------------------------------------------------------------
# Recordings / species list view
# ---------------------------------------------------------------------------

def _recordings_content():
    rows = _query(
        "SELECT Com_Name, COUNT(*) as cnt, MAX(Confidence) as maxconf, "
        "MAX(Date) as lastdate FROM detections GROUP BY Com_Name ORDER BY cnt DESC"
    )
    if not rows:
        return Div(H2("Species Recordings"), P("No data yet."))

    table_rows = [
        Tr(
            Td(A(r["Com_Name"],
                 href=f"/app/species/{_slug(r['Com_Name'])}",
                 hx_get=f"/app/species/{_slug(r['Com_Name'])}",
                 hx_target="#content", hx_push_url="true")),
            Td(f"{r['cnt']:,}"),
            Td(f"{round(float(r['maxconf'])*100)}%"),
            Td(r["lastdate"]),
        )
        for r in rows
    ]

    return Div(
        H2("Species Recordings", style="margin-bottom:16px"),
        Table(
            Thead(Tr(Th("Species"), Th("Detections"), Th("Best Confidence"), Th("Last Seen"))),
            Tbody(*table_rows),
            cls="det-table",
        ),
    )


# ---------------------------------------------------------------------------
# Charts view (embeds existing Streamlit app in-page)
# ---------------------------------------------------------------------------

def _charts_content():
    return Div(
        H2("Species Charts", style="margin-bottom:16px"),
        P("Powered by the existing Streamlit chart service."),
        Div(
            NotStr('<iframe src="/stats" style="width:100%;height:80vh;border:none;border-radius:8px"></iframe>'),
        ),
    )


# ---------------------------------------------------------------------------
# Species detail view
# ---------------------------------------------------------------------------

def _species_content(slug: str):
    com_name = slug.replace("_", " ")
    row = _query_one(
        "SELECT Com_Name, Sci_Name, COUNT(*) as cnt, MAX(Confidence) as maxconf, "
        "MAX(Date||' '||Time) as lastdt, File_Name, Date "
        "FROM detections WHERE Com_Name = ? LIMIT 1",
        (com_name,))

    if not row:
        return Div(H2(f"Species: {com_name}"), P("Not found in database."))

    slug_clean = _slug(com_name)
    safe_file = _safe_basename(row["File_Name"])
    # Validate date is YYYY-MM-DD before embedding in a file path
    safe_date = row["Date"] if re.match(r'^\d{4}-\d{2}-\d{2}$', row["Date"] or "") else ""
    filename = f"/By_Date/{safe_date}/{slug_clean}/{safe_file}" if safe_date and safe_file else ""

    return Div(
        H2(row["Com_Name"], style="margin-bottom:4px"),
        P(f"({row['Sci_Name']})", style="font-style:italic;margin-bottom:16px;color:#555"),
        Div(
            Div(Div("Total Detections", cls="widget-label"), Div(f"{row['cnt']:,}", cls="widget-value"), cls="widget"),
            Div(Div("Best Confidence",  cls="widget-label"), Div(f"{round(float(row['maxconf'])*100)}%", cls="widget-value"), cls="widget"),
            Div(Div("Last Seen",        cls="widget-label"), Div(row["lastdt"], cls="widget-value", style="font-size:1rem"), cls="widget"),
            cls="widget-grid",
        ),
        Div(
            Div("Best Recording", cls="widget-label"),
            Audio(Source(src=filename, type="audio/mpeg"),
                  controls=True, style="width:100%;max-width:500px")
            if filename else P("Recording unavailable.", style="color:#777"),
            cls="widget",
            style="margin-top:4px",
        ),
    )


# ---------------------------------------------------------------------------
# FastHTML application
# ---------------------------------------------------------------------------

if FASTHTML_AVAILABLE:

    # static_path='static' tells FastHTML to serve files from the ./static/
    # directory (relative to the working directory, which the systemd service
    # sets to $HOME/BirdNET-Pi/homepage).  htmx.min.js is served at /static/htmx.min.js.
    app = FastHTML(static_path='static')

    @app.get("/app/dashboard")
    def dashboard():
        return _shell(_dashboard_content(), "/app/dashboard")

    # HTMX partial: return just the content div, not the shell
    @app.get("/app/dashboard", headers={"HX-Request": "true"})
    def dashboard_partial():
        return _dashboard_content()

    @app.get("/app/detections")
    def detections():
        return _shell(_detections_content(), "/app/detections")

    @app.get("/app/detections", headers={"HX-Request": "true"})
    def detections_partial():
        return _detections_content()

    @app.get("/app/recordings")
    def recordings():
        return _shell(_recordings_content(), "/app/recordings")

    @app.get("/app/recordings", headers={"HX-Request": "true"})
    def recordings_partial():
        return _recordings_content()

    @app.get("/app/charts")
    def charts():
        return _shell(_charts_content(), "/app/charts")

    @app.get("/app/charts", headers={"HX-Request": "true"})
    def charts_partial():
        return _charts_content()

    @app.get("/app/species/{slug}")
    def species(slug: str):
        return _shell(_species_content(slug), "/app/recordings")

    @app.get("/app/species/{slug}", headers={"HX-Request": "true"})
    def species_partial(slug: str):
        return _species_content(slug)

    @app.get("/app")
    @app.get("/app/")
    def app_root():
        return dashboard()

    if __name__ == "__main__":
        serve(port=PORT)

else:
    # Fallback: print install instructions if FastHTML is not installed
    if __name__ == "__main__":
        print("python-fasthtml is not installed.")
        print("Install it with:  pip install python-fasthtml")
        print("")
        print("This file is a proof-of-concept FastHTML web app for BirdNET-Pi.")
        print("See docs/ui-improvement-proposal.md for the full migration plan.")
