"""
CHHS extraction module.

Pulls county-level mortality counts (all leading causes of death) for the
seven Central Valley counties from the "Death Profiles by County" CKAN
dataset, validates the response, and writes one raw CSV per run to
data/raw/.

Design decisions worth noting for reviewers:
- No API key required (CKAN datastore_search on a public portal).
- Residence-based geography is used (deaths among county residents), to
  match the ACS population denominators death rates will be computed
  against in the transform step -- not occurrence-based (deaths that
  happened in the county regardless of where the decedent lived).
- Raw death counts are preserved as pulled; rates per 100k population are
  derived later in transform, once ACS population figures are available
  to divide by.
- CHHS suppresses death counts below a small-number threshold for
  privacy (Annotation_Code "1", "Cell suppressed for small numbers").
  These come back as NULL already and are logged, never dropped or
  imputed.

Run standalone:
    python -m src.extract.chhs
"""

from datetime import datetime

import pandas as pd

from src.config import (
    CENTRAL_VALLEY_COUNTIES,
    CHHS_CAUSE_CODES,
    CHHS_DEATH_RESOURCE_ID,
    CHHS_GEOGRAPHY_TYPE,
    CHHS_PORTAL_BASE_URL,
    CHHS_STRATA,
    CHHS_YEARS,
    DATA_RAW,
)
from src.utils.api_client import fetch_json
from src.utils.logger import get_logger

logger = get_logger(__name__)

DATASTORE_SEARCH_URL = f"{CHHS_PORTAL_BASE_URL}/datastore_search"

EXPECTED_ROW_COUNT = len(CENTRAL_VALLEY_COUNTIES) * len(CHHS_YEARS) * len(CHHS_CAUSE_CODES)


def _fetch() -> pd.DataFrame:
    """Fetch all cause-of-death counts for all seven counties and years in one request."""
    import json as _json

    filters = {
        "County": list(CENTRAL_VALLEY_COUNTIES.keys()),
        "Year": [str(y) for y in CHHS_YEARS],
        "Strata": CHHS_STRATA,
        "Geography_Type": CHHS_GEOGRAPHY_TYPE,
    }
    params = {
        "resource_id": CHHS_DEATH_RESOURCE_ID,
        "filters": _json.dumps(filters),
        "limit": 5000,
    }

    logger.info("Requesting CHHS death profiles for %d counties, %d years", len(CENTRAL_VALLEY_COUNTIES), len(CHHS_YEARS))
    raw = fetch_json(DATASTORE_SEARCH_URL, params=params, source="chhs")

    result = raw.get("result", {})
    records = result.get("records", [])
    if not records:
        logger.warning("CHHS: no data records returned")
    return pd.DataFrame(records)


def _clean_and_validate(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """
    Filter to configured causes, rename columns, coerce types, and run
    data quality checks. Returns the cleaned frame plus a list of
    human-readable quality flags for the run report.
    """
    flags: list[str] = []

    df = df[df["Cause"].isin(CHHS_CAUSE_CODES)].copy()
    df = df.rename(columns={
        "Year": "death_year",
        "County": "county_name",
        "Cause": "cause_code",
        "Count": "death_count_raw",
        "Annotation_Code": "annotation_code",
        "Annotation_Desc": "annotation_desc",
    })
    df["death_year"] = pd.to_numeric(df["death_year"], errors="coerce")

    # Check 1: expected row count (counties x years x causes)
    if len(df) != EXPECTED_ROW_COUNT:
        msg = f"CHHS: expected {EXPECTED_ROW_COUNT} rows, got {len(df)}"
        logger.warning(msg)
        flags.append(msg)

    # Check 2: all seven counties present
    missing = set(CENTRAL_VALLEY_COUNTIES) - set(df["county_name"])
    if missing:
        msg = f"CHHS: missing counties in response: {sorted(missing)}"
        logger.warning(msg)
        flags.append(msg)

    # Check 3: suppressed cells -> NULL, logged per occurrence
    suppressed_mask = df["annotation_code"].notna()
    for _, row in df.loc[suppressed_mask].iterrows():
        msg = (
            f"CHHS {row['death_year']}: {row['cause_code']} for "
            f"{row['county_name']} suppressed ({row['annotation_desc']}), set to NULL"
        )
        logger.warning(msg)
        flags.append(msg)

    df["death_count"] = pd.to_numeric(df["death_count_raw"], errors="coerce")

    # Check 4: negative counts are impossible
    neg_mask = df["death_count"] < 0
    for _, row in df.loc[neg_mask.fillna(False)].iterrows():
        msg = (
            f"CHHS {row['death_year']}: negative death count {row['death_count']} "
            f"for {row['cause_code']} in {row['county_name']} (flagged, retained)"
        )
        logger.warning(msg)
        flags.append(msg)

    # Check 5: cause-specific counts cannot exceed the all-cause total
    all_cause = df[df["cause_code"] == "ALL"][["county_name", "death_year", "death_count"]]
    all_cause = all_cause.rename(columns={"death_count": "all_cause_count"})
    merged = df.merge(all_cause, on=["county_name", "death_year"], how="left")
    exceeds = (merged["cause_code"] != "ALL") & (merged["death_count"] > merged["all_cause_count"])
    for _, row in merged.loc[exceeds.fillna(False)].iterrows():
        msg = (
            f"CHHS {row['death_year']}: {row['cause_code']} count exceeds all-cause "
            f"total for {row['county_name']} (flagged, retained)"
        )
        logger.warning(msg)
        flags.append(msg)

    df["fips"] = df["county_name"].map(
        {name: "06" + code for name, code in CENTRAL_VALLEY_COUNTIES.items()}
    )
    df["cause"] = df["cause_code"].map(CHHS_CAUSE_CODES)

    ordered = ["fips", "county_name", "death_year", "cause", "death_count"]
    return df[ordered], flags


def extract_chhs() -> tuple[pd.DataFrame, list[str]]:
    """
    Full CHHS extraction: leading causes of death for all seven counties
    and configured years, cleaned, validated, and written to data/raw/.
    Returns the cleaned dataframe (long format: one row per
    county-year-cause) and all quality flags.
    """
    raw = _fetch()
    clean, flags = _clean_and_validate(raw)
    logger.info("CHHS: %d rows, %d quality flags", len(clean), len(flags))

    stamp = datetime.now().strftime("%Y%m%d")
    out_path = DATA_RAW / f"chhs_deaths_{stamp}.csv"
    clean.to_csv(out_path, index=False)
    logger.info("CHHS extraction complete: %d rows -> %s", len(clean), out_path)

    return clean, flags


if __name__ == "__main__":
    df, flags = extract_chhs()
    print(f"\nExtracted {len(df)} county-year-cause rows across {df['death_year'].nunique()} years")
    print(f"Quality flags raised: {len(flags)}")
    print(df.head(20).to_string(index=False))
