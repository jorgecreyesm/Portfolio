import psycopg2
from config import DB


def get_conn():
    return psycopg2.connect(**DB)


def init_db():
    with open("schema.sql") as f:
        sql = f.read()
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql)
        conn.commit()
    print("Database initialized.")
