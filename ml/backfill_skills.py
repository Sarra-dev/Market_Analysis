from api.database import SessionLocal
from ml.skill_extractor import build_skill_extractor, extract_skills
from sqlalchemy import text

def backfill():
    db = SessionLocal()
    nlp = build_skill_extractor()

    rows = db.execute(text("SELECT id, description FROM jobs")).fetchall()
    print(f"Processing {len(rows)} jobs...")

    for row in rows:
        skills = extract_skills(nlp, row.description)
        db.execute(
            text("UPDATE jobs SET skills = :skills WHERE id = :id"),
            {"skills": skills, "id": row.id}
        )

    db.commit()
    print("Done.")

if __name__ == "__main__":
    backfill()