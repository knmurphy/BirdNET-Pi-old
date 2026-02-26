"""Audio endpoints: device listing and file serving."""

import subprocess
import re
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette.responses import FileResponse

from api.config import settings

router = APIRouter()


class AudioDevice(BaseModel):
    """An ALSA capture device."""

    id: str
    name: str
    card: int
    device: int


class AudioDevicesResponse(BaseModel):
    """Response for audio devices listing."""

    devices: list[AudioDevice]


def _parse_arecord_output(output: str) -> list[AudioDevice]:
    """Parse `arecord -l` output into AudioDevice list.

    Example line:
        card 1: Device [USB Audio Device], device 0: USB Audio [USB Audio]
    """
    devices: list[AudioDevice] = []
    pattern = re.compile(
        r"^card\s+(\d+):\s+\S+\s+\[(.+?)\],\s+device\s+(\d+):"
    )
    for line in output.splitlines():
        m = pattern.match(line)
        if m:
            card_num = int(m.group(1))
            name = m.group(2).strip()
            device_num = int(m.group(3))
            devices.append(
                AudioDevice(
                    id=f"hw:{card_num},{device_num}",
                    name=name,
                    card=card_num,
                    device=device_num,
                )
            )
    return devices


@router.get("/audio/devices", response_model=AudioDevicesResponse)
async def list_audio_devices():
    """List available ALSA capture (input) devices.

    Returns an empty list on non-Linux systems or when arecord is unavailable.
    """
    try:
        result = subprocess.run(
            ["arecord", "-l"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        devices = _parse_arecord_output(result.stdout)
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        devices = []
    return AudioDevicesResponse(devices=devices)


@router.get("/audio/{path:path}")
async def serve_audio_file(path: str):
    """Serve an audio file from the configured audio base path.

    The path is relative to settings.audio_base_path (e.g. 2026-02-25/birdnet/clip.wav).
    """
    # Reject obvious traversal attempts before resolving
    if ".." in path.split("/"):
        raise HTTPException(status_code=400, detail="Path traversal not allowed")

    base = settings.audio_base_path.resolve()
    requested = (base / path).resolve()

    # Verify resolved path is under base (catches symlink escapes too)
    if not str(requested).startswith(str(base) + "/") and requested != base:
        raise HTTPException(status_code=400, detail="Path traversal not allowed")

    if not requested.is_file():
        raise HTTPException(status_code=404, detail="Audio file not found")

    # Guess media type from suffix, default to audio/wav
    suffix = requested.suffix.lower()
    media_types = {
        ".wav": "audio/wav",
        ".mp3": "audio/mpeg",
        ".ogg": "audio/ogg",
        ".flac": "audio/flac",
    }
    media_type = media_types.get(suffix, "application/octet-stream")

    return FileResponse(str(requested), media_type=media_type)
