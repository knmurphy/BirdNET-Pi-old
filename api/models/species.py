"""Pydantic models for species endpoints."""

from pydantic import BaseModel
from typing import Optional


class SpeciesSummary(BaseModel):
    """Summary for a single species detected today."""

    com_name: str
    sci_name: str
    detection_count: int
    max_confidence: float
    last_seen: str  # "HH:MM:SS"
    hourly_counts: list[int]  # 24-element array
    is_new: bool  # First detection was within last 2 hours


class SpeciesTodayResponse(BaseModel):
    """Response for /api/species/today."""

    species: list[SpeciesSummary]
    generated_at: str


class SpeciesStats(BaseModel):
    """Full stats for a single species."""

    com_name: str
    sci_name: str
    detection_count: int
    max_confidence: float
    best_date: str  # "YYYY-MM-DD"
    best_time: str  # "HH:MM:SS"
    best_file_name: str  # Relative path to best audio file


class SpeciesStatsResponse(BaseModel):
    """Response for /api/species/stats."""

    species: list[SpeciesStats]
    total_species: int
    generated_at: str
