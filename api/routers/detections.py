"""Detection-related API endpoints."""

from datetime import date, datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.services.database import get_connection
from api.services.eventbus import event_bus, DetectionEvent
from api.models.detection import TodaySummaryResponse, TopSpecies

router = APIRouter()


class DetectionNotification(BaseModel):
    """Payload for notifying the system of a new detection."""

    com_name: str
    sci_name: str
    confidence: float
    file_name: str = ""
    classifier: str = "birdnet"


class NotifyResponse(BaseModel):
    """Response for /api/detections/notify."""

    status: str
    subscribers_notified: int


@router.post("/detections/notify", response_model=NotifyResponse)
async def notify_detection(notification: DetectionNotification):
    """Publish a new detection event to all SSE subscribers.

    Called by analysis scripts when a new bird is detected.
    Broadcasts the detection to all connected SSE clients in real time.
    """
    now = datetime.now()
    event = DetectionEvent(
        id=0,
        com_name=notification.com_name,
        sci_name=notification.sci_name,
        confidence=notification.confidence,
        date=now.strftime("%Y-%m-%d"),
        time=now.strftime("%H:%M:%S"),
        iso8601=now.isoformat(),
        file_name=notification.file_name,
        classifier=notification.classifier,
    )
    count = await event_bus.publish(event)
    return NotifyResponse(status="published", subscribers_notified=count)


@router.get("/detections/today/summary", response_model=TodaySummaryResponse)
async def get_today_summary():
    """Get summary of today's detections.

    Returns total count, species count, top species, and hourly breakdown.
    """
    today = date.today().isoformat()

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Total detections today
        cursor.execute(
            "SELECT COUNT(*) FROM detections WHERE Date = ?", [today]
        )
        total = cursor.fetchone()[0]

        # Species count today
        cursor.execute(
            "SELECT COUNT(DISTINCT Com_Name) FROM detections WHERE Date = ?", [today]
        )
        species_count = cursor.fetchone()[0]

        # Top 5 species
        cursor.execute("""
            SELECT Com_Name, COUNT(*) as count
            FROM detections
            WHERE Date = ?
            GROUP BY Com_Name
            ORDER BY count DESC
            LIMIT 5
        """, [today])
        top_species_rows = cursor.fetchall()

        top_species = [
            TopSpecies(com_name=row[0], count=row[1])
            for row in top_species_rows
        ]

        # Hourly counts (24-element array)
        # SQLite uses substr() to extract characters
        cursor.execute("""
            SELECT CAST(substr(Time, 1, 2) AS INTEGER) as hour, COUNT(*) as count
            FROM detections
            WHERE Date = ?
            GROUP BY hour
        """, [today])
        hourly_rows = cursor.fetchall()

        hourly_counts = [0] * 24
        for hour, count in hourly_rows:
            if hour is not None and 0 <= hour < 24:
                hourly_counts[hour] = count

        conn.close()

        return TodaySummaryResponse(
            total_detections=total,
            species_count=species_count,
            top_species=top_species,
            hourly_counts=hourly_counts,
            generated_at=datetime.now().isoformat(),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
