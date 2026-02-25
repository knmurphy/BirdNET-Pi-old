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

# Create the FastHTML application
app = FastHTML()


@app.get("/app/dashboard")
def dashboard():
    """Render the dashboard page."""
    return _shell(_dashboard_content(), "/app/dashboard")


def _dashboard_content():
    """Generate the dashboard content."""
    return Div(H2("Dashboard"))


def _shell(content, current_path: str = "/app/dashboard"):
    """Wrap content in the app shell (HTML structure)."""
    # For now, return just the content
    # Will be expanded to include full HTML shell with navigation
    return content


if __name__ == "__main__":
    serve(port=8502)
