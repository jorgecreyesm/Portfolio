import io
from datetime import date
from pathlib import Path

import pandas as pd
from tabulate import tabulate

from database.models import fetch_all_postings, fetch_all_skills

REPORTS_DIR = Path("reports")


def _build_report(df_jobs: pd.DataFrame, df_skills: pd.DataFrame) -> str:
    buf = io.StringIO()

    total        = len(df_jobs)
    agency_count = int(df_jobs["is_staffing_agency"].sum())
    direct_count = total - agency_count
    remote_count = int(df_jobs["is_remote"].sum())

    buf.write("=" * 60 + "\n")
    buf.write("  JOB MARKET ANALYSIS — Entry-Level DA / BA Postings\n")
    buf.write("=" * 60 + "\n")
    pct = lambda n: f"{n / total * 100:.1f}" if total else "0.0"

    buf.write(f"\nTotal postings scraped : {total}\n")
    buf.write(f"Direct employer        : {direct_count} ({pct(direct_count)}%)\n")
    buf.write(f"Staffing agency        : {agency_count} ({pct(agency_count)}%)\n")
    buf.write(f"Remote / hybrid        : {remote_count} ({pct(remote_count)}%)\n")

    if not df_skills.empty:
        buf.write("\n--- Top 15 Required Skills ---\n")
        top_skills = (
            df_skills.groupby("skill_normalized")
            .size()
            .sort_values(ascending=False)
            .head(15)
            .reset_index(name="count")
        )
        top_skills["% of postings"] = (top_skills["count"] / total * 100).round(1)
        buf.write(tabulate(top_skills, headers="keys", tablefmt="simple", showindex=False) + "\n")

        buf.write("\n--- Skills by Category ---\n")
        cat_counts = (
            df_skills.groupby("skill_category")
            .size()
            .sort_values(ascending=False)
            .reset_index(name="mentions")
        )
        buf.write(tabulate(cat_counts, headers="keys", tablefmt="simple", showindex=False) + "\n")

    salary_df = df_jobs.dropna(subset=["salary_min", "salary_max"]).copy()
    buf.write("\n--- Salary Ranges ---\n")
    if not salary_df.empty:
        for stype, grp in salary_df.groupby("salary_type"):
            label = "Hourly ($)" if stype == "hourly" else "Annual ($)"
            buf.write(f"\n  {label}\n")
            buf.write(f"    Min   : ${grp['salary_min'].min():,.0f}\n")
            buf.write(f"    Median: ${grp['salary_min'].median():,.0f} – ${grp['salary_max'].median():,.0f}\n")
            buf.write(f"    Max   : ${grp['salary_max'].max():,.0f}\n")
            buf.write(f"    Count : {len(grp)} postings with salary data\n")
    else:
        buf.write("  No salary data available.\n")

    if not df_skills.empty:
        df_merged = df_skills.merge(
            df_jobs[["id", "is_staffing_agency"]], left_on="job_id", right_on="id"
        )
        buf.write("\n--- Top Skills: Direct Employers vs Staffing Agencies ---\n")
        for is_agency, label in [(False, "Direct Employers"), (True, "Staffing Agencies")]:
            subset = (
                df_merged[df_merged["is_staffing_agency"] == is_agency]
                .groupby("skill_normalized")
                .size()
                .sort_values(ascending=False)
                .head(8)
                .reset_index(name="count")
            )
            buf.write(f"\n  {label}:\n")
            buf.write(tabulate(subset, headers="keys", tablefmt="simple", showindex=False) + "\n")

    buf.write("\n--- Top 10 Locations ---\n")
    loc = (
        df_jobs["location"]
        .value_counts()
        .head(10)
        .reset_index()
    )
    loc.columns = ["location", "count"]
    buf.write(tabulate(loc, headers="keys", tablefmt="simple", showindex=False) + "\n")

    buf.write("\n--- Filter Tier Breakdown ---\n")
    tier_counts = (
        df_jobs["filter_tier"].fillna("NONE")
        .value_counts()
        .reset_index()
    )
    tier_counts.columns = ["tier", "count"]
    tier_counts["% of total"] = (tier_counts["count"] / total * 100).round(1)
    buf.write(tabulate(tier_counts, headers="keys", tablefmt="simple", showindex=False) + "\n")

    buf.write("\n--- Top 15 Direct Employers ---\n")
    top_cos = (
        df_jobs[~df_jobs["is_staffing_agency"].fillna(False)]
        .groupby("company_name")
        .size()
        .sort_values(ascending=False)
        .head(15)
        .reset_index(name="postings")
    )
    buf.write(tabulate(top_cos, headers="keys", tablefmt="simple", showindex=False) + "\n")

    if "date_posted" in df_jobs.columns:
        buf.write("\n--- Job Freshness ---\n")
        today = pd.Timestamp.today().normalize()
        df_jobs["date_posted"] = pd.to_datetime(df_jobs["date_posted"], errors="coerce")
        fresh_1d = int((df_jobs["date_posted"] >= today - pd.Timedelta(days=1)).sum())
        fresh_3d = int((df_jobs["date_posted"] >= today - pd.Timedelta(days=3)).sum())
        fresh_7d = int((df_jobs["date_posted"] >= today - pd.Timedelta(days=7)).sum())
        unknown  = int(df_jobs["date_posted"].isna().sum())
        buf.write(f"  Posted within 1 day  : {fresh_1d:>4}\n")
        buf.write(f"  Posted within 3 days : {fresh_3d:>4}\n")
        buf.write(f"  Posted within 7 days : {fresh_7d:>4}\n")
        buf.write(f"  Older / unknown      : {unknown + (total - fresh_7d - unknown):>4}\n")

    if not salary_df.empty:
        buf.write("\n--- Salary: Remote vs On-Site (Annual) ---\n")
        annual_salary = salary_df[salary_df["salary_type"] == "annual"].copy()
        if not annual_salary.empty:
            annual_salary["midpoint"] = (annual_salary["salary_min"] + annual_salary["salary_max"]) / 2
            sal_compare = []
            for label, mask in [("Remote", annual_salary["is_remote"] == True),
                                 ("On-site", annual_salary["is_remote"] == False)]:
                grp = annual_salary[mask]
                if not grp.empty:
                    sal_compare.append({
                        "type":       label,
                        "count":      len(grp),
                        "median_mid": f"${grp['midpoint'].median():,.0f}",
                        "median_min": f"${grp['salary_min'].median():,.0f}",
                        "median_max": f"${grp['salary_max'].median():,.0f}",
                    })
            if sal_compare:
                buf.write(tabulate(sal_compare, headers="keys", tablefmt="simple", showindex=False) + "\n")

    buf.write("\n" + "=" * 60 + "\n")
    return buf.getvalue()


def _save_csv(df_jobs: pd.DataFrame, df_skills: pd.DataFrame, stamp: str):
    jobs_path = REPORTS_DIR / f"jobs_{stamp}.csv"
    df_jobs.to_csv(jobs_path, index=False)
    print(f"  Saved cleaned jobs data  → {jobs_path}")

    if not df_skills.empty:
        skills_path = REPORTS_DIR / f"skills_{stamp}.csv"
        df_skills.to_csv(skills_path, index=False)
        print(f"  Saved normalized skills  → {skills_path}")


def run_summary(save: bool = False):
    postings = fetch_all_postings()
    skills   = fetch_all_skills()

    if not postings:
        print("No data in database. Run scrape first.")
        return

    df_jobs   = pd.DataFrame(postings)
    df_skills = pd.DataFrame(skills)

    report = _build_report(df_jobs, df_skills)
    print(report)

    if save:
        stamp = date.today().isoformat()
        report_path = REPORTS_DIR / f"analysis_report_{stamp}.txt"
        report_path.write_text(report)
        print(f"  Saved analysis report    → {report_path}")
        _save_csv(df_jobs, df_skills, stamp)
