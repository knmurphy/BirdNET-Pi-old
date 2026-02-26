"""Pydantic models for classifier endpoints."""

from pydantic import BaseModel
from typing import Optional


class ClassifierConfig(BaseModel):
    """Configuration for a classifier."""

    id: str
    name: str
    enabled: bool
    model_path: Optional[str] = None
    labels_path: Optional[str] = None
    confidence_threshold: float = 0.8
    overlap: float = 0.0
    sensitivity: float = 1.0


class ClassifierToggleResponse(BaseModel):
    """Response for toggling a classifier."""

    id: str
    enabled: bool
    message: str
