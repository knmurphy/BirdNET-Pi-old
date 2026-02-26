"""Detection-related API endpoints."""

from datetime import date, datetime

from fastapi import APIRouter, HTTPException

from api.services.database import get_duckdb_connection
from api.models.detection import TodaySummaryResponse, TopSpecies

router = APIRouter()


@router.get("/detections/today/summary", response_model=TodaySummaryResponse)
async def get_today_summary():
    """Get summary of today's detections.

    Returns total count, species count, top species, and hourly breakdown.
    """
    today = date.today().isoformat()
    
    try:
        conn = get_duckdb_connection(read_only=True)
        
        # Total detections today
        total = conn.execute(
            "SELECT COUNT(*) FROM detections WHERE date = ?", [today]
        ).fetchone()[0]
        
        # Species count today
        species_count = conn.execute(
            "SELECT COUNT(DISTINCT com_name) FROM detections WHERE date = ?", [today]
        ).fetchone()[0]
        
        # Top 5 species
        top_species_rows = conn.execute("""
            SELECT com_name, COUNT(*) as count
            FROM detections 
            WHERE date = ?
            GROUP BY com_name
            ORDER BY count DESC 
            LIMIT 5
        """, [today]).fetchall()
        
        top_species = [
            TopSpecies(com_name=row[0], count=row[1])
            for row in top_species_rows
        ]
        
        # Hourly counts (24-element array)
        # Use SUBSTRING since time is stored as "HH:MM:SS" not a timestamp
        hourly_rows = conn.execute("""
            SELECT CAST(SUBSTRING(time, 1, 2) AS INTEGER) as hour, COUNT(*) as count
            FROM detections 
            WHERE date = ?
            GROUP BY hour
        """, [today]).fetchall()
        
        hourly_counts = [0] * 24
        for hour, count in hourly_rows:
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
