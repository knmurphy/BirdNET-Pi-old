"""Tests for Flickr image integration."""

import pytest
from unittest.mock import patch, MagicMock
import sqlite3

from fastapi.testclient import TestClient

from api.main import app
from api.services.flickr_service import FlickrService
from api.models.flickr import FlickrImage, FlickrImageResponse


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestFlickrModels:
    """Tests for Flickr Pydantic models."""

    def test_flickr_image_required_fields(self):
        """FlickrImage requires sci_name, com_name, image_url."""
        image = FlickrImage(
            sci_name="Turdus migratorius",
            com_name="American Robin",
            image_url="https://example.com/image.jpg",
        )
        assert image.sci_name == "Turdus migratorius"
        assert image.com_name == "American Robin"
        assert image.image_url == "https://example.com/image.jpg"
        assert image.title is None
        assert image.author_url is None
        assert image.license_url is None

    def test_flickr_image_optional_fields(self):
        """FlickrImage accepts optional attribution fields."""
        image = FlickrImage(
            sci_name="Turdus migratorius",
            com_name="American Robin",
            image_url="https://example.com/image.jpg",
            title="American Robin in flight",
            author_url="https://flickr.com/people/user",
            license_url="https://creativecommons.org/licenses/by/2.0/",
        )
        assert image.title == "American Robin in flight"
        assert image.author_url == "https://flickr.com/people/user"
        assert image.license_url == "https://creativecommons.org/licenses/by/2.0/"

    def test_flickr_image_response_source_field(self):
        """FlickrImageResponse includes source field."""
        response = FlickrImageResponse(
            sci_name="Cardinalis cardinalis",
            com_name="Northern Cardinal",
            image_url="https://example.com/cardinal.jpg",
            source="flickr",
        )
        assert response.source == "flickr"


class TestFlickrServicePaths:
    """Tests for FlickrService path configuration."""

    def test_flickr_db_path(self):
        """FlickrService uses correct flickr.db path."""
        service = FlickrService()
        assert "BirdNET-Pi" in str(service.FLICKR_DB_PATH)
        assert service.FLICKR_DB_PATH.name == "flickr.db"

    def test_birds_db_path(self):
        """FlickrService uses correct birds.db path."""
        service = FlickrService()
        assert "BirdNET-Pi" in str(service.BIRDS_DB_PATH)
        assert service.BIRDS_DB_PATH.name == "birds.db"


class TestFlickrServiceGetCachedImage:
    """Tests for FlickrService.get_cached_image."""

    def test_returns_none_when_db_missing(self, tmp_path):
        """Returns None if flickr.db doesn't exist."""
        service = FlickrService()
        service.FLICKR_DB_PATH = tmp_path / "nonexistent.db"
        
        result = service.get_cached_image("Turdus migratorius")
        assert result is None

    def test_returns_image_when_found(self, tmp_path):
        """Returns FlickrImage when species is in cache."""
        # Create test database
        db_path = tmp_path / "flickr.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE images (
                sci_name TEXT,
                com_en_name TEXT,
                image_url TEXT,
                title TEXT,
                author_url TEXT,
                license_url TEXT
            )
        """)
        cursor.execute(
            "INSERT INTO images VALUES (?, ?, ?, ?, ?, ?)",
            [
                "Turdus migratorius",
                "American Robin",
                "https://flickr.com/123.jpg",
                "Robin Photo",
                "https://flickr.com/people/user",
                "https://creativecommons.org/licenses/by/2.0/",
            ],
        )
        conn.commit()
        conn.close()

        service = FlickrService()
        service.FLICKR_DB_PATH = db_path
        
        result = service.get_cached_image("Turdus migratorius")
        
        assert result is not None
        assert result.sci_name == "Turdus migratorius"
        assert result.com_name == "American Robin"
        assert result.image_url == "https://flickr.com/123.jpg"
        assert result.title == "Robin Photo"

    def test_returns_none_for_unknown_species(self, tmp_path):
        """Returns None when species not in cache."""
        db_path = tmp_path / "flickr.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE images (
                sci_name TEXT,
                com_en_name TEXT,
                image_url TEXT,
                title TEXT,
                author_url TEXT,
                license_url TEXT
            )
        """)
        conn.commit()
        conn.close()

        service = FlickrService()
        service.FLICKR_DB_PATH = db_path
        
        result = service.get_cached_image("Unknownus speciesus")
        assert result is None

    def test_handles_db_error_gracefully(self, tmp_path):
        """Returns None on database error (corrupt DB, etc.)."""
        db_path = tmp_path / "corrupt.db"
        db_path.write_text("not a sqlite database")
        
        service = FlickrService()
        service.FLICKR_DB_PATH = db_path
        
        result = service.get_cached_image("Turdus migratorius")
        assert result is None


class TestFlickrServiceGetImageForCommonName:
    """Tests for FlickrService.get_image_for_common_name."""

    def test_returns_none_when_db_missing(self, tmp_path):
        """Returns None if flickr.db doesn't exist."""
        service = FlickrService()
        service.FLICKR_DB_PATH = tmp_path / "nonexistent.db"
        
        result = service.get_image_for_common_name("American Robin")
        assert result is None

    def test_finds_by_common_name_case_insensitive(self, tmp_path):
        """Finds image regardless of common name case."""
        db_path = tmp_path / "flickr.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE images (
                sci_name TEXT,
                com_en_name TEXT,
                image_url TEXT,
                title TEXT,
                author_url TEXT,
                license_url TEXT
            )
        """)
        cursor.execute(
            "INSERT INTO images VALUES (?, ?, ?, ?, ?, ?)",
            [
                "Turdus migratorius",
                "American Robin",
                "https://flickr.com/robin.jpg",
                None,
                None,
                None,
            ],
        )
        conn.commit()
        conn.close()

        service = FlickrService()
        service.FLICKR_DB_PATH = db_path
        
        # Test various case permutations
        for name in ["american robin", "AMERICAN ROBIN", "American robin"]:
            result = service.get_image_for_common_name(name)
            assert result is not None, f"Failed for {name}"
            assert result.sci_name == "Turdus migratorius"

    def test_returns_none_for_unknown_common_name(self, tmp_path):
        """Returns None when common name not in cache."""
        db_path = tmp_path / "flickr.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE images (
                sci_name TEXT,
                com_en_name TEXT,
                image_url TEXT,
                title TEXT,
                author_url TEXT,
                license_url TEXT
            )
        """)
        conn.commit()
        conn.close()

        service = FlickrService()
        service.FLICKR_DB_PATH = db_path
        
        result = service.get_image_for_common_name("Nonexistent Bird")
        assert result is None


class TestFlickrServiceGetOrFetchImage:
    """Tests for FlickrService.get_or_fetch_image."""

    def test_returns_response_when_found_by_sci_name(self, tmp_path):
        """Returns FlickrImageResponse when found by scientific name."""
        db_path = tmp_path / "flickr.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE images (
                sci_name TEXT,
                com_en_name TEXT,
                image_url TEXT,
                title TEXT,
                author_url TEXT,
                license_url TEXT
            )
        """)
        cursor.execute(
            "INSERT INTO images VALUES (?, ?, ?, ?, ?, ?)",
            ["Cardinalis cardinalis", "Northern Cardinal", "https://flickr.com/card.jpg", None, None, None],
        )
        conn.commit()
        conn.close()

        service = FlickrService()
        service.FLICKR_DB_PATH = db_path
        
        result = service.get_or_fetch_image("Cardinalis cardinalis", "Northern Cardinal")
        
        assert result is not None
        assert isinstance(result, FlickrImageResponse)
        assert result.sci_name == "Cardinalis cardinalis"
        assert result.source == "flickr"

    def test_falls_back_to_common_name(self, tmp_path):
        """Tries common name if scientific name not found."""
        db_path = tmp_path / "flickr.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE images (
                sci_name TEXT,
                com_en_name TEXT,
                image_url TEXT,
                title TEXT,
                author_url TEXT,
                license_url TEXT
            )
        """)
        # Insert with different sci_name than query
        cursor.execute(
            "INSERT INTO images VALUES (?, ?, ?, ?, ?, ?)",
            ["Old scientific name", "Blue Jay", "https://flickr.com/jay.jpg", None, None, None],
        )
        conn.commit()
        conn.close()

        service = FlickrService()
        service.FLICKR_DB_PATH = db_path
        
        result = service.get_or_fetch_image("Cyanocitta cristata", "Blue Jay")
        
        assert result is not None
        assert result.com_name == "Blue Jay"
        assert result.source == "flickr"

    def test_returns_none_when_not_found(self, tmp_path):
        """Returns None when image not in cache by either name."""
        db_path = tmp_path / "flickr.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE images (
                sci_name TEXT,
                com_en_name TEXT,
                image_url TEXT,
                title TEXT,
                author_url TEXT,
                license_url TEXT
            )
        """)
        conn.commit()
        conn.close()

        service = FlickrService()
        service.FLICKR_DB_PATH = db_path
        
        result = service.get_or_fetch_image("Unknownus speciesus", "Unknown Bird")
        assert result is None


class TestSpeciesImageEndpoint:
    """Tests for GET /api/species/{com_name}/image endpoint."""

    def test_returns_404_when_no_image(self, client, tmp_path, monkeypatch):
        """Returns 404 when species has no cached image."""
        # Create empty flickr.db
        db_path = tmp_path / "flickr.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE images (
                sci_name TEXT,
                com_en_name TEXT,
                image_url TEXT,
                title TEXT,
                author_url TEXT,
                license_url TEXT
            )
        """)
        conn.commit()
        conn.close()

        # Patch the path
        monkeypatch.setattr(
            FlickrService,
            "FLICKR_DB_PATH",
            db_path,
        )
        
        response = client.get("/api/species/Unknown%20Bird/image")
        assert response.status_code == 404

    def test_returns_image_when_found(self, client, tmp_path, monkeypatch):
        """Returns image data when species is in cache."""
        db_path = tmp_path / "flickr.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE images (
                sci_name TEXT,
                com_en_name TEXT,
                image_url TEXT,
                title TEXT,
                author_url TEXT,
                license_url TEXT
            )
        """)
        cursor.execute(
            "INSERT INTO images VALUES (?, ?, ?, ?, ?, ?)",
            [
                "Turdus migratorius",
                "American Robin",
                "https://flickr.com/robin.jpg",
                "Robin in tree",
                "https://flickr.com/people/birder",
                "https://creativecommons.org/licenses/by/2.0/",
            ],
        )
        conn.commit()
        conn.close()

        monkeypatch.setattr(FlickrService, "FLICKR_DB_PATH", db_path)
        
        response = client.get("/api/species/American%20Robin/image")
        
        assert response.status_code == 200
        data = response.json()
        assert data["sci_name"] == "Turdus migratorius"
        assert data["com_name"] == "American Robin"
        assert data["image_url"] == "https://flickr.com/robin.jpg"
        assert data["title"] == "Robin in tree"
        assert data["source"] == "flickr"

    def test_handles_special_characters_in_name(self, client, tmp_path, monkeypatch):
        """Handles URL encoding and special characters."""
        db_path = tmp_path / "flickr.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE images (
                sci_name TEXT,
                com_en_name TEXT,
                image_url TEXT,
                title TEXT,
                author_url TEXT,
                license_url TEXT
            )
        """)
        cursor.execute(
            "INSERT INTO images VALUES (?, ?, ?, ?, ?, ?)",
            ["Pipilo erythrophthalmus", "Eastern Towhee", "https://flickr.com/towhee.jpg", None, None, None],
        )
        conn.commit()
        conn.close()

        monkeypatch.setattr(FlickrService, "FLICKR_DB_PATH", db_path)
        
        # Test URL-encoded name
        response = client.get("/api/species/Eastern%20Towhee/image")
        assert response.status_code == 200
        assert response.json()["com_name"] == "Eastern Towhee"

    def test_returns_404_when_flickr_db_missing(self, client, tmp_path, monkeypatch):
        """Returns 404 when flickr.db doesn't exist."""
        nonexistent = tmp_path / "nonexistent.db"
        monkeypatch.setattr(FlickrService, "FLICKR_DB_PATH", nonexistent)
        
        response = client.get("/api/species/American%20Robin/image")
        assert response.status_code == 404
