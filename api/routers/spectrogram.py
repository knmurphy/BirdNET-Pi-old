"""Spectrogram data API endpoint.

NOTE: This is a stub. The actual spectrogram data format will be determined
during the design/prototype phase based on the Unknown Pleasures WebGL
reference implementation (github.com/knmurphy/spectrogram-unknown).
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()


class SpectrogramResponse(BaseModel):
    """Spectrogram data response.

    Format is preliminary — will evolve based on Unknown Pleasures
    WebGL implementation requirements.
    """

    status: str  # "available" or "not_recording"
    sample_rate: Optional[int] = None
    fft_size: int = 2048
    bins: list[list[float]] = []  # Time-frequency bins (rows=time, cols=freq)
    timestamp: str  # ISO datetime of the audio segment
    duration_ms: int = 0
    generated_at: str


@router.get("/spectrogram", response_model=SpectrogramResponse)
async def get_spectrogram(
    duration: int = Query(3, ge=1, le=30, description="Seconds of audio to analyze"),
):
    """Get spectrogram data for current audio segment.

    NOTE: This is a stub endpoint returning empty data. The actual
    implementation will provide FFT bins from the live audio stream
    once the WebGL frontend is ready.
    """
    return SpectrogramResponse(
        status="not_recording",
        fft_size=2048,
        bins=[],
        timestamp=datetime.now().isoformat(),
        duration_ms=duration * 1000,
        generated_at=datetime.now().isoformat(),
    )
