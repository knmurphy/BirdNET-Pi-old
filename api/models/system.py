"""Pydantic models for system endpoints."""

from pydantic import BaseModel


class SystemResponse(BaseModel):
    """Response for /api/system."""

    cpu_percent: float
    temperature_celsius: float
    disk_used_gb: float
    disk_total_gb: float
    uptime_seconds: float
    active_classifiers: list[str]
    sse_subscribers: int
    generated_at: str
