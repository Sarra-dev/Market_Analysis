from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from api.database import get_db

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.get("/")
def get_jobs(
    db: Session = Depends(get_db),
    country: str = Query(None),
    contrat: str = Query(None),
    experience: str = Query(None),
    search: str = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0)
):
    base_where = "WHERE 1=1"
    params = {}

    if country:
        base_where += " AND source ILIKE :country"
        params["country"] = f"%{country}%"
    if contrat:
        base_where += " AND contrat = :contrat"
        params["contrat"] = contrat
    if experience:
        base_where += " AND experience = :experience"
        params["experience"] = experience
    if search:
        base_where += " AND (titre ILIKE :search OR description ILIKE :search)"
        params["search"] = f"%{search}%"

    count_query = f"SELECT COUNT(*) AS total FROM jobs {base_where}"
    total = db.execute(text(count_query), params).scalar()

    data_query = f"""
        SELECT id, titre, entreprise, localisation, date_publication, experience, contrat, source
        FROM jobs {base_where}
        ORDER BY scraped_at DESC LIMIT :limit OFFSET :offset
    """
    params["limit"] = limit
    params["offset"] = offset
    result = db.execute(text(data_query), params).fetchall()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": [dict(row._mapping) for row in result]
    }


@router.get("/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    result = db.execute(
        text("SELECT * FROM jobs WHERE id = :id"),
        {"id": job_id}
    ).fetchone()
    if not result:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Job not found")
    return dict(result._mapping)