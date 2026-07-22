"""
Espresso Shot Tracker — FastAPI backend.

Run:  uvicorn api:app --reload --port 8000

Reads DB connection from DATABASE_URL env var or individual
DB_HOST / DB_NAME / DB_USER / DB_PASSWORD / DB_PORT vars (same as Espresso_Tracker).
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Optional

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

load_dotenv()

logger = logging.getLogger("espresso")

app = FastAPI(title="Espresso Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────
# DB
# ─────────────────────────────────────────────────────────────

def get_conn():
    url = os.getenv("DATABASE_URL")
    if url:
        return psycopg2.connect(url, cursor_factory=psycopg2.extras.RealDictCursor)
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        dbname=os.getenv("DB_NAME", "espresso"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        port=int(os.getenv("DB_PORT", "5432")),
        cursor_factory=psycopg2.extras.RealDictCursor,
    )


@app.on_event("startup")
def ensure_schema() -> None:
    """Create tables if they don't exist yet (idempotent). Lets a fresh
    Neon database come up without a manual psql step. A failure here is
    logged but not fatal, so the app still serves the static frontend."""
    schema_path = Path(__file__).with_name("schema.sql")
    try:
        ddl = schema_path.read_text()
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(ddl)
            conn.commit()
        logger.info("Schema ensured (%s)", schema_path.name)
    except Exception as exc:  # noqa: BLE001 — never block startup on this
        logger.warning("Could not ensure schema: %s", exc)


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _fmt_shot_at(ts: datetime) -> str:
    today = date.today()
    shot_date = ts.date()
    if shot_date == today:
        prefix = "Today"
    elif shot_date == today - timedelta(days=1):
        prefix = "Yesterday"
    else:
        prefix = ts.strftime("%a, %b %-d")
    return f"{prefix} · {ts.strftime('%H:%M')}"


# ─────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────

@app.get("/api/shots")
def list_shots():
    sql = """
        SELECT
            s.id,
            s.shot_at,
            COALESCE(b.roaster, '') AS brand,
            COALESCE(b.name, '')    AS bean,
            COALESCE(b.roast_level, '') AS roast,
            COALESCE(b.origin, '')  AS origin,
            s.dose_g::float  AS dose,
            s.yield_g::float AS yield,
            s.time_sec       AS time,
            COALESCE(s.grind_setting, '') AS grind,
            COALESCE(s.taste_rating, 0)   AS rating,
            COALESCE(s.notes, '')          AS notes
        FROM shots s
        LEFT JOIN beans b ON s.bean_id = b.id
        ORDER BY s.shot_at DESC
        LIMIT 200;
    """
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    result = []
    for r in rows:
        result.append({
            "id":      r["id"],
            "shot_at": _fmt_shot_at(r["shot_at"]),
            "brand":   r["brand"],
            "bean":    r["bean"],
            "roast":   r["roast"].title().replace("-", "-"),  # "medium-dark" → "Medium-dark"
            "origin":  r["origin"].title() if r["origin"] else "",
            "dose":    r["dose"],
            "yield":   r["yield"],
            "time":    r["time"],
            "grind":   r["grind"],
            "rating":  r["rating"],
            "notes":   r["notes"],
        })
    return result


class ShotIn(BaseModel):
    brand: str
    bean: str
    roast: str
    origin: str
    dose_g: float
    yield_g: float
    time_sec: int
    grind_setting: str
    taste_rating: int
    notes: Optional[str] = None


@app.post("/api/shots", status_code=201)
def log_shot(body: ShotIn):
    roast_norm = body.roast.lower()
    valid_roasts = {"light", "medium-light", "medium", "medium-dark", "dark"}
    if roast_norm not in valid_roasts:
        roast_norm = "medium"

    try:
        with get_conn() as conn, conn.cursor() as cur:
            # Find or create bean
            cur.execute(
                """
                SELECT id FROM beans
                WHERE lower(name) = lower(%s) AND lower(coalesce(roaster,'')) = lower(%s)
                LIMIT 1
                """,
                (body.bean, body.brand),
            )
            row = cur.fetchone()
            if row:
                bean_id = row["id"]
            else:
                cur.execute(
                    """
                    INSERT INTO beans (name, roaster, roast_level, origin)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """,
                    (body.bean, body.brand, roast_norm, body.origin),
                )
                bean_id = cur.fetchone()["id"]

            # Insert shot
            cur.execute(
                """
                INSERT INTO shots (shot_at, bean_id, dose_g, yield_g, time_sec,
                                   grind_setting, taste_rating, notes)
                VALUES (NOW(), %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    bean_id,
                    body.dose_g,
                    body.yield_g,
                    body.time_sec,
                    body.grind_setting,
                    body.taste_rating,
                    body.notes,
                ),
            )
            new_id = cur.fetchone()["id"]
            conn.commit()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return {"id": new_id}


# Serve the HTML/JSX files — must be mounted AFTER the API routes
app.mount("/", StaticFiles(directory=".", html=True), name="static")
