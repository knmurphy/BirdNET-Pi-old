"""Species-related API endpoints."""

from datetime import date, datetime

from fastapi import APIRouter, HTTPException

from api.services.database import get_connection
from api.models.species import SpeciesSummary, SpeciesTodayResponse

router = APIRouter()


@router.get("/species/today", response_model=SpeciesTodayResponse)
async def get_species_today():
    """Get all species detected today with counts and hourly breakdown."""
    today = date.today().isoformat()

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Get all species with aggregations
        cursor.execute("""
            SELECT
                Com_Name,
                Sci_Name,
                COUNT(*) as detection_count,
                MAX(Confidence) as max_confidence,
                MAX(Time) as last_seen
            FROM detections
            WHERE Date = ?
            GROUP BY Com_Name, Sci_Name
            ORDER BY detection_count DESC
        """, [today])
        species_rows = cursor.fetchall()

        species_list = []

        for row in species_rows:
            com_name, sci_name, detection_count, max_confidence, last_seen = row

            # Get hourly counts for this species
            cursor.execute("""
                SELECT CAST(substr(Time, 1, 2) AS INTEGER) as hour, COUNT(*) as count
                FROM detections
                WHERE Date = ? AND Com_Name = ?
                GROUP BY hour
            """, [today, com_name])
            hourly_rows = cursor.fetchall()

            hourly_counts = [0] * 24
            for hour, count in hourly_rows:
                if hour is not None and 0 <= hour < 24:
                    hourly_counts[hour] = count

            species_list.append(SpeciesSummary(
                com_name=com_name,
                sci_name=sci_name,
                detection_count=detection_count,
                max_confidence=max_confidence,
                last_seen=last_seen,
                hourly_counts=hourly_counts,
            ))

        conn.close()

        return SpeciesTodayResponse(
            species=species_list,
            generated_at=datetime.now().isoformat(),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
