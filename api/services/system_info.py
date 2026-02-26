"""System information utilities for CPU, temperature, disk, etc."""

import time
import shutil
from typing import NamedTuple

import psutil


class DiskUsage(NamedTuple):
    """Disk usage information."""

    used_gb: float
    total_gb: float
    percent: float


def get_cpu_percent(interval: float = 0.1) -> float:
    """Get CPU usage percentage.

    Args:
        interval: Measurement interval in seconds.

    Returns:
        CPU usage as percentage (0-100).
    """
    return psutil.cpu_percent(interval=interval)


def get_temperature() -> float:
    """Get CPU temperature in Celsius.

    Returns:
        Temperature in Celsius, or 0 if unavailable.
    """
    try:
        # Raspberry Pi thermal zone
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return int(f.read().strip()) / 1000.0
    except (FileNotFoundError, PermissionError, ValueError):
        return 0.0


def get_disk_usage(path: str = "/") -> DiskUsage:
    """Get disk usage for a path.

    Args:
        path: Path to check (default: root).

    Returns:
        DiskUsage tuple with used_gb, total_gb, percent.
    """
    usage = shutil.disk_usage(path)
    total_gb = usage.total / (1024**3)
    used_gb = usage.used / (1024**3)
    percent = (usage.used / usage.total) * 100 if usage.total > 0 else 0
    return DiskUsage(used_gb=used_gb, total_gb=total_gb, percent=percent)


def get_uptime() -> float:
    """Get system uptime in seconds.

    Returns:
        Uptime in seconds.
    """
    return time.time() - psutil.boot_time()


def get_memory_percent() -> float:
    """Get memory usage percentage.

    Returns:
        Memory usage as percentage (0-100).
    """
    return psutil.virtual_memory().percent
