from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from api.database import get_db

router = APIRouter(prefix="/stats", tags=["Stats"])

@router.get("/overview")
def get_overview(db: Session = Depends(get_db)):
    result = db.execute(text("""
        SELECT
            COUNT(*)                                        AS total_jobs,
            COUNT(DISTINCT entreprise)                      AS total_companies,
            COUNT(DISTINCT source)                          AS total_countries,
            COUNT(CASE WHEN experience = 'Senior' THEN 1 END) AS senior_roles,
            COUNT(CASE WHEN description ILIKE '%remote%' THEN 1 END) AS remote_roles
        FROM jobs
    """)).fetchone()
    return dict(result._mapping)


@router.get("/by-country")
def get_by_country(db: Session = Depends(get_db)):
    result = db.execute(text("""
        SELECT source AS country, COUNT(*) AS count
        FROM jobs
        GROUP BY source
        ORDER BY count DESC
    """)).fetchall()
    return [dict(row._mapping) for row in result]


@router.get("/by-contract")
def get_by_contract(db: Session = Depends(get_db)):
    result = db.execute(text("""
        SELECT contrat, COUNT(*) AS count
        FROM jobs
        WHERE contrat IS NOT NULL AND contrat <> 'N/A'
        GROUP BY contrat
        ORDER BY count DESC
    """)).fetchall()
    return [dict(row._mapping) for row in result]


@router.get("/top-skills")
def get_top_skills(db: Session = Depends(get_db), limit: int = 15):
    result = db.execute(text("""
        SELECT skill, COUNT(*) AS count
        FROM jobs, UNNEST(skills) AS skill
        GROUP BY skill
        ORDER BY count DESC
        LIMIT :limit
    """), {"limit": limit}).fetchall()
    return [dict(row._mapping) for row in result]


@router.get("/top-companies")
def get_top_companies(db: Session = Depends(get_db)):
    result = db.execute(text("""
        SELECT entreprise AS company, COUNT(*) AS count
        FROM jobs
        WHERE entreprise IS NOT NULL
        GROUP BY entreprise
        ORDER BY count DESC
        LIMIT 10
    """)).fetchall()
    return [dict(row._mapping) for row in result]


@router.get("/by-date")
def get_by_date(db: Session = Depends(get_db)):
    result = db.execute(text("""
        SELECT date_publication AS date, COUNT(*) AS count
        FROM jobs
        WHERE date_publication IS NOT NULL
        GROUP BY date_publication
        ORDER BY date_publication DESC
        LIMIT 30
    """)).fetchall()
    return [dict(row._mapping) for row in result]