"""Pydantic models for species endpoints."""

from pydantic import BaseModel


class SpeciesSummary(BaseModel):
    """Summary for a single species detected today."""

    com_name: str
    sci_name: str
    detection_count: int
    max_confidence: float
    last_seen: str  # "HH:MM:SS"
    hourly_counts: list[int]  # 24-element array


class SpeciesTodayResponse(BaseModel):
    """Response for /api/species/today."""

    species: list[SpeciesSummary]
    generated_at: str
