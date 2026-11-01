import pandas as pd
from api.database import engine

query = """
    SELECT id, titre, description, experience, entreprise, localisation, contrat, source
    FROM jobs
"""
df = pd.read_sql(query, engine)

print("Columns:", df.columns.tolist())
print("Shape:", df.shape)

df.to_csv("jobs_export.csv", index=False)
print("Saved jobs_export.csv")