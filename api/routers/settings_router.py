"""Settings API endpoints."""

from datetime import datetime
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from api.config import settings

router = APIRouter()


class SettingsResponse(BaseModel):
    """Response for /api/settings."""

    # Audio settings
    audio_path: str
    
    # Location
    latitude: float
    longitude: float
    
    # Model settings
    confidence_threshold: float
    overlap: float
    sensitivity: float
    
    # Processing
    week: int  # -1 for auto
    
    # Server info
    generated_at: str


def parse_config_ini() -> dict[str, Any]:
    """Parse birdnet.conf (shell script KEY=VALUE format) and return settings dict.

    The birdnet.conf file uses shell script format (KEY=VALUE), not INI format.
    This parser reads line by line and extracts key-value pairs.
    """
    config_path = settings.config_ini_path

    # Default values
    defaults = {
        "latitude": 0.0,
        "longitude": 0.0,
        "confidence_threshold": 0.8,
        "overlap": 0.0,
        "sensitivity": 1.0,
        "week": -1,
    }

    if not config_path.exists():
        return defaults

    # Parse shell script format: KEY=VALUE
    config_values: dict[str, str] = {}
    try:
        with open(config_path, "r") as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue
                # Parse KEY=VALUE
                if "=" in line:
                    key, _, value = line.partition("=")
                    config_values[key.strip()] = value.strip().strip('"').strip("'")
    except Exception:
        return defaults

    # Map config keys to response fields with type conversion
    def get_float(key: str, default: float) -> float:
        try:
            return float(config_values.get(key, default))
        except (ValueError, TypeError):
            return default

    def get_int(key: str, default: int) -> int:
        try:
            return int(config_values.get(key, default))
        except (ValueError, TypeError):
            return default

    return {
        "latitude": get_float("LATITUDE", defaults["latitude"]),
        "longitude": get_float("LONGITUDE", defaults["longitude"]),
        "confidence_threshold": get_float("SF_THRESH", defaults["confidence_threshold"]),
        "overlap": get_float("OVERLAP", defaults["overlap"]),
        "sensitivity": get_float("SENSITIVITY", defaults["sensitivity"]),
        "week": get_int("WEEK", defaults["week"]),
    }


@router.get("/settings", response_model=SettingsResponse)
async def get_settings():
    """Get current BirdNET-Pi settings from config file."""
    config_values = parse_config_ini()
    
    return SettingsResponse(
        audio_path=str(settings.audio_base_path),
        latitude=config_values["latitude"],
        longitude=config_values["longitude"],
        confidence_threshold=config_values["confidence_threshold"],
        overlap=config_values["overlap"],
        sensitivity=config_values["sensitivity"],
        week=config_values["week"],
        generated_at=datetime.now().isoformat(),
    )
