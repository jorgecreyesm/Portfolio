import re
from datetime import datetime, date

from config import (
    EXCLUDE_TITLE_KEYWORDS, EXCLUDE_BODY_KEYWORDS, POSITIVE_SIGNALS,
    FAKE_COMPANY_PATTERNS, SALARY_CONFIG,
)


def is_fake_company(company_name: str) -> bool:
    if not company_name or len(company_name.strip()) < 3:
        return True
    name_lower = company_name.lower()
    return any(re.search(p, name_lower) for p in FAKE_COMPANY_PATTERNS)


def has_excluded_title(title: str) -> bool:
    padded = f" {title.lower()} "
    return any(f" {kw} " in padded for kw in EXCLUDE_TITLE_KEYWORDS)


def has_excluded_body_keywords(description: str) -> bool:
    desc_lower = description.lower()
    return any(kw in desc_lower for kw in EXCLUDE_BODY_KEYWORDS)


def count_positive_signals(description: str) -> int:
    desc_lower = description.lower()
    return sum(1 for kw in POSITIVE_SIGNALS if kw in desc_lower)


def is_recent(posted_date, max_days: int = 7) -> bool:
    if not posted_date:
        return True
    if isinstance(posted_date, str):
        try:
            posted_date = datetime.strptime(posted_date, "%Y-%m-%d").date()
        except ValueError:
            return True
    if isinstance(posted_date, datetime):
        posted_date = posted_date.date()
    if not isinstance(posted_date, date):
        return True
    return (date.today() - posted_date).days <= max_days


def _is_remote(job: dict) -> bool:
    if job.get("is_remote"):
        return True
    description = (job.get("raw_description") or "").lower()
    location = (job.get("location") or "").lower()
    onsite_signals = [
        "must report to office",
        "on-site required",
        "in-office",
        "must be located in",
        "must reside in",
        "hybrid — must be within",
        "occasional travel to our",
    ]
    if any(s in description for s in onsite_signals):
        return False
    remote_signals = ["remote", "work from home", "distributed", "anywhere in the us"]
    return any(s in location or s in description for s in remote_signals)


def _to_annual(val, salary_type: str) -> float:
    if val is None:
        return 0.0
    return float(val) * 2080 if salary_type == "hourly" else float(val)


def _salary_passes(salary_min, salary_max, salary_type: str) -> bool:
    if salary_min is None and salary_max is None:
        return True  # no salary data — don't reject, flag for review
    val = salary_min if salary_min is not None else salary_max
    return _to_annual(val, salary_type or "") >= SALARY_CONFIG["min_annual"]


def filter_job(job: dict) -> dict:
    """
    Pre-insertion filter for a scraped job dict.

    Returns:
        {"pass": bool, "reason": str, "score": int, "tier": str|None, "flags": list}

    Expects scraper-format keys:
        job_title, company_name, location, is_remote,
        raw_description, salary_min, salary_max, salary_type, date_posted
    """
    title       = job.get("job_title", "")
    company     = job.get("company_name", "")
    description = job.get("raw_description", "")
    salary_min  = job.get("salary_min")
    salary_max  = job.get("salary_max")
    salary_type = job.get("salary_type") or ""
    posted_date = job.get("date_posted")

    def _fail(reason):
        return {"pass": False, "reason": reason, "score": 0, "tier": None, "flags": []}

    if is_fake_company(company):
        return _fail("Fake or unknown company")

    if has_excluded_title(title):
        return _fail(f"Excluded title: {title}")

    if has_excluded_body_keywords(description):
        matched = [kw for kw in EXCLUDE_BODY_KEYWORDS if kw in description.lower()]
        return _fail(f"Red flag keywords: {matched}")

    if not _is_remote(job):
        return _fail("Not remote")

    if not _salary_passes(salary_min, salary_max, salary_type):
        return _fail(f"Salary too low (min={salary_min}, max={salary_max})")

    if not is_recent(posted_date, max_days=7):
        return _fail("Posted more than 7 days ago")

    # ── Scoring ──────────────────────────────────────────────────────
    score = 0
    flags = []

    if salary_min is None and salary_max is None:
        flags.append("No salary listed — verify manually")
        score += 1
    else:
        annual = _to_annual(salary_min or salary_max, salary_type)
        if annual >= SALARY_CONFIG["target_min"] * 1.2:
            score += 3
        elif annual >= SALARY_CONFIG["target_min"]:
            score += 2
        else:
            score += 1

    score += min(count_positive_signals(description), 5)

    if is_recent(posted_date, max_days=2):
        score += 2
        flags.append("Very recent — apply ASAP")

    tier = "HIGH" if score >= 8 else ("MEDIUM" if score >= 5 else "LOW")

    return {"pass": True, "score": score, "tier": tier, "flags": flags, "reason": "Passed all filters"}
