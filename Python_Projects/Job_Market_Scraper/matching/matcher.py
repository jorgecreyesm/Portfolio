import json
import math
import decimal
from pathlib import Path

import pandas as pd
from tabulate import tabulate

from database.models import fetch_all_postings, fetch_all_skills

PROFILE_PATH = Path("profile.json")

WEIGHTS = {
    "skill":    0.50,
    "remote":   0.15,
    "salary":   0.20,
    "title":    0.15,
}

AGENCY_PENALTY  = 0.85                              # multiplier for staffing agency postings
TIER_BONUS      = {"HIGH": 0.05, "MEDIUM": 0.02}   # additive bonus from pre-filter tier
SKILL_BREADTH_N = 5                                 # skill count treated as "full breadth"


def load_profile() -> dict:
    with open(PROFILE_PATH) as f:
        return json.load(f)


def _skill_score(job_skills: set[str], user_skills: set[str]) -> float:
    """
    Hybrid of coverage (% of job requirements met) and breadth (absolute match count).
    Prevents jobs with many listed skills from being unfairly penalized.
    """
    if not job_skills:
        return 0.0
    matched = job_skills & user_skills
    if not matched:
        return 0.0
    coverage = len(matched) / len(job_skills)
    breadth  = min(len(matched) / SKILL_BREADTH_N, 1.0)
    return 0.6 * coverage + 0.4 * breadth


def _remote_score(is_remote: bool, location: str, profile: dict) -> float:
    loc = location.lower()
    if is_remote or "remote" in loc:
        return 1.0 if profile["preferred_remote"] else 0.3
    if profile["open_to_hybrid"] and "hybrid" in loc:
        return 0.7
    for pref in profile["preferred_locations"]:
        if pref.lower() in loc:
            return 0.8
    return 0.2 if profile["preferred_remote"] else 0.6


def _salary_score(salary_min, salary_max, salary_type: str, profile: dict) -> float:
    if salary_min is None and salary_max is None:
        return 0.5

    try:
        salary_min = float(salary_min) if salary_min is not None else None
        salary_max = float(salary_max) if salary_max is not None else None
        if salary_min is not None and math.isnan(salary_min):
            salary_min = None
        if salary_max is not None and math.isnan(salary_max):
            salary_max = None
    except (TypeError, ValueError, decimal.InvalidOperation):
        return 0.5

    if salary_min is None and salary_max is None:
        return 0.5

    # Use midpoint when both present; avoids over-rewarding jobs with wide ranges
    if salary_min is not None and salary_max is not None:
        val = (salary_min + salary_max) / 2
    else:
        val = salary_max or salary_min

    if salary_type == "hourly":
        annual_equiv = val * 2080
        threshold    = profile["salary_min_hourly"] * 2080
    else:
        annual_equiv = val
        threshold    = profile["salary_min_annual"]

    if annual_equiv >= threshold * 1.3:
        return 1.0
    if annual_equiv >= threshold * 1.1:
        return 0.85
    if annual_equiv >= threshold:
        return 0.7
    if annual_equiv >= threshold * 0.85:
        return 0.4
    return 0.1


def _title_score(job_title: str, profile: dict) -> float:
    title = job_title.lower()
    for kw in profile["preferred_titles"]:
        if kw.lower() in title:
            return 1.0
    if "analyst" in title:   # catches reporting/financial/commercial/etc analyst
        return 0.6
    return 0.2


def run_matcher(save: bool = False, exclude_agency: bool = False):
    profile  = load_profile()
    postings = fetch_all_postings()
    skills   = fetch_all_skills()

    if not postings:
        print("No postings in database. Run scrape first.")
        return

    user_skills = {s.lower() for s in profile["skills"]}

    df_jobs   = pd.DataFrame(postings)
    df_skills = pd.DataFrame(skills) if skills else pd.DataFrame(
        columns=["job_id", "skill_normalized"]
    )

    if exclude_agency:
        before = len(df_jobs)
        df_jobs = df_jobs[~df_jobs["is_staffing_agency"].fillna(False)].copy()
        print(f"  Excluded {before - len(df_jobs)} agency postings.")

    skills_by_job = (
        df_skills.groupby("job_id")["skill_normalized"]
        .apply(lambda x: {s.lower() for s in x})
        .to_dict()
    )

    rows = []
    for _, job in df_jobs.iterrows():
        job_id     = job["id"]
        job_skills = skills_by_job.get(job_id, set())

        s_skill  = _skill_score(job_skills, user_skills)
        s_remote = _remote_score(job["is_remote"], job["location"] or "", profile)
        s_salary = _salary_score(
            job["salary_min"], job["salary_max"], job["salary_type"] or "", profile
        )
        s_title  = _title_score(job["job_title"], profile)

        weighted = (
            WEIGHTS["skill"]  * s_skill  +
            WEIGHTS["remote"] * s_remote +
            WEIGHTS["salary"] * s_salary +
            WEIGHTS["title"]  * s_title
        )

        if job["is_staffing_agency"]:
            weighted *= AGENCY_PENALTY

        raw_tier   = job["filter_tier"] if isinstance(job["filter_tier"], str) else ""
        tier_bonus = TIER_BONUS.get(raw_tier, 0.0)
        total      = min(1.0, weighted + tier_bonus)

        matched_skills = sorted(job_skills & user_skills)
        missing_skills = sorted(job_skills - user_skills)

        rows.append({
            "match_%":        round(total * 100, 1),
            "job_title":      job["job_title"],
            "company":        job["company_name"],
            "location":       job["location"],
            "remote":         "Yes" if job["is_remote"] else "No",
            "agency":         "Yes" if job["is_staffing_agency"] else "No",
            "filter_tier":    raw_tier or "—",
            "salary_min":     f"${job['salary_min']:,.0f}" if job["salary_min"] else "—",
            "salary_max":     f"${job['salary_max']:,.0f}" if job["salary_max"] else "—",
            "salary_type":    job["salary_type"] or "—",
            "skills_matched": ", ".join(matched_skills) if matched_skills else "none",
            "skills_missing": ", ".join(missing_skills[:6]) if missing_skills else "—",
            "source_url":     job["source_url"],
            "skill_score":    round(s_skill  * 100, 1),
            "remote_score":   round(s_remote * 100, 1),
            "salary_score":   round(s_salary * 100, 1),
            "title_score":    round(s_title  * 100, 1),
        })

    df_results = (
        pd.DataFrame(rows)
        .sort_values("match_%", ascending=False)
        .reset_index(drop=True)
    )

    top_n  = profile.get("top_n", 10)
    top_df = df_results.head(top_n)

    display_cols = [
        "match_%", "job_title", "company", "location",
        "remote", "agency", "filter_tier",
        "salary_min", "salary_max", "salary_type", "skills_matched",
    ]

    print("\n" + "=" * 60)
    print(f"  TOP {top_n} JOB MATCHES FOR {profile['name'].upper()}")
    print("=" * 60)
    print(tabulate(top_df[display_cols], headers="keys", tablefmt="simple",
                   showindex=True))

    print("\n--- Score Breakdown (top matches) ---")
    score_cols = [
        "match_%", "job_title",
        "skill_score", "remote_score", "salary_score", "title_score",
        "skills_missing",
    ]
    print(tabulate(top_df[score_cols], headers="keys", tablefmt="simple",
                   showindex=True))

    print("\n--- Apply Links (top matches) ---")
    for i, row in top_df.iterrows():
        print(f"  [{i}] {row['job_title']} @ {row['company']}")
        print(f"      {row['source_url']}")

    print("=" * 60 + "\n")

    if save:
        from datetime import date
        out = Path("reports") / f"matches_{date.today().isoformat()}.csv"
        df_results.to_csv(out, index=False)
        print(f"  Saved full match rankings → {out}")
