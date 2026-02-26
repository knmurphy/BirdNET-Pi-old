#!/usr/bin/env python3
"""Migrate detections from legacy SQLite database to DuckDB.

Usage:
    python scripts/migrate_to_duckdb.py [SQLITE_PATH] [DUCKDB_PATH]
    python scripts/migrate_to_duckdb.py --help
"""

import argparse
import sqlite3
import sys
import time
from pathlib import Path

import duckdb

BATCH_SIZE = 1000

SQLITE_COLUMNS = [
    "ROWID",
    "Date",
    "Time",
    "Sci_Name",
    "Com_Name",
    "Confidence",
    "Lat",
    "Lon",
    "Cutoff",
    "Week",
    "Sens",
    "Overlap",
    "File_Name",
]

CREATE_TABLE_SQL = """
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
"""

CREATE_INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_date ON detections(date)",
    "CREATE INDEX IF NOT EXISTS idx_com_name ON detections(com_name)",
    "CREATE INDEX IF NOT EXISTS idx_classifier ON detections(classifier)",
    "CREATE INDEX IF NOT EXISTS idx_date_com_name ON detections(date, com_name)",
]

INSERT_SQL = """
INSERT INTO detections (
    id, date, time, iso8601, com_name, sci_name,
    confidence, file_name, classifier,
    lat, lon, cutoff, week, sens, overlap
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


def build_iso8601(date_str: str, time_str: str) -> str | None:
    """Construct ISO 8601 string from date and time components."""
    if date_str and time_str:
        return f"{date_str}T{time_str}"
    return None


def sqlite_row_to_duckdb(row: tuple) -> tuple:
    """Map a SQLite row (with ROWID) to a DuckDB insert tuple.

    SQLite columns order (from SQLITE_COLUMNS):
        ROWID, Date, Time, Sci_Name, Com_Name, Confidence,
        Lat, Lon, Cutoff, Week, Sens, Overlap, File_Name

    DuckDB columns order (from INSERT_SQL):
        id, date, time, iso8601, com_name, sci_name,
        confidence, file_name, classifier,
        lat, lon, cutoff, week, sens, overlap
    """
    (
        rowid,
        date_val,
        time_val,
        sci_name,
        com_name,
        confidence,
        lat,
        lon,
        cutoff,
        week,
        sens,
        overlap,
        file_name,
    ) = row

    iso8601 = build_iso8601(date_val or "", time_val or "")

    return (
        rowid,
        date_val,
        time_val,
        iso8601,
        com_name,
        sci_name,
        confidence,
        file_name,
        "birdnet",  # classifier default
        lat,
        lon,
        cutoff,
        week,
        sens,
        overlap,
    )


def migrate(
    sqlite_path: str | Path,
    duckdb_path: str | Path,
    *,
    force: bool = False,
) -> int:
    """Run the migration from SQLite to DuckDB.

    Args:
        sqlite_path: Path to the source SQLite database.
        duckdb_path: Path to the destination DuckDB database.
        force: If True, drop existing detections table before migrating.

    Returns:
        Number of rows migrated.
    """
    sqlite_path = Path(sqlite_path).expanduser()
    duckdb_path = Path(duckdb_path).expanduser()

    if not sqlite_path.exists():
        raise FileNotFoundError(f"SQLite database not found: {sqlite_path}")

    # Connect to SQLite (read-only)
    sqlite_conn = sqlite3.connect(f"file:{sqlite_path}?mode=ro", uri=True)

    # Connect to DuckDB
    duck_conn = duckdb.connect(str(duckdb_path))

    try:
        # Check if DuckDB already has data
        duck_conn.execute(CREATE_TABLE_SQL)
        existing = duck_conn.execute(
            "SELECT COUNT(*) FROM detections"
        ).fetchone()[0]

        if existing > 0 and not force:
            raise RuntimeError(
                f"DuckDB already has {existing} rows. "
                "Use --force to overwrite."
            )

        if existing > 0 and force:
            duck_conn.execute("DELETE FROM detections")

        # Read from SQLite
        select_cols = ", ".join(SQLITE_COLUMNS)
        cursor = sqlite_conn.execute(f"SELECT {select_cols} FROM detections")

        total = 0
        while True:
            rows = cursor.fetchmany(BATCH_SIZE)
            if not rows:
                break

            mapped = [sqlite_row_to_duckdb(row) for row in rows]
            duck_conn.executemany(INSERT_SQL, mapped)
            total += len(mapped)

        # Create indexes
        for idx_sql in CREATE_INDEXES_SQL:
            duck_conn.execute(idx_sql)

        return total

    finally:
        sqlite_conn.close()
        duck_conn.close()


def main(argv: list[str] | None = None) -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate BirdNET-Pi detections from SQLite to DuckDB.",
    )
    parser.add_argument(
        "sqlite_path",
        nargs="?",
        default="~/BirdNET-Pi/scripts/birds.db",
        help="Path to SQLite database (default: ~/BirdNET-Pi/scripts/birds.db)",
    )
    parser.add_argument(
        "duckdb_path",
        nargs="?",
        default="~/BirdNET-Pi/scripts/birds.duckdb",
        help="Path to DuckDB database (default: ~/BirdNET-Pi/scripts/birds.duckdb)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing data in DuckDB",
    )

    args = parser.parse_args(argv)

    t0 = time.monotonic()
    try:
        count = migrate(args.sqlite_path, args.duckdb_path, force=args.force)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    elapsed = time.monotonic() - t0
    print(f"Migrated {count} rows in {elapsed:.2f}s")


if __name__ == "__main__":
    main()
