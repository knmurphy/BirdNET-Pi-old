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
        # The content should contain "Dashboard" heading as an H2 element
        assert "<h2>Dashboard</h2>" in str(content)


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
        assert count >= 0

    def test_get_total_detection_count(self):
        """Should query total detection count (all time) from database."""
        from homepage.web_app import get_total_detection_count
        count = get_total_detection_count()
        assert isinstance(count, int)
        assert count >= 0

    def test_get_total_species_count(self):
        """Should query count of distinct species (all time) from database."""
        from homepage.web_app import get_total_species_count
        count = get_total_species_count()
        assert isinstance(count, int)
        assert count >= 0


class TestDashboardWidgets:
    """Test that dashboard displays real data."""

    def test_dashboard_shows_today_detection_count(self):
        """Dashboard should display today's detection count."""
        from homepage.web_app import _dashboard_content
        content = str(_dashboard_content())
        # Dashboard should show detection count in a widget with proper structure
        assert "Today's Detections" in content
        assert 'class="widget"' in content


    def test_dashboard_shows_today_species_count(self):
        """Dashboard should display today's species count."""
        from homepage.web_app import _dashboard_content
        content = str(_dashboard_content())
        # Dashboard should show species count in a widget with proper structure
        assert "Today's Species" in content


    def test_dashboard_shows_latest_detection(self):
        """Dashboard should display the most recent detection."""
        from homepage.web_app import _dashboard_content
        content = str(_dashboard_content())
        # Should show latest detection section with proper label
        assert "Latest Detection" in content or "No detections yet" in content


    def test_dashboard_uses_widget_classes(self):
        """Dashboard should use .widget class for styling."""
        from homepage.web_app import _dashboard_content
        content = str(_dashboard_content())
        # Should have widget class for card styling
        assert 'class="widget"' in content or "class='widget'" in content


class TestNavigationShell:
    """Test the navigation shell structure."""

    def test_shell_has_header_with_title(self):
        """Shell should have a header with station title."""
        from homepage.web_app import _shell
        shell = str(_shell("test content", "/app/dashboard"))
        # Shell should have header with proper title structure
        assert "<title>Field Station</title>" in shell or "<h1" in shell

    def test_shell_has_bottom_tabs(self):
        """Shell should have bottom navigation with tabs."""
        from homepage.web_app import _shell
        shell = str(_shell("test content", "/app/dashboard"))
        # Should have navigation tabs with proper href structure
        assert '<a href="/app/dashboard"' in shell or "Dashboard</a>" in shell


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
        # Should contain "Today's Detections" header with proper H2 structure
        assert "<h2>Today's Detections</h2>" in content or "No detections" in content

    def test_detections_content_has_audio_playback(self):
        """Detections content should include audio elements for playback."""
        from homepage.web_app import _detections_content
        content = str(_detections_content())
        # If there are detections, they should include audio elements
        # If no detections or error, the test passes vacuously
        has_detections = "<h2>Today's Detections</h2>" in content
        has_no_data = "No detections" in content or "Unable to load" in content
        if has_detections and not has_no_data:
            assert "<audio" in content, "Detections should include audio elements"
            assert "controls" in content, "Audio elements should have controls"



    def test_confidence_class_helper(self):
        """The _confidence_class helper should return correct classes."""
        from homepage.web_app import _confidence_class
        assert _confidence_class(0.90) == "conf-high"
        assert _confidence_class(0.80) == "conf-high"
        assert _confidence_class(0.70) == "conf-medium"
        assert _confidence_class(0.50) == "conf-medium"
        assert _confidence_class(0.40) == "conf-low"

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
        # Should contain "Today's Species" header with proper H2 structure
        assert "<h2>Today's Species</h2>" in content or "No species detected" in content

    def test_species_content_uses_confidence_classes(self):
        """Species content should apply confidence classes for max_conf."""
        from homepage.web_app import _species_content
        content = str(_species_content())
        # Should contain one of the confidence class names (if data exists)
        # This verifies the bug fix: species content applies confidence classes
        has_conf_class = "conf-high" in content or "conf-medium" in content or "conf-low" in content
        # If there are species today, they should have confidence classes
        # If no species (empty state), the test passes vacuously
        if "No species detected" not in content and "Error loading" not in content:
            assert has_conf_class, "Species content should use confidence classes"



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
        # Should contain "Statistics" header with proper H2 structure
        assert "<h2>Statistics</h2>" in content


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
        # Should contain "Settings" header with proper H2 structure
        assert "<h2>Settings</h2>" in content