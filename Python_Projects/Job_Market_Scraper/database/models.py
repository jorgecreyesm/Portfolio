from .connection import get_conn

INSERT_POSTING = """
    INSERT INTO job_postings
        (job_title, company_name, location, is_remote,
         salary_min, salary_max, salary_type,
         raw_description, source_url, source, date_posted,
         is_staffing_agency, agency_flag_reason,
         filter_score, filter_tier)
    VALUES
        (%(job_title)s, %(company_name)s, %(location)s, %(is_remote)s,
         %(salary_min)s, %(salary_max)s, %(salary_type)s,
         %(raw_description)s, %(source_url)s, %(source)s, %(date_posted)s,
         %(is_staffing_agency)s, %(agency_flag_reason)s,
         %(filter_score)s, %(filter_tier)s)
    RETURNING id;
"""

INSERT_SKILL = """
    INSERT INTO job_skills (job_id, skill_raw, skill_normalized, skill_category)
    VALUES (%s, %s, %s, %s);
"""


def insert_posting(job: dict) -> int:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(INSERT_POSTING, job)
        conn.commit()
        return cur.fetchone()[0]


def insert_skills(job_id: int, skills: list[dict]):
    if not skills:
        return
    rows = [(job_id, s["raw"], s["normalized"], s["category"]) for s in skills]
    with get_conn() as conn, conn.cursor() as cur:
        cur.executemany(INSERT_SKILL, rows)
        conn.commit()


def insert_posting_with_skills(job: dict, skills: list[dict]) -> int:
    """Atomic insert — posting and skills commit together or not at all."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(INSERT_POSTING, job)
        job_id = cur.fetchone()[0]
        if skills:
            rows = [(job_id, s["raw"], s["normalized"], s["category"]) for s in skills]
            cur.executemany(INSERT_SKILL, rows)
        conn.commit()
        return job_id


def fetch_all_postings() -> list[dict]:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT id, job_title, company_name, location, is_remote,
                   salary_min, salary_max, salary_type,
                   raw_description, is_staffing_agency, agency_flag_reason,
                   source_url, source, filter_score, filter_tier, date_posted
            FROM job_postings
            ORDER BY scraped_at DESC;
        """)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def fetch_all_skills() -> list[dict]:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT job_id, skill_raw, skill_normalized, skill_category FROM job_skills;")
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def url_exists(url: str) -> bool:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT 1 FROM job_postings WHERE source_url = %s LIMIT 1;", (url,))
        return cur.fetchone() is not None
