import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "job_market"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
    )

    cur = conn.cursor()

    cur.execute("SHOW server_encoding;")
    print("Server:", cur.fetchone())

    cur.execute("SHOW client_encoding;")
    print("Client:", cur.fetchone())

    cur.execute("SELECT version();")
    print("Version:", cur.fetchone())

    conn.close()

except Exception as e:
    print(type(e))
    print(repr(e))