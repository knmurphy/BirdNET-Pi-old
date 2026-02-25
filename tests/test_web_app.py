"""
Tests for Field Station OS FastHTML web application.

Following TDD: Write the test first, watch it fail, write minimal code to pass.
"""
import pytest
from fasthtml.common import FastHTML


class TestAppCreation:
    """Test that the FastHTML app can be created and configured."""
    
    def test_app_exists(self):
        """The FastHTML app should be creatable."""
        from homepage.web_app import app
        assert app is not None
    
    def test_app_is_fasthtml_instance(self):
        """The app should be a FastHTML instance."""
        from homepage.web_app import app
        assert isinstance(app, FastHTML)


class TestDashboardRoute:
    """Test the dashboard route."""
    
    def test_dashboard_route_exists(self):
        """The /app/dashboard route should be registered."""
        from homepage.web_app import app
        # Check that the route is registered
        routes = [r.path for r in app.routes]
        assert "/app/dashboard" in routes


class TestDashboardContent:
    """Test dashboard content generation."""
    
    def test_dashboard_returns_html_with_title(self):
        """Dashboard should return HTML containing the site title."""
        from homepage.web_app import _dashboard_content
        content = _dashboard_content()
        # The content should contain "Dashboard" heading
        assert "Dashboard" in str(content)


class TestDatabase:
    """Test database connectivity and queries."""
    
    def test_get_today_detection_count(self):
        """Should be able to query today's detection count from database."""
        from homepage.web_app import get_today_detection_count
        count = get_today_detection_count()
        assert isinstance(count, int)
        assert count >= 0
    
    def test_get_today_species_count(self):
        """Should query count of distinct species detected today."""
        from homepage.web_app import get_today_species_count
        count = get_today_species_count()
        assert isinstance(count, int)
        assert count >= 0


class TestDashboardWidgets:
    """Test that dashboard displays real data."""

    def test_dashboard_shows_today_detection_count(self):
        """Dashboard should display today's detection count."""
        from homepage.web_app import _dashboard_content
        content = str(_dashboard_content())
        # Dashboard should show detection count
        assert "Detections" in content or "detections" in content


    def test_dashboard_shows_today_species_count(self):
        """Dashboard should display today's species count."""
        from homepage.web_app import _dashboard_content
        content = str(_dashboard_content())
        # Dashboard should show species count
        assert "Species" in content


    def test_dashboard_shows_latest_detection(self):
        """Dashboard should display the most recent detection."""
        from homepage.web_app import _dashboard_content
        content = str(_dashboard_content())
        # Should show latest detection section
        assert "Latest" in content or "latest" in content


class TestNavigationShell:
    """Test the navigation shell structure."""

    def test_shell_has_header_with_title(self):
        """Shell should have a header with station title."""
        from homepage.web_app import _shell
        shell = str(_shell("test content", "/app/dashboard"))
        assert "Field Station" in shell or "Station" in shell

    def test_shell_has_bottom_tabs(self):
        """Shell should have bottom navigation with tabs."""
        from homepage.web_app import _shell
        shell = str(_shell("test content", "/app/dashboard"))
        # Should have navigation tabs
        assert "Dashboard" in shell


class TestDetectionsRoute:
    """Test the detections route."""

    def test_detections_route_exists(self):
        """The /app/detections route should be registered."""
        from homepage.web_app import app
        routes = [r.path for r in app.routes]
        assert "/app/detections" in routes

    def test_detections_content_shows_species(self):
        """Detections content should show species names."""
        from homepage.web_app import _detections_content
        content = str(_detections_content())
        # Should contain detections header
        assert "Detection" in content


class TestSpeciesRoute:
    """Test the species route."""

    def test_species_route_exists(self):
        """The /app/species route should be registered."""
        from homepage.web_app import app
        routes = [r.path for r in app.routes]
        assert "/app/species" in routes

    def test_species_content_shows_species(self):
        """Species content should show species information."""
        from homepage.web_app import _species_content
        content = str(_species_content())
        assert "Species" in content



class TestStatsRoute:
    """Test the stats route."""

    def test_stats_route_exists(self):
        """The /app/stats route should be registered."""
        from homepage.web_app import app
        routes = [r.path for r in app.routes]
        assert "/app/stats" in routes

    def test_stats_content_shows_stats(self):
        """Stats content should show statistics."""
        from homepage.web_app import _stats_content
        content = str(_stats_content())
        assert "Stat" in content or "stat" in content


class TestSettingsRoute:
    """Test the settings route."""

    def test_settings_route_exists(self):
        """The /app/settings route should be registered."""
        from homepage.web_app import app
        routes = [r.path for r in app.routes]
        assert "/app/settings" in routes

    def test_settings_content_shows_settings(self):
        """Settings content should show settings information."""
        from homepage.web_app import _settings_content
        content = str(_settings_content())
        assert "Setting" in content or "setting" in content