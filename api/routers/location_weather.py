"""Location and weather API - city name from reverse geocode, weather from Open-Meteo."""

import time
from typing import Optional

import httpx
from fastapi import APIRouter
from pydantic import BaseModel

from api.config import settings
from api.routers.settings_router import parse_config_ini

router = APIRouter()

# In-memory cache: (lat, lon) -> (result, expiry_timestamp)
_CACHE: dict[tuple[float, float], tuple[dict, float]] = {}
_CACHE_TTL = 30 * 60  # 30 minutes


def _weather_code_to_condition(code: int) -> str:
    """Map WMO weather code to short condition string."""
    if code in (0, 1):
        return "Clear"
    if code in (2, 3):
        return "Cloudy"
    if 45 <= code <= 48:
        return "Fog"
    if 51 <= code <= 67:
        return "Rain"
    if 71 <= code <= 77:
        return "Snow"
    if 80 <= code <= 82:
        return "Showers"
    if 85 <= code <= 86:
        return "Snow showers"
    if 95 <= code <= 99:
        return "Thunderstorm"
    return "Cloudy"


class LocationWeatherResponse(BaseModel):
    """Response for /api/location-weather."""

    city: str
    temp_c: float
    condition: str
    latitude: float
    longitude: float


async def _fetch_nominatim(lat: float, lon: float) -> Optional[str]:
    """Reverse geocode lat/lon to city name via Nominatim."""
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {"lat": lat, "lon": lon, "format": "json", "zoom": 10}
    headers = {"User-Agent": "BirdNET-Pi-FieldStation/1.0"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, params=params, headers=headers)
        if resp.status_code != 200:
            return None
        data = resp.json()
        addr = data.get("address", {})
        return addr.get("city") or addr.get("town") or addr.get("village") or addr.get("municipality") or data.get("name")


async def _fetch_open_meteo(lat: float, lon: float) -> tuple[float, int]:
    """Fetch current temp and weather code from Open-Meteo."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": lat, "longitude": lon, "current": "temperature_2m,weather_code"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, params=params)
        if resp.status_code != 200:
            return 0.0, 0
        data = resp.json()
        cur = data.get("current", {})
        return cur.get("temperature_2m", 0.0), cur.get("weather_code", 0)


@router.get("/location-weather", response_model=LocationWeatherResponse)
async def get_location_weather():
    """Get city name (reverse geocode) and current weather for station location."""
    config = parse_config_ini()
    lat = config["latitude"]
    lon = config["longitude"]

    if lat == 0.0 and lon == 0.0:
        return LocationWeatherResponse(
            city="Unknown",
            temp_c=0.0,
            condition="—",
            latitude=0.0,
            longitude=0.0,
        )

    cache_key = (round(lat, 4), round(lon, 4))
    now = time.time()
    if cache_key in _CACHE:
        cached, expiry = _CACHE[cache_key]
        if now < expiry:
            return LocationWeatherResponse(**cached)

    city = await _fetch_nominatim(lat, lon) or "Unknown"
    temp_c, weather_code = await _fetch_open_meteo(lat, lon)
    condition = _weather_code_to_condition(weather_code)

    result = {
        "city": city,
        "temp_c": temp_c,
        "condition": condition,
        "latitude": lat,
        "longitude": lon,
    }
    _CACHE[cache_key] = (result, now + _CACHE_TTL)

    return LocationWeatherResponse(**result)
