"""
Field Station OS - FastHTML Web Application

A Python-native web UI for passive acoustic monitoring.
Built with FastHTML for HTMX-based navigation (no iframe, no full page reload).

Following TDD: This code is written to pass tests, then refactored.
"""
import os
import sqlite3
from datetime import date, datetime

from fasthtml.common import FastHTML, serve, Div, H2, Header, Nav, A, P

# Database configuration
DB_PATH = os.path.join(os.path.expanduser("~"), "BirdNET-Pi", "scripts", "birds.db")


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
    except Exception:
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
    except Exception:
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
    except Exception:
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
        Div(f"Today's Detections: {today_count}"),
        Div(f"Today's Species: {species_count}"),
    ]

    if latest:
        widgets.append(Div(f"Latest: {latest['Com_Name']} ({latest['Time']})"))
    else:
        widgets.append(Div("Latest: No detections yet"))

    return Div(*widgets)


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

    nav_links = [A(name, href=path) for name, path in tabs]

    return Div(
        Header(f"Field Station - {current_time}"),
        content,
        Nav(*nav_links),
    )


if __name__ == "__main__":
    serve(port=8502)


@app.get("/app/detections")
def detections():
    """Render the detections page."""
    return _shell(_detections_content(), "/app/detections")


def _detections_content():
    """Generate the detections list content."""
    today = date.today().isoformat()
    try:
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        con.row_factory = sqlite3.Row
        cursor = con.execute(
            "SELECT Com_Name, Sci_Name, Time, Confidence FROM detections WHERE Date = ? ORDER BY Time DESC LIMIT 50",
            (today,)
        )
        rows = cursor.fetchall()
        con.close()

        if not rows:
            return Div(H2("Today's Detections"), P("No detections yet today."))

        items = [
            Div(f"{row['Time']} - {row['Com_Name']} ({float(row['Confidence'])*100:.0f}%)")
            for row in rows
        ]
        return Div(H2("Today's Detections"), *items)
    except Exception:
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
            Div(f"{r['Com_Name']} - {r['count']} detections")
            for r in rows
        ]
        return Div(H2("Today's Species"), *items)
    except Exception:
        return Div(H2("Today's Species"), P("Error loading species."))


def get_total_detection_count() -> int:
    """Get total detections (all time)."""
    try:
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        cursor = con.execute("SELECT COUNT(*) FROM detections")
        count = cursor.fetchone()[0]
        con.close()
        return count
    except Exception:
        return 0


def get_total_species_count() -> int:
    """Get total distinct species (all time)."""
    try:
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        cursor = con.execute("SELECT COUNT(DISTINCT Com_Name) FROM detections")
        count = cursor.fetchone()[0]
        con.close()
        return count
    except Exception:
        return 0



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
        Div(f"Total Detections: {total_detections:,}"),
        Div(f"Total Species: {total_species:,}"),
        P("System stats coming soon...")
    )