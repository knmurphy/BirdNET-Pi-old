"""System information API endpoints."""

import re
import subprocess
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.models.system import SystemResponse
from api.services.eventbus import event_bus
from api.services.system_info import (
    get_cpu_percent,
    get_temperature,
    celsius_to_fahrenheit,
    get_disk_usage,
    get_uptime,
    get_memory_percent,
)

router = APIRouter()


@router.get("/system", response_model=SystemResponse)
async def get_system():
    """Get system status including CPU, temperature, disk, and uptime."""
    # CPU (non-blocking quick read)
    cpu = get_cpu_percent(interval=0.1)

    # Temperature (Pi-specific)
    temp = get_temperature()

    # Disk usage
    disk = get_disk_usage("/")

    # Uptime
    uptime = get_uptime()

    # TODO: Get actual active classifiers from config
    active_classifiers = ["birdnet"]

    return SystemResponse(
        cpu_percent=cpu,
        temperature_celsius=temp,
        temperature_fahrenheit=celsius_to_fahrenheit(temp),
        memory_percent=get_memory_percent(),
        disk_used_gb=disk.used_gb,
        disk_total_gb=disk.total_gb,
        uptime_seconds=uptime,
        active_classifiers=active_classifiers,
        sse_subscribers=event_bus.subscriber_count,
        generated_at=datetime.now().isoformat(),
    )


class RestartRequest(BaseModel):
    """Request body for POST /system/restart."""

    confirm: bool
    service: str = "birdnet_analysis"


class RestartResponse(BaseModel):
    """Response for POST /system/restart."""

    status: str  # "restarting" or "rejected"
    service: str
    message: str


_SERVICE_NAME_RE = re.compile(r"^[a-zA-Z0-9_-]+$")


@router.post("/system/restart", response_model=RestartResponse)
async def restart_service(req: RestartRequest):
    """Restart a system service (e.g., the BirdNET analysis service).

    Requires explicit confirmation. Service name is validated to prevent
    injection attacks.
    """
    if not _SERVICE_NAME_RE.match(req.service):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid service name: '{req.service}'",
        )

    if not req.confirm:
        raise HTTPException(
            status_code=400,
            detail="Confirmation required to restart service",
        )

    try:
        subprocess.run(
            ["sudo", "systemctl", "restart", req.service],
            capture_output=True,
            timeout=10,
            check=True,
        )
        message = "Service restart initiated"
    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        FileNotFoundError,
    ):
        message = "Restart command issued (may require elevated privileges)"

    return RestartResponse(
        status="restarting",
        service=req.service,
        message=message,
    )
