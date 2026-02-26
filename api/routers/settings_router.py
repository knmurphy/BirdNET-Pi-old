"""Settings API endpoints."""

import configparser
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
    """Parse birdnet.conf and return settings dict."""
    config = configparser.ConfigParser()
    config_path = settings.config_ini_path

    if not config_path.exists():
        # Return defaults if config doesn't exist
        return {
            "latitude": 0.0,
            "longitude": 0.0,
            "confidence_threshold": 0.8,
            "overlap": 0.0,
            "sensitivity": 1.0,
            "week": -1,
        }

    try:
        config.read(config_path)

        # Extract values from [BIRDNET] section
        birdnet = config.get("BIRDNET", {})

        return {
            "latitude": float(birdnet.get("LATITUDE", 0.0)),
            "longitude": float(birdnet.get("LONGITUDE", 0.0)),
            "confidence_threshold": float(birdnet.get("CONFIDENCE", 0.8)),
            "overlap": float(birdnet.get("OVERLAP", 0.0)),
            "sensitivity": float(birdnet.get("SENSITIVITY", 1.0)),
            "week": int(birdnet.get("WEEK", -1)),
        }
    except Exception:
        # Return defaults on parse error
        return {
            "latitude": 0.0,
            "longitude": 0.0,
            "confidence_threshold": 0.8,
            "overlap": 0.0,
            "sensitivity": 1.0,
            "week": -1,
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
