"""Pydantic models for detection endpoints."""

from pydantic import BaseModel
from typing import Optional


class Detection(BaseModel):
    """Single detection record."""

    id: int
    date: str
    time: str
    iso8601: Optional[str] = None
    com_name: str
    sci_name: str
    confidence: float
    file_name: Optional[str] = None
    classifier: str = "birdnet"
    lat: Optional[float] = None
    lon: Optional[float] = None
    cutoff: Optional[float] = None
    week: Optional[int] = None
    sens: Optional[float] = None
    overlap: Optional[float] = None


class TopSpecies(BaseModel):
    """Top species entry for today summary."""

    com_name: str
    count: int


class TodaySummaryResponse(BaseModel):
    """Response for /api/detections/today/summary."""

    total_detections: int
    species_count: int
    top_species: list[TopSpecies]
    hourly_counts: list[int]  # 24-element array
    generated_at: str
