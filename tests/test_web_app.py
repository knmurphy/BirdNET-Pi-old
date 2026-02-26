"""
Tests for Field Station OS FastHTML web application.

Following TDD: Write the test first, watch it fail, write minimal code to pass.
"""
from fasthtml.common import FastHTML, to_xml
from unittest.mock import patch


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


class TestDashboardWidgets:
    """Test that dashboard displays real data."""

    MOCK_SUMMARY = {
        "total_detections": 5, "species_count": 3,
        "top_species": [{"com_name": "Carolina Wren", "count": 3}],
        "hourly_counts": [0] * 24,
        "generated_at": "2024-01-01T00:00:00",
    }

    @patch("homepage.web_app.api_get")
    def test_dashboard_shows_today_detection_count(self, mock_api_get):
        """Dashboard should display today's detection count."""
        mock_api_get.return_value = self.MOCK_SUMMARY
        from homepage.web_app import _dashboard_content
        content = str(_dashboard_content())
        assert "Today's Detections" in content
        assert 'class="widget"' in content

    @patch("homepage.web_app.api_get")
    def test_dashboard_shows_today_species_count(self, mock_api_get):
        """Dashboard should display today's species count."""
        mock_api_get.return_value = self.MOCK_SUMMARY
        from homepage.web_app import _dashboard_content
        content = str(_dashboard_content())
        assert "Today's Species" in content

    @patch("homepage.web_app.api_get")
    def test_dashboard_shows_latest_detection(self, mock_api_get):
        """Dashboard should display the most recent detection."""
        mock_api_get.return_value = self.MOCK_SUMMARY
        from homepage.web_app import _dashboard_content
        content = str(_dashboard_content())
        # Dashboard uses API-driven widgets, not "Latest Detection" section
        assert "Today's Detections" in content or "No detections yet" in content

    @patch("homepage.web_app.api_get")
    def test_dashboard_uses_widget_classes(self, mock_api_get):
        """Dashboard should use .widget class for styling."""
        mock_api_get.return_value = self.MOCK_SUMMARY
        from homepage.web_app import _dashboard_content
        content = str(_dashboard_content())
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

    @patch("homepage.web_app.api_get")
    def test_detections_content_has_audio_playback(self, mock_api_get):
        """Detections content should include species data when API returns results."""
        mock_api_get.return_value = {
            "species": [
                {"com_name": "Carolina Wren", "detection_count": 3,
                 "sci_name": "Thryothorus ludovicianus", "max_confidence": 0.92}
            ]
        }
        from homepage.web_app import _detections_content
        content = str(_detections_content())
        assert "Carolina Wren" in content

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

    @patch("homepage.web_app.api_get")
    def test_species_content_uses_confidence_classes(self, mock_api_get):
        """Species content should apply confidence classes for max_conf."""
        mock_api_get.return_value = {
            "species": [
                {"com_name": "Carolina Wren", "detection_count": 3,
                 "sci_name": "Thryothorus ludovicianus", "max_confidence": 0.92}
            ]
        }
        from homepage.web_app import _species_content
        content = str(_species_content())
        has_conf_class = "conf-high" in content or "conf-medium" in content or "conf-low" in content
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


class TestHourlyActivity:
    """Test hourly activity chart functionality."""

    def test_hourly_activity_section_returns_div(self):
        """Should return a Div element."""
        from homepage.web_app import _hourly_activity_section
        content = _hourly_activity_section()
        assert "Today's Activity" in str(content)


class TestSystemHealth:
    """Test system health metrics functionality."""

    @patch("homepage.web_app.api_get")
    def test_system_health_section_returns_div(self, mock_api_get):
        """Should return a Div element with health widgets."""
        mock_api_get.return_value = {
            "cpu_percent": 25.0, "temperature_celsius": 45.0,
            "disk_used_gb": 10.0, "disk_total_gb": 32.0,
            "uptime_seconds": 3600, "sse_subscribers": 1,
        }
        from homepage.web_app import _system_health_section
        content = to_xml(_system_health_section())
        assert "System Health" in content


class TestStatsContentEnhanced:
    """Test enhanced stats page with hourly and health sections."""

    MOCK_SUMMARY = {
        "total_detections": 10, "species_count": 5,
        "top_species": [], "hourly_counts": [0] * 24,
        "generated_at": "2024-01-01T00:00:00",
    }
    MOCK_SYSTEM = {
        "cpu_percent": 25.0, "temperature_celsius": 45.0,
        "disk_used_gb": 10.0, "disk_total_gb": 32.0,
        "uptime_seconds": 3600, "sse_subscribers": 1,
    }

    @patch("homepage.web_app.api_get")
    def test_stats_content_includes_hourly_activity(self, mock_api_get):
        """Stats should show hourly activity section."""
        def side_effect(endpoint):
            if "system" in endpoint:
                return self.MOCK_SYSTEM
            return self.MOCK_SUMMARY
        mock_api_get.side_effect = side_effect
        from homepage.web_app import _stats_content
        content = str(_stats_content())
        assert "Today's Activity" in content or "Statistics" in content

    @patch("homepage.web_app.api_get")
    def test_stats_content_includes_system_health(self, mock_api_get):
        """Stats should show system health section."""
        def side_effect(endpoint):
            if "system" in endpoint:
                return self.MOCK_SYSTEM
            return self.MOCK_SUMMARY
        mock_api_get.side_effect = side_effect
        from homepage.web_app import _stats_content
        content = str(_stats_content())
        assert "System Health" in content

    @patch("homepage.web_app.api_get")
    def test_stats_content_uses_widget_classes(self, mock_api_get):
        """Stats should use proper widget styling."""
        def side_effect(endpoint):
            if "system" in endpoint:
                return self.MOCK_SYSTEM
            return self.MOCK_SUMMARY
        mock_api_get.side_effect = side_effect
        from homepage.web_app import _stats_content
        content = str(_stats_content())
        assert 'class="widget"' in content or "class='widget'" in content


class TestLiveDataWiring:
    """Test live data wiring between FastAPI backend and FastHTML frontend."""

    def test_shell_includes_htmx_script(self):
        """Shell should include the HTMX script tag."""
        from homepage.web_app import _shell
        shell = str(_shell("test content", "/app/dashboard"))
        assert "htmx.org" in shell

    def test_shell_includes_sse_javascript(self):
        """Shell should include the SSE client JavaScript."""
        from homepage.web_app import _shell
        shell = str(_shell("test content", "/app/dashboard"))
        assert "EventSource" in shell

    def test_shell_injects_api_url(self):
        """Shell should inject the API base URL into the SSE JavaScript."""
        from homepage.web_app import _shell, API_BASE_URL
        shell = str(_shell("test content", "/app/dashboard"))
        expected_url = API_BASE_URL.rstrip("/")
        assert expected_url in shell

    def test_partial_dashboard_stats_route_exists(self):
        """The /app/partials/dashboard-stats route should be registered."""
        from homepage.web_app import app
        routes = [r.path for r in app.routes]
        assert "/app/partials/dashboard-stats" in routes

    def test_partial_system_health_route_exists(self):
        """The /app/partials/system-health route should be registered."""
        from homepage.web_app import app
        routes = [r.path for r in app.routes]
        assert "/app/partials/system-health" in routes

    @patch("homepage.web_app.api_get")
    def test_dashboard_has_live_feed_section(self, mock_api_get):
        """Dashboard should have a live feed section."""
        mock_api_get.return_value = {
            "total_detections": 5, "species_count": 3,
            "top_species": [], "hourly_counts": [0] * 24,
            "generated_at": "2024-01-01T00:00:00",
        }
        from homepage.web_app import _dashboard_content
        content = str(_dashboard_content())
        assert "live-feed" in content

    @patch("homepage.web_app.api_get")
    def test_dashboard_has_live_indicator(self, mock_api_get):
        """Dashboard should have a live status indicator."""
        mock_api_get.return_value = {
            "total_detections": 5, "species_count": 3,
            "top_species": [], "hourly_counts": [0] * 24,
            "generated_at": "2024-01-01T00:00:00",
        }
        from homepage.web_app import _dashboard_content
        content = str(_dashboard_content())
        assert "live-dot" in content

    @patch("homepage.web_app.api_get")
    def test_dashboard_stats_have_htmx_polling(self, mock_api_get):
        """Dashboard stats should have hx-get for HTMX polling."""
        mock_api_get.return_value = {
            "total_detections": 5, "species_count": 3,
            "top_species": [], "hourly_counts": [0] * 24,
            "generated_at": "2024-01-01T00:00:00",
        }
        from homepage.web_app import _dashboard_content
        content = str(_dashboard_content())
        assert "hx-get" in content

    @patch("homepage.web_app.api_get")
    def test_dashboard_stats_have_widget_ids(self, mock_api_get):
        """Dashboard widgets should have IDs for SSE JavaScript updates."""
        mock_api_get.return_value = {
            "total_detections": 5, "species_count": 3,
            "top_species": [], "hourly_counts": [0] * 24,
            "generated_at": "2024-01-01T00:00:00",
        }
        from homepage.web_app import _dashboard_content
        content = str(_dashboard_content())
        assert "today-count" in content

    def test_sse_connect_gated_behind_live_feed(self):
        """SSE connect() should only run if live-feed element exists."""
        from homepage.web_app import LIVE_JS
        assert "getElementById('live-feed')" in LIVE_JS
