"""System information API endpoints."""

from datetime import datetime

from fastapi import APIRouter

from api.models.system import SystemResponse
from api.services.eventbus import event_bus
from api.services.system_info import (
    get_cpu_percent,
    get_temperature,
    get_disk_usage,
    get_uptime,
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
        disk_used_gb=disk.used_gb,
        disk_total_gb=disk.total_gb,
        uptime_seconds=uptime,
        active_classifiers=active_classifiers,
        sse_subscribers=event_bus.subscriber_count,
        generated_at=datetime.now().isoformat(),
    )
