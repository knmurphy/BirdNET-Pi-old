"""Detection-related API endpoints."""

from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from api.services.database import get_connection, get_duckdb_connection
from api.models.detection import Detection, TodaySummaryResponse, TopSpecies

router = APIRouter()


class DetectionsResponse(BaseModel):
    """Paginated response for detections list."""

    detections: list[Detection]
    total: int
    page: int
    limit: int
    has_more: bool


@router.get("/detections", response_model=DetectionsResponse)
async def get_detections(
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    classifier: Optional[str] = Query(None, description="Filter by classifier name"),
    min_confidence: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum confidence threshold"),
    species: Optional[str] = Query(None, description="Filter by species name (common name)"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(50, ge=1, le=500, description="Results per page"),
):
    """Get paginated detection log with optional filtering.

    Query DuckDB for detection records with support for filtering by date,
    classifier, minimum confidence, and species name.
    """
    try:
        conn = get_duckdb_connection()
        
        # Build query with filters
        conditions = []
        params = []
        
        if date:
            conditions.append("date = ?")
            params.append(date)
        
        if classifier:
            conditions.append("classifier = ?")
            params.append(classifier)
        
        if min_confidence is not None:
            conditions.append("confidence >= ?")
            params.append(min_confidence)
        
        if species:
            conditions.append("com_name ILIKE ?")
            params.append(f"%{species}%")
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # Get total count
        count_query = f"SELECT COUNT(*) FROM detections WHERE {where_clause}"
        total = conn.execute(count_query, params).fetchone()[0]
        
        # Calculate pagination
        offset = (page - 1) * limit
        
        # Get paginated results
        data_query = f"""
            SELECT id, date, time, iso8601, com_name, sci_name, confidence,
                   file_name, classifier, lat, lon, cutoff, week, sens, overlap
            FROM detections
            WHERE {where_clause}
            ORDER BY date DESC, time DESC
            LIMIT ? OFFSET ?
        """
        params_with_pagination = params + [limit, offset]
        rows = conn.execute(data_query, params_with_pagination).fetchall()
        
        conn.close()
        
        # Convert to Detection models
        detections = [
            Detection(
                id=row[0],
                date=row[1],
                time=row[2],
                iso8601=row[3],
                com_name=row[4],
                sci_name=row[5],
                confidence=row[6],
                file_name=row[7],
                classifier=row[8] or "birdnet",
                lat=row[9],
                lon=row[10],
                cutoff=row[11],
                week=row[12],
                sens=row[13],
                overlap=row[14],
            )
            for row in rows
        ]
        
        return DetectionsResponse(
            detections=detections,
            total=total,
            page=page,
            limit=limit,
            has_more=(offset + limit) < total,
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


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
