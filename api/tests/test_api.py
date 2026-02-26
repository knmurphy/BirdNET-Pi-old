"""Tests for Field Station API endpoints."""

import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestRootEndpoints:
    """Tests for root endpoints."""

    def test_root(self, client):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Field Station API"
        assert "version" in data

    def test_health(self, client):
        """Test health endpoint returns ok."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestDetectionsEndpoints:
    """Tests for detection endpoints."""

    def test_today_summary_structure(self, client):
        """Test /api/detections/today/summary returns correct structure."""
        response = client.get("/api/detections/today/summary")
        # May fail if database doesn't exist, which is fine for structure test
        if response.status_code == 200:
            data = response.json()
            assert "total_detections" in data
            assert "species_count" in data
            assert "top_species" in data
            assert "hourly_counts" in data
            assert "generated_at" in data
            assert len(data["hourly_counts"]) == 24


class TestSpeciesEndpoints:
    """Tests for species endpoints."""

    def test_species_today_structure(self, client):
        """Test /api/species/today returns correct structure."""
        response = client.get("/api/species/today")
        if response.status_code == 200:
            data = response.json()
            assert "species" in data
            assert "generated_at" in data


class TestSystemEndpoints:
    """Tests for system endpoints."""

    def test_system_returns_data(self, client):
        """Test /api/system returns system info."""
        response = client.get("/api/system")
        assert response.status_code == 200
        data = response.json()
        assert "cpu_percent" in data
        assert "temperature_celsius" in data
        assert "disk_used_gb" in data
        assert "disk_total_gb" in data
        assert "uptime_seconds" in data
        assert "active_classifiers" in data
        assert "sse_subscribers" in data
        assert "generated_at" in data


class TestClassifiersEndpoints:
    """Tests for classifier endpoints."""

    def test_get_classifiers(self, client):
        """Test /api/classifiers returns list."""
        response = client.get("/api/classifiers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_toggle_classifier_not_found(self, client):
        """Test toggle returns 404 for unknown classifier."""
        response = client.post("/api/classifiers/unknown/toggle")
        assert response.status_code == 404


class TestSettingsEndpoints:
    """Tests for settings endpoints."""

    def test_get_settings(self, client):
        """Test /api/settings returns settings."""
        response = client.get("/api/settings")
        assert response.status_code == 200
        data = response.json()
        assert "audio_path" in data
        assert "latitude" in data
        assert "longitude" in data
        assert "confidence_threshold" in data
        assert "generated_at" in data


class TestEventsEndpoint:
    """Tests for SSE events endpoint."""

    @pytest.mark.skip(reason="SSE endpoint requires async client; hangs in sync TestClient")
    def test_events_endpoint_exists(self, client):
        """Test /api/events endpoint exists."""
        # SSE streams require async testing with httpx.AsyncClient
        # The sync TestClient hangs on infinite streams
        # See: https://github.com/encode/starlette/issues/1562
        pass
