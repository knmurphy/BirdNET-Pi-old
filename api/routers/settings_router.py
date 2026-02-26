"""Settings API endpoints."""

from datetime import datetime
from typing import Any, Optional

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



class SettingsUpdateRequest(BaseModel):
    """Request body for POST /api/settings."""

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    confidence_threshold: Optional[float] = None
    overlap: Optional[float] = None
    sensitivity: Optional[float] = None
    week: Optional[int] = None


class SettingsUpdateResponse(BaseModel):
    """Response for POST /api/settings."""

    status: str
    fields_changed: list[str]


# Mapping from pydantic field name to birdnet.conf key
_FIELD_TO_CONFIG_KEY: dict[str, str] = {
    "latitude": "LATITUDE",
    "longitude": "LONGITUDE",
    "confidence_threshold": "SF_THRESH",
    "overlap": "OVERLAP",
    "sensitivity": "SENSITIVITY",
    "week": "WEEK",
}


def write_config_values(updates: dict[str, str]) -> None:
    """Write key-value pairs to birdnet.conf, preserving existing content.

    For each KEY=VALUE line where KEY is in updates, replaces the value.
    Keys in updates not found in the file are appended at the end.
    If the file doesn't exist, creates it with the given values.
    Comments and non-KEY=VALUE lines are preserved as-is.
    """
    config_path = settings.config_ini_path

    if not updates:
        return

    remaining = dict(updates)  # keys we still need to write
    lines: list[str] = []

    if config_path.exists():
        with open(config_path, "r") as f:
            for line in f:
                raw = line.rstrip("\n")
                stripped = raw.strip()
                # Check if this is a KEY=VALUE line whose key we need to update
                if stripped and not stripped.startswith("#") and "=" in stripped:
                    key, _, _ = stripped.partition("=")
                    key = key.strip()
                    if key in remaining:
                        lines.append(f"{key}={remaining.pop(key)}")
                        continue
                lines.append(raw)

    # Append any keys that weren't already in the file
    for key, value in remaining.items():
        lines.append(f"{key}={value}")

    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as f:
        f.write("\n".join(lines))
        if lines:
            f.write("\n")


@router.post("/settings", response_model=SettingsUpdateResponse)
async def update_settings(body: SettingsUpdateRequest):
    """Update BirdNET-Pi settings in config file."""
    # Build config updates from non-None fields
    config_updates: dict[str, str] = {}
    fields_changed: list[str] = []

    for field_name, config_key in _FIELD_TO_CONFIG_KEY.items():
        value = getattr(body, field_name)
        if value is not None:
            config_updates[config_key] = str(value)
            fields_changed.append(field_name)

    write_config_values(config_updates)

    return SettingsUpdateResponse(status="updated", fields_changed=fields_changed)