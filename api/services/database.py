"""Database connection and query utilities."""

import duckdb
import sqlite3
from contextlib import contextmanager

from api.config import settings


def get_duckdb_connection(read_only: bool = True) -> duckdb.DuckDBPyConnection:
    """Get a DuckDB connection to the bird database.

    Args:
        read_only: If True, opens in read-only mode (default).

    Returns:
        DuckDB connection object.

    Note:
        Caller is responsible for closing the connection.
    """
    db_path = settings.duckdb_path

    # Fall back to SQLite path if DuckDB doesn't exist yet
    if not db_path.exists():
        db_path = settings.database_path

    return duckdb.connect(str(db_path), read_only=read_only)


def get_connection() -> sqlite3.Connection:
    """Get a SQLite connection to the bird database (legacy support).

    Returns:
        SQLite connection object.

    Note:
        Caller is responsible for closing the connection.
        Prefer get_duckdb_connection() for new code.
    """
    return sqlite3.connect(str(settings.database_path))


@contextmanager
def duckdb_cursor(read_only: bool = True):
    """Context manager for DuckDB cursor.

    Usage:
        with duckdb_cursor() as cur:
            result = cur.execute("SELECT * FROM detections").fetchall()
    """
    conn = get_duckdb_connection(read_only=read_only)
    try:
        yield conn.cursor()
    finally:
        conn.close()


def init_duckdb_schema(conn: duckdb.DuckDBPyConnection) -> None:
    """Initialize DuckDB schema if it doesn't exist.

    This creates the detections table with indexes for optimal query performance.
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            iso8601 TEXT,
            com_name TEXT NOT NULL,
            sci_name TEXT NOT NULL,
            confidence REAL NOT NULL,
            file_name TEXT,
            classifier TEXT DEFAULT 'birdnet',
            lat REAL,
            lon REAL,
            cutoff REAL,
            week INTEGER,
            sens REAL,
            overlap REAL
        )
    """)

    # Create indexes for common queries
    conn.execute("CREATE INDEX IF NOT EXISTS idx_date ON detections(date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_com_name ON detections(com_name)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_classifier ON detections(classifier)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_date_com_name ON detections(date, com_name)")
