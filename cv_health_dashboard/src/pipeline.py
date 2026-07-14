"""
Master pipeline orchestration script.

Runs the full ETL sequence in dependency order: extract all four
sources, transform them, load into PostgreSQL, and write a per-run
report. Transform functions are pure (dataframe in, dataframe out) so
this script owns writing the processed CSVs -- the load stage reads
those back from disk, same as when each stage is run standalone.

Census must transform before CHHS: CHHS derives per-100k death rates
from ACS population figures, so fact_acs has to exist first.

Run:
    python -m src.pipeline
"""

from datetime import datetime

import pandas as pd

from src.config import DATA_PROCESSED, REPORTS_DIR
from src.extract.cdc_places import extract_cdc_places
from src.extract.census import extract_census
from src.extract.chhs import extract_chhs
from src.extract.nass import extract_nass
from src.load.postgres import load_all
from src.transform.cdc_places import transform_cdc_places
from src.transform.census import transform_census
from src.transform.chhs import transform_chhs
from src.transform.nass import transform_nass
from src.utils.logger import current_log_file, get_logger

logger = get_logger(__name__)


def _write_processed(df: pd.DataFrame, name: str, stamp: str) -> None:
    out_path = DATA_PROCESSED / f"{name}_{stamp}.csv"
    df.to_csv(out_path, index=False)
    logger.info("Wrote %s (%d rows)", out_path, len(df))


def run() -> list[dict]:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stage_results: list[dict] = []

    def record(stage: str, source: str, rows: int, flags: list[str]) -> None:
        stage_results.append({"stage": stage, "source": source, "rows": rows, "flags": len(flags)})
        logger.info("%s/%s: %d rows, %d flags", stage, source, rows, len(flags))

    logger.info("=== Pipeline run started ===")

    # --- Extract ---
    census_raw, census_extract_flags = extract_census()
    record("extract", "census", len(census_raw), census_extract_flags)

    nass_raw, nass_extract_flags = extract_nass()
    record("extract", "nass", len(nass_raw), nass_extract_flags)

    cdc_raw, cdc_extract_flags = extract_cdc_places()
    record("extract", "cdc_places", len(cdc_raw), cdc_extract_flags)

    chhs_raw, chhs_extract_flags = extract_chhs()
    record("extract", "chhs", len(chhs_raw), chhs_extract_flags)

    # --- Transform ---
    census_fact, census_transform_flags = transform_census(census_raw)
    record("transform", "census", len(census_fact), census_transform_flags)
    _write_processed(census_fact, "fact_acs", stamp)

    nass_fact, nass_transform_flags = transform_nass(nass_raw)
    record("transform", "nass", len(nass_fact), nass_transform_flags)
    _write_processed(nass_fact, "fact_nass", stamp)

    cdc_fact, cdc_transform_flags = transform_cdc_places(cdc_raw)
    record("transform", "cdc_places", len(cdc_fact), cdc_transform_flags)
    _write_processed(cdc_fact, "fact_cdc_places", stamp)

    chhs_fact, chhs_transform_flags = transform_chhs(chhs_raw, census_fact)
    record("transform", "chhs", len(chhs_fact), chhs_transform_flags)
    _write_processed(chhs_fact, "fact_chhs_deaths", stamp)

    # --- Load ---
    load_counts = load_all()
    for table, n in load_counts.items():
        stage_results.append({"stage": "load", "source": table, "rows": n, "flags": 0})

    logger.info("=== Pipeline run complete ===")
    _write_report(stage_results, stamp)
    return stage_results


def _write_report(stage_results: list[dict], stamp: str) -> None:
    summary_df = pd.DataFrame(stage_results)
    summary_path = REPORTS_DIR / f"run_summary_{stamp}.csv"
    summary_df.to_csv(summary_path, index=False)

    total_flags = summary_df["flags"].sum()
    lines = [
        f"# Pipeline run report -- {stamp}",
        "",
        f"Total quality flags raised: {total_flags}",
        f"Log file: {current_log_file()}",
        "",
        "| Stage | Source | Rows | Flags |",
        "|---|---|---|---|",
    ]
    for row in stage_results:
        lines.append(f"| {row['stage']} | {row['source']} | {row['rows']} | {row['flags']} |")

    report_path = REPORTS_DIR / f"run_report_{stamp}.md"
    report_path.write_text("\n".join(lines) + "\n")

    logger.info("Report written: %s, %s", summary_path, report_path)


if __name__ == "__main__":
    results = run()
    print("\nPipeline run complete.")
    for row in results:
        print(f"  {row['stage']:10s} {row['source']:14s} rows={row['rows']:4d} flags={row['flags']}")
