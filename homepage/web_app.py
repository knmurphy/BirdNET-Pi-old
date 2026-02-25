"""
Field Station OS - FastHTML Web Application

A Python-native web UI for passive acoustic monitoring.
Built with FastHTML for HTMX-based navigation (no iframe, no full page reload).

Following TDD: This code is written to pass tests, then refactored.
"""
import os
import sqlite3
from datetime import date

from fasthtml.common import FastHTML, serve, Div, H2

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
    """Wrap content in the app shell (HTML structure)."""
    # For now, return just the content
    # Will be expanded to include full HTML shell with navigation
    return content


if __name__ == "__main__":
    serve(port=8502)
