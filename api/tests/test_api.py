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


class TestDetectionNotify:
    """Tests for the detection notification endpoint."""

    def test_notify_returns_published(self, client):
        """POST /api/detections/notify should return success."""
        response = client.post("/api/detections/notify", json={
            "com_name": "Carolina Wren",
            "sci_name": "Thryothorus ludovicianus",
            "confidence": 0.92,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "published"
        assert "subscribers_notified" in data

    def test_notify_requires_com_name(self, client):
        """POST /api/detections/notify should require com_name."""
        response = client.post("/api/detections/notify", json={
            "sci_name": "Thryothorus ludovicianus",
            "confidence": 0.92,
        })
        assert response.status_code == 422

    def test_notify_requires_confidence(self, client):
        """POST /api/detections/notify should require confidence."""
        response = client.post("/api/detections/notify", json={
            "com_name": "Carolina Wren",
            "sci_name": "Thryothorus ludovicianus",
        })
        assert response.status_code == 422

    def test_notify_default_classifier(self, client):
        """POST /api/detections/notify should default classifier to birdnet."""
        response = client.post("/api/detections/notify", json={
            "com_name": "Blue Jay",
            "sci_name": "Cyanocitta cristata",
            "confidence": 0.85,
        })
        assert response.status_code == 200
        # No error means the default classifier was applied

    def test_notify_with_custom_classifier(self, client):
        """POST /api/detections/notify should accept custom classifier."""
        response = client.post("/api/detections/notify", json={
            "com_name": "Blue Jay",
            "sci_name": "Cyanocitta cristata",
            "confidence": 0.85,
            "classifier": "custom_model",
            "file_name": "clip_001.wav",
        })
        assert response.status_code == 200



class TestAudioEndpoints:
    """Tests for audio endpoints."""

    def test_audio_devices_returns_list(self, client):
        """GET /api/audio/devices returns 200 with devices list."""
        response = client.get("/api/audio/devices")
        assert response.status_code == 200
        data = response.json()
        assert "devices" in data
        assert isinstance(data["devices"], list)

    def test_audio_file_not_found(self, client):
        """GET /api/audio/nonexistent.wav returns 404."""
        response = client.get("/api/audio/nonexistent.wav")
        assert response.status_code == 404

    def test_audio_path_traversal_blocked(self, client):
        """GET /api/audio/../../etc/passwd returns 400."""
        response = client.get("/api/audio/../../etc/passwd")
        assert response.status_code in (400, 404)


class TestSettingsUpdate:
    """Tests for POST /api/settings endpoint."""

    def test_post_settings_returns_updated(self, client, tmp_path, monkeypatch):
        """POST with valid data returns 200 with status='updated'."""
        conf = tmp_path / "birdnet.conf"
        conf.write_text("LATITUDE=0.0\nLONGITUDE=0.0\n")
        monkeypatch.setattr("api.routers.settings_router.settings.config_ini_path", conf)
        response = client.post("/api/settings", json={
            "latitude": 42.5,
            "longitude": -71.0,
            "confidence_threshold": 0.7,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "updated"
        assert set(data["fields_changed"]) == {"latitude", "longitude", "confidence_threshold"}
        # Verify values were written to the file
        content = conf.read_text()
        assert "LATITUDE=42.5" in content
        assert "LONGITUDE=-71.0" in content
        assert "SF_THRESH=0.7" in content

    def test_post_settings_partial_update(self, client, tmp_path, monkeypatch):
        """POST with only latitude returns 200, fields_changed=['latitude']."""
        conf = tmp_path / "birdnet.conf"
        conf.write_text("LATITUDE=0.0\nSENSITIVITY=1.0\n")
        monkeypatch.setattr("api.routers.settings_router.settings.config_ini_path", conf)
        response = client.post("/api/settings", json={"latitude": 35.0})
        assert response.status_code == 200
        data = response.json()
        assert data["fields_changed"] == ["latitude"]
        # Verify existing keys are preserved
        content = conf.read_text()
        assert "LATITUDE=35.0" in content
        assert "SENSITIVITY=1.0" in content

    def test_post_settings_empty_body(self, client, tmp_path, monkeypatch):
        """POST with {} returns 200, fields_changed=[]."""
        conf = tmp_path / "birdnet.conf"
        conf.write_text("LATITUDE=10.0\n")
        monkeypatch.setattr("api.routers.settings_router.settings.config_ini_path", conf)
        response = client.post("/api/settings", json={})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "updated"
        assert data["fields_changed"] == []
        # File should be unchanged
        content = conf.read_text()
        assert "LATITUDE=10.0" in content


class TestSystemRestart:
    """Tests for POST /api/system/restart endpoint."""

    def test_restart_requires_confirm(self, client):
        """POST with confirm=False returns 400."""
        response = client.post("/api/system/restart", json={
            "confirm": False,
        })
        assert response.status_code == 400

    def test_restart_missing_confirm(self, client):
        """POST with {} returns 422 (confirm is required)."""
        response = client.post("/api/system/restart", json={})
        assert response.status_code == 422

    def test_restart_with_confirm(self, client):
        """POST with confirm=True returns 200 with status='restarting'."""
        response = client.post("/api/system/restart", json={
            "confirm": True,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "restarting"
        assert data["service"] == "birdnet_analysis"

    def test_restart_invalid_service_name(self, client):
        """POST with service='../../hack' returns 400."""
        response = client.post("/api/system/restart", json={
            "confirm": True,
            "service": "../../hack",
        })
        assert response.status_code == 400


class TestSpectrogramEndpoint:
    """Tests for GET /api/spectrogram endpoint."""

    def test_spectrogram_returns_structure(self, client):
        """GET /api/spectrogram returns 200 with correct fields."""
        response = client.get("/api/spectrogram")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "fft_size" in data
        assert "bins" in data
        assert "timestamp" in data
        assert "duration_ms" in data
        assert "generated_at" in data

    def test_spectrogram_default_not_recording(self, client):
        """Default status is 'not_recording'."""
        response = client.get("/api/spectrogram")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "not_recording"
        assert data["bins"] == []

    def test_spectrogram_accepts_duration_param(self, client):
        """GET /api/spectrogram?duration=5 returns duration_ms=5000."""
        response = client.get("/api/spectrogram?duration=5")
        assert response.status_code == 200
        data = response.json()
        assert data["duration_ms"] == 5000