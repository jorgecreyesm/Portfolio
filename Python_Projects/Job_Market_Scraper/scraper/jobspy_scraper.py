import pandas as pd
from jobspy import scrape_jobs


def fetch_jobs(query: str, location: str = "", results: int = 50) -> list[dict]:
    df = scrape_jobs(
        site_name=["indeed", "linkedin", "google"],
        search_term=query,
        location=location or "United States",
        results_wanted=results,
        hours_old=168,
        country_indeed="USA",
        verbose=0,
    )

    if df is None or df.empty:
        return []

    jobs = []
    for _, row in df.iterrows():
        salary_min, salary_max, salary_type = _parse_salary(row)
        jobs.append({
            "job_title":          str(row.get("title") or ""),
            "company_name":       str(row.get("company") or ""),
            "location":           str(row.get("location") or ""),
            "is_remote":          bool(row.get("is_remote") or False),
            "salary_min":         salary_min,
            "salary_max":         salary_max,
            "salary_type":        salary_type,
            "raw_description":    str(row.get("description") or ""),
            "source_url":         str(row.get("job_url") or ""),
            "source":             str(row.get("site") or ""),
            "date_posted":        _clean_date(row.get("date_posted")),
            "is_staffing_agency": False,
            "agency_flag_reason": None,
        })
    return jobs


def _clean_date(val):
    if val is None:
        return None
    try:
        if pd.isna(val):
            return None
    except (TypeError, ValueError):
        pass
    return val


def _parse_salary(row) -> tuple:
    lo   = row.get("min_amount")
    hi   = row.get("max_amount")
    unit = str(row.get("interval") or "").lower()

    salary_type = None
    if "hour" in unit:
        salary_type = "hourly"
    elif "year" in unit or "annual" in unit:
        salary_type = "annual"

    try:
        lo = float(lo) if lo is not None else None
        hi = float(hi) if hi is not None else None
    except (ValueError, TypeError):
        lo, hi = None, None

    return lo, hi, salary_type
