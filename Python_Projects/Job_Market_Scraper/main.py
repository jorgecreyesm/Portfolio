"""
Entry point — run individual pipeline stages or the full pipeline.

Usage:
    python main.py init                      # create DB tables
    python main.py scrape                    # scrape Indeed
    python main.py clean                     # detect agencies + extract skills
    python main.py analyze                   # print summary report
    python main.py run-all                   # init → scrape → clean → analyze
"""
import argparse

from database.connection import init_db
from database.models import (
    insert_posting_with_skills, fetch_all_postings, url_exists
)
from scraper.jobspy_scraper import fetch_jobs
from cleaning.skills_normalizer import extract_skills
from cleaning.agency_detector import detect_agency
from cleaning.job_filter import filter_job
from analysis.summary import run_summary
from matching.matcher import run_matcher
from config import SEARCH_QUERIES, SEARCH_LOCATION, PAGES_PER_QUERY, REQUEST_DELAY


def cmd_init():
    init_db()


def cmd_scrape():
    total_new = total_filtered = total_dupes = 0
    rejection_reasons: dict[str, int] = {}

    for query in SEARCH_QUERIES:
        print(f"\nQuery: {query!r}")
        results = fetch_jobs(query, location=SEARCH_LOCATION, results=PAGES_PER_QUERY * 15)
        print(f"  Retrieved {len(results)} listings")
        for job in results:
            url = job.get("source_url", "")
            if url and url_exists(url):
                total_dupes += 1
                continue

            fr = filter_job(job)
            if not fr["pass"]:
                total_filtered += 1
                bucket = fr["reason"].split(":")[0]
                rejection_reasons[bucket] = rejection_reasons.get(bucket, 0) + 1
                continue

            job["filter_score"] = fr["score"]
            job["filter_tier"]  = fr["tier"]

            is_agency, reason = detect_agency(
                job.get("company_name", ""), job.get("raw_description", "")
            )
            job["is_staffing_agency"] = is_agency
            job["agency_flag_reason"] = reason
            skills = extract_skills(job.get("raw_description", ""))
            insert_posting_with_skills(job, skills)
            total_new += 1

    print(f"\nDone.")
    print(f"  Saved    : {total_new} new postings")
    print(f"  Filtered : {total_filtered} rejected by pre-filter")
    print(f"  Dupes    : {total_dupes} already in DB")
    if rejection_reasons:
        print("  Rejection breakdown:")
        for reason, count in sorted(rejection_reasons.items(), key=lambda x: -x[1]):
            print(f"    {count:>4}x  {reason}")


def cmd_clean():
    """Re-run agency detection and skill extraction on all postings."""
    from database.connection import get_conn
    postings = fetch_all_postings()
    updated = 0
    for job in postings:
        is_agency, reason = detect_agency(
            job.get("company_name", ""), job.get("raw_description", "")
        )
        skills = extract_skills(job.get("raw_description", ""))

        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                """UPDATE job_postings
                   SET is_staffing_agency = %s, agency_flag_reason = %s
                   WHERE id = %s""",
                (is_agency, reason, job["id"])
            )
            cur.execute("DELETE FROM job_skills WHERE job_id = %s", (job["id"],))
            if skills:
                rows = [(job["id"], s["raw"], s["normalized"], s["category"]) for s in skills]
                cur.executemany(
                    "INSERT INTO job_skills (job_id, skill_raw, skill_normalized, skill_category) "
                    "VALUES (%s, %s, %s, %s)",
                    rows
                )
            conn.commit()
        updated += 1
    print(f"Cleaned {updated} postings.")


def cmd_analyze(save: bool = False):
    run_summary(save=save)


def main():
    parser = argparse.ArgumentParser(description="Job Market Scraper")
    parser.add_argument(
        "command",
        choices=["init", "scrape", "clean", "analyze", "match", "run-all"],
        help="Pipeline stage to run"
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save analysis report and cleaned data CSVs to reports/"
    )
    parser.add_argument(
        "--exclude-agency",
        action="store_true",
        help="Exclude staffing agency postings from match results"
    )
    args = parser.parse_args()

    if args.command == "init":
        cmd_init()
    elif args.command == "scrape":
        cmd_scrape()
    elif args.command == "clean":
        cmd_clean()
    elif args.command == "analyze":
        cmd_analyze(save=args.save)
    elif args.command == "match":
        run_matcher(save=args.save, exclude_agency=args.exclude_agency)
    elif args.command == "run-all":
        cmd_init()
        cmd_scrape()
        cmd_clean()
        cmd_analyze(save=args.save)
        run_matcher(save=args.save)


if __name__ == "__main__":
    main()
