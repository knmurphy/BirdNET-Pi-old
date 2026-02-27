"""Tests for system_info utilities."""

import pytest
from unittest.mock import MagicMock, patch

from api.services.system_info import (
    celsius_to_fahrenheit,
    get_memory_percent,
)


class TestCelsiusToFahrenheit:
    """Tests for celsius_to_fahrenheit conversion function."""

    def test_celsius_to_fahrenheit_freezing(self):
        """Test 0°C = 32°F (freezing point)"""
        result = celsius_to_fahrenheit(0)
        assert result == 32

    def test_celsius_to_fahrenheit_boiling(self):
        """Test 100°C = 212°F (boiling point)"""
        result = celsius_to_fahrenheit(100)
        assert result == 212

    def test_celsius_to_fahrenheit_negative(self):
        """Test negative temperature (-40°C = -40°F)"""
        result = celsius_to_fahrenheit(-40)
        assert result == -40

    def test_celsius_to_fahrenheit_decimal(self):
        """Test decimal precision"""
        result = celsius_to_fahrenheit(37.5)
        assert result == 99.5


class TestGetMemoryPercent:
    """Tests for get_memory_percent function."""

    @patch("api.services.system_info.psutil.virtual_memory")
    def test_get_memory_percent_valid_range(self, mock_virtual_memory):
        """Test that memory percent returns valid range"""
        mock_memory = MagicMock()
        mock_memory.percent = 45.5
        mock_virtual_memory.return_value = mock_memory

        result = get_memory_percent()
        assert 0 <= result <= 100
        assert isinstance(result, float)
        assert result == 45.5

    @patch("api.services.system_info.psutil.virtual_memory")
    def test_get_memory_percent_zero(self, mock_virtual_memory):
        """Test memory percent returns 0 when no memory used"""
        mock_memory = MagicMock()
        mock_memory.percent = 0.0
        mock_virtual_memory.return_value = mock_memory

        result = get_memory_percent()
        assert result == 0.0

    @patch("api.services.system_info.psutil.virtual_memory")
    def test_get_memory_percent_full(self, mock_virtual_memory):
        """Test memory percent returns 100 when memory full"""
        mock_memory = MagicMock()
        mock_memory.percent = 100.0
        mock_virtual_memory.return_value = mock_memory

        result = get_memory_percent()
        assert result == 100.0
