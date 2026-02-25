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