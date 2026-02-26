"""Species-related API endpoints."""

from datetime import date, datetime

from fastapi import APIRouter, HTTPException

from api.services.database import get_duckdb_connection
from api.models.species import SpeciesSummary, SpeciesTodayResponse

router = APIRouter()


@router.get("/species/today", response_model=SpeciesTodayResponse)
async def get_species_today():
    """Get all species detected today with counts and hourly breakdown."""
    today = date.today().isoformat()
    
    try:
        conn = get_duckdb_connection(read_only=True)
        
        # Get all species with aggregations
        species_rows = conn.execute("""
            SELECT
                com_name,
                sci_name,
                COUNT(*) as detection_count,
                MAX(confidence) as max_confidence,
                MAX(time) as last_seen
            FROM detections
            WHERE date = ?
            GROUP BY com_name, sci_name
            ORDER BY detection_count DESC
        """, [today]).fetchall()
        
        species_list = []
        
        for row in species_rows:
            com_name, sci_name, detection_count, max_confidence, last_seen = row
            
            # Get hourly counts for this species
            # Use SUBSTRING since time is stored as "HH:MM:SS" not a timestamp
            hourly_rows = conn.execute("""
                SELECT CAST(SUBSTRING(time, 1, 2) AS INTEGER) as hour, COUNT(*) as count
                FROM detections 
                WHERE date = ? AND com_name = ?
                GROUP BY hour
            """, [today, com_name]).fetchall()
            
            hourly_counts = [0] * 24
            for hour, count in hourly_rows:
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
