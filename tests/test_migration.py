"""Tests for SQLite → DuckDB migration script."""

import sqlite3
import tempfile
from pathlib import Path

import duckdb
import pytest

from scripts.migrate_to_duckdb import build_iso8601, migrate, sqlite_row_to_duckdb


def _create_sqlite(path: Path) -> None:
    """Create a SQLite database matching legacy BirdNET-Pi schema."""
    conn = sqlite3.connect(str(path))
    conn.execute("""
        CREATE TABLE detections (
            Date TEXT,
            Time TEXT,
            Sci_Name TEXT,
            Com_Name TEXT,
            Confidence REAL,
            Lat REAL,
            Lon REAL,
            Cutoff REAL,
            Week INTEGER,
            Sens REAL,
            Overlap REAL,
            File_Name TEXT
        )
    """)
    conn.commit()
    conn.close()


def _insert_sqlite_row(
    path: Path,
    *,
    date: str = "2024-06-15",
    time: str = "08:30:00",
    sci_name: str = "Turdus migratorius",
    com_name: str = "American Robin",
    confidence: float = 0.85,
    lat: float = 42.36,
    lon: float = -71.06,
    cutoff: float = 0.7,
    week: int = 24,
    sens: float = 1.25,
    overlap: float = 0.0,
    file_name: str = "2024-06-15-birdnet-08:30:00.wav",
) -> None:
    conn = sqlite3.connect(str(path))
    conn.execute(
        """
        INSERT INTO detections
            (Date, Time, Sci_Name, Com_Name, Confidence,
             Lat, Lon, Cutoff, Week, Sens, Overlap, File_Name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            date, time, sci_name, com_name, confidence,
            lat, lon, cutoff, week, sens, overlap, file_name,
        ),
    )
    conn.commit()
    conn.close()


@pytest.fixture()
def migration_paths(tmp_path):
    """Provide temp SQLite and DuckDB paths."""
    sqlite_path = tmp_path / "birds.db"
    duckdb_path = tmp_path / "birds.duckdb"
    _create_sqlite(sqlite_path)
    return sqlite_path, duckdb_path


class TestMigrateEmptyDB:
    """Migration of an empty SQLite database."""

    def test_migrate_empty_db(self, migration_paths):
        """Empty SQLite produces empty DuckDB with correct schema."""
        sqlite_path, duckdb_path = migration_paths

        count = migrate(sqlite_path, duckdb_path)

        assert count == 0

        conn = duckdb.connect(str(duckdb_path))
        result = conn.execute("SELECT COUNT(*) FROM detections").fetchone()
        assert result[0] == 0

        # Verify table exists with expected columns
        cols = conn.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'detections' ORDER BY ordinal_position"
        ).fetchall()
        col_names = [c[0] for c in cols]
        assert "id" in col_names
        assert "iso8601" in col_names
        assert "classifier" in col_names
        conn.close()


class TestMigrateSingleRow:
    """Migration of a single detection row."""

    def test_migrate_single_row(self, migration_paths):
        """One detection row migrates with all fields mapped correctly."""
        sqlite_path, duckdb_path = migration_paths
        _insert_sqlite_row(sqlite_path)

        count = migrate(sqlite_path, duckdb_path)
        assert count == 1

        conn = duckdb.connect(str(duckdb_path))
        row = conn.execute(
            "SELECT id, date, time, iso8601, com_name, sci_name, "
            "confidence, file_name, classifier, "
            "lat, lon, cutoff, week, sens, overlap "
            "FROM detections"
        ).fetchone()
        conn.close()

        assert row is not None
        (
            id_, date_, time_, iso8601_, com_name_, sci_name_,
            confidence_, file_name_, classifier_,
            lat_, lon_, cutoff_, week_, sens_, overlap_,
        ) = row

        assert id_ == 1  # ROWID of first insert
        assert date_ == "2024-06-15"
        assert time_ == "08:30:00"
        assert iso8601_ == "2024-06-15T08:30:00"
        assert com_name_ == "American Robin"
        assert sci_name_ == "Turdus migratorius"
        assert confidence_ == pytest.approx(0.85)
        assert file_name_ == "2024-06-15-birdnet-08:30:00.wav"
        assert classifier_ == "birdnet"
        assert lat_ == pytest.approx(42.36)
        assert lon_ == pytest.approx(-71.06)
        assert cutoff_ == pytest.approx(0.7)
        assert week_ == 24
        assert sens_ == pytest.approx(1.25)
        assert overlap_ == pytest.approx(0.0)

    def test_migrate_null_optional_fields(self, migration_paths):
        """NULL values in optional SQLite fields migrate as NULL."""
        sqlite_path, duckdb_path = migration_paths
        _insert_sqlite_row(
            sqlite_path,
            lat=None,
            lon=None,
            cutoff=None,
            week=None,
            sens=None,
            overlap=None,
            file_name=None,
        )

        count = migrate(sqlite_path, duckdb_path)
        assert count == 1

        conn = duckdb.connect(str(duckdb_path))
        row = conn.execute(
            "SELECT lat, lon, cutoff, week, sens, overlap, file_name "
            "FROM detections"
        ).fetchone()
        conn.close()

        assert row == (None, None, None, None, None, None, None)


class TestIso8601Construction:
    """Verify ISO 8601 datetime construction."""

    def test_migrate_iso8601_construction(self, migration_paths):
        """iso8601 = Date + 'T' + Time."""
        sqlite_path, duckdb_path = migration_paths
        _insert_sqlite_row(sqlite_path, date="2024-01-02", time="14:05:30")

        migrate(sqlite_path, duckdb_path)

        conn = duckdb.connect(str(duckdb_path))
        iso = conn.execute("SELECT iso8601 FROM detections").fetchone()[0]
        conn.close()

        assert iso == "2024-01-02T14:05:30"

    def test_iso8601_short_time_format(self, migration_paths):
        """HH:MM format (no seconds) still works."""
        sqlite_path, duckdb_path = migration_paths
        _insert_sqlite_row(sqlite_path, date="2024-03-10", time="09:15")

        migrate(sqlite_path, duckdb_path)

        conn = duckdb.connect(str(duckdb_path))
        iso = conn.execute("SELECT iso8601 FROM detections").fetchone()[0]
        conn.close()

        assert iso == "2024-03-10T09:15"

    def test_build_iso8601_helper(self):
        """Unit test the helper function directly."""
        assert build_iso8601("2024-06-15", "08:30:00") == "2024-06-15T08:30:00"
        assert build_iso8601("", "") is None
        assert build_iso8601("2024-06-15", "") is None
        assert build_iso8601("", "08:30:00") is None


class TestClassifierDefault:
    """Verify classifier column defaults to 'birdnet'."""

    def test_migrate_classifier_default(self, migration_paths):
        """classifier is always 'birdnet' for migrated rows."""
        sqlite_path, duckdb_path = migration_paths
        _insert_sqlite_row(sqlite_path, com_name="Blue Jay")
        _insert_sqlite_row(sqlite_path, com_name="Cardinal")

        migrate(sqlite_path, duckdb_path)

        conn = duckdb.connect(str(duckdb_path))
        classifiers = conn.execute(
            "SELECT DISTINCT classifier FROM detections"
        ).fetchall()
        conn.close()

        assert classifiers == [("birdnet",)]


class TestMigrateEdgeCases:
    """Edge cases and error handling."""

    def test_sqlite_not_found(self, tmp_path):
        """FileNotFoundError when SQLite DB doesn't exist."""
        with pytest.raises(FileNotFoundError, match="not found"):
            migrate(
                tmp_path / "nonexistent.db",
                tmp_path / "out.duckdb",
            )

    def test_duckdb_already_has_data_no_force(self, migration_paths):
        """RuntimeError when DuckDB already has data and force=False."""
        sqlite_path, duckdb_path = migration_paths
        _insert_sqlite_row(sqlite_path)

        migrate(sqlite_path, duckdb_path)

        # Second migration without force should fail
        with pytest.raises(RuntimeError, match="already has"):
            migrate(sqlite_path, duckdb_path)

    def test_duckdb_force_overwrite(self, migration_paths):
        """force=True clears existing DuckDB data and re-migrates."""
        sqlite_path, duckdb_path = migration_paths
        _insert_sqlite_row(sqlite_path, com_name="Blue Jay")

        migrate(sqlite_path, duckdb_path)

        # Add a second species to SQLite
        _insert_sqlite_row(sqlite_path, com_name="Cardinal")

        # Force re-migration
        count = migrate(sqlite_path, duckdb_path, force=True)
        assert count == 2

        conn = duckdb.connect(str(duckdb_path))
        total = conn.execute("SELECT COUNT(*) FROM detections").fetchone()[0]
        conn.close()
        assert total == 2

    def test_batch_insert(self, migration_paths):
        """Multiple batches are handled correctly (> BATCH_SIZE rows)."""
        sqlite_path, duckdb_path = migration_paths

        # Insert 2500 rows to trigger multiple batches
        conn = sqlite3.connect(str(sqlite_path))
        for i in range(2500):
            conn.execute(
                """
                INSERT INTO detections
                    (Date, Time, Sci_Name, Com_Name, Confidence,
                     Lat, Lon, Cutoff, Week, Sens, Overlap, File_Name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "2024-06-15", "08:30:00", "Turdus migratorius",
                    f"Bird {i}", 0.9, 42.0, -71.0, 0.7, 24, 1.0, 0.0,
                    f"file_{i}.wav",
                ),
            )
        conn.commit()
        conn.close()

        count = migrate(sqlite_path, duckdb_path)
        assert count == 2500

        duck = duckdb.connect(str(duckdb_path))
        total = duck.execute("SELECT COUNT(*) FROM detections").fetchone()[0]
        duck.close()
        assert total == 2500


class TestSqliteRowMapping:
    """Unit tests for the row mapping function."""

    def test_sqlite_row_to_duckdb_mapping(self):
        """Verify tuple mapping from SQLite to DuckDB order."""
        row = (
            42,  # ROWID
            "2024-06-15",  # Date
            "08:30:00",  # Time
            "Turdus migratorius",  # Sci_Name
            "American Robin",  # Com_Name
            0.85,  # Confidence
            42.36,  # Lat
            -71.06,  # Lon
            0.7,  # Cutoff
            24,  # Week
            1.25,  # Sens
            0.0,  # Overlap
            "file.wav",  # File_Name
        )

        result = sqlite_row_to_duckdb(row)

        assert result == (
            42,  # id
            "2024-06-15",  # date
            "08:30:00",  # time
            "2024-06-15T08:30:00",  # iso8601
            "American Robin",  # com_name
            "Turdus migratorius",  # sci_name
            0.85,  # confidence
            "file.wav",  # file_name
            "birdnet",  # classifier
            42.36,  # lat
            -71.06,  # lon
            0.7,  # cutoff
            24,  # week
            1.25,  # sens
            0.0,  # overlap
        )
