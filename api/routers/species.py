"""Species-related API endpoints."""

from datetime import date, datetime

from fastapi import APIRouter, HTTPException

from api.services.database import get_connection
from api.services.flickr_service import FlickrService
from api.models.species import SpeciesSummary, SpeciesTodayResponse
from api.models.flickr import FlickrImageResponse

router = APIRouter()


@router.get("/species/{com_name}/image", response_model=FlickrImageResponse)
async def get_species_image(com_name: str):
    """Get a Flickr image for a species by common name."""
    flickr = FlickrService()
    # Try to get image by common name
    image = flickr.get_image_for_common_name(com_name)
    if image:
        return FlickrImageResponse(
            sci_name=image.sci_name,
            com_name=image.com_name,
            image_url=image.image_url,
            title=image.title,
            author_url=image.author_url,
            license_url=image.license_url,
            source="flickr",
        )
    raise HTTPException(status_code=404, detail=f"No image cached for species: {com_name}")


@router.get("/species/today", response_model=SpeciesTodayResponse)
async def get_species_today():
    """Get all species detected today with counts and hourly breakdown."""
    today = date.today().isoformat()

    conn = None
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

        # Get current hour for "is_new" calculation
        current_hour = datetime.now().hour

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
            first_detection_hour = None
            for hour, count in hourly_rows:
                if hour is not None and 0 <= hour < 24:
                    hourly_counts[hour] = count
                    if first_detection_hour is None or hour < first_detection_hour:
                        first_detection_hour = hour

            # Determine if species is "new" (first detection within last 2 hours)
            is_new = False
            if first_detection_hour is not None:
                hours_since_first = current_hour - first_detection_hour
                is_new = 0 <= hours_since_first <= 2

            species_list.append(SpeciesSummary(
                com_name=com_name,
                sci_name=sci_name,
                detection_count=detection_count,
                max_confidence=max_confidence,
                last_seen=last_seen,
                hourly_counts=hourly_counts,
                is_new=is_new,
            ))

        return SpeciesTodayResponse(
            species=species_list,
            generated_at=datetime.now().isoformat(),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if conn:
            conn.close()
