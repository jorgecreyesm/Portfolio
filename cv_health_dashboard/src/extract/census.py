"""
Census Bureau ACS 5-Year extraction module.

Pulls detailed-table estimates for the seven Central Valley counties
across multiple vintages, validates the response, and writes one raw
CSV per run to data/raw/.

Design decisions worth noting for reviewers:
- Raw values are preserved as pulled; derived rates (poverty %, education
  attainment %, unemployment %) are computed later in the transform step
  so every number in the database can be traced back to a raw API value.
- Anomalies are flagged and logged, never silently dropped. The Census
  API uses sentinel values (large negatives like -666666666) for
  suppressed or unavailable estimates; these are converted to NULL and
  each occurrence is logged with county, year, and variable.

Run standalone:
    python -m src.extract.census
"""

from datetime import datetime

import pandas as pd

from src.config import (
    ACS_DATASET,
    ACS_VARIABLES,
    ACS_YEARS,
    CA_STATE_FIPS,
    CENSUS_API_KEY,
    CENSUS_BASE_URL,
    CENTRAL_VALLEY_COUNTIES,
    DATA_RAW,
)
from src.utils.api_client import fetch_json
from src.utils.logger import get_logger

logger = get_logger(__name__)

# ACS sentinel values that mean "no estimate available", not real data.
# Anything at or below this threshold is treated as a sentinel.
SENTINEL_THRESHOLD = -222222222

EXPECTED_COUNTY_COUNT = len(CENTRAL_VALLEY_COUNTIES)


def _build_url(year: int) -> str:
    return f"{CENSUS_BASE_URL}/{year}/{ACS_DATASET}"


def _fetch_year(year: int) -> pd.DataFrame:
    """Fetch all configured variables for all seven counties for one vintage."""
    county_codes = ",".join(CENTRAL_VALLEY_COUNTIES.values())
    params = {
        "get": "NAME," + ",".join(ACS_VARIABLES.keys()),
        "for": f"county:{county_codes}",
        "in": f"state:{CA_STATE_FIPS}",
        "key": CENSUS_API_KEY,
    }

    logger.info("Requesting ACS %s vintage %d", ACS_DATASET, year)
    raw = fetch_json(_build_url(year), params=params, source="census")

    # Census returns a list of lists: first row is the header
    df = pd.DataFrame(raw[1:], columns=raw[0])
    df["acs_year"] = year
    return df


def _clean_and_validate(df: pd.DataFrame, year: int) -> tuple[pd.DataFrame, list[str]]:
    """
    Rename columns, coerce types, replace sentinels with NULL, and run
    data quality checks. Returns the cleaned frame plus a list of
    human-readable quality flags for the run report.
    """
    flags: list[str] = []

    df = df.rename(columns=ACS_VARIABLES)
    df = df.rename(columns={"NAME": "county_name", "state": "state_fips", "county": "county_fips"})
    df["county_name"] = df["county_name"].str.replace(" County, California", "", regex=False)
    df["fips"] = df["state_fips"] + df["county_fips"]

    # Check 1: all seven counties present
    missing = set(CENTRAL_VALLEY_COUNTIES) - set(df["county_name"])
    if missing:
        msg = f"ACS {year}: missing counties in response: {sorted(missing)}"
        logger.warning(msg)
        flags.append(msg)

    # Check 2: no unexpected extra rows
    if len(df) != EXPECTED_COUNTY_COUNT:
        msg = f"ACS {year}: expected {EXPECTED_COUNTY_COUNT} rows, got {len(df)}"
        logger.warning(msg)
        flags.append(msg)

    # Coerce numeric columns and handle sentinels
    value_cols = list(ACS_VARIABLES.values())
    for col in value_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

        # Check 3: sentinel values -> NULL, logged per occurrence
        sentinel_mask = df[col] <= SENTINEL_THRESHOLD
        for _, row in df.loc[sentinel_mask].iterrows():
            msg = (
                f"ACS {year}: sentinel value in {col} for "
                f"{row['county_name']} (set to NULL)"
            )
            logger.warning(msg)
            flags.append(msg)
        df.loc[sentinel_mask, col] = pd.NA

        # Check 4: negative values in count/median columns are impossible
        neg_mask = df[col] < 0
        for _, row in df.loc[neg_mask].iterrows():
            msg = (
                f"ACS {year}: negative value {row[col]} in {col} for "
                f"{row['county_name']} (flagged, retained)"
            )
            logger.warning(msg)
            flags.append(msg)

    # Check 5: sanity range on total population. Central Valley counties
    # run from roughly 150k (Kings, Madera) to about 1M (Fresno). Values
    # far outside that range signal a parsing or API problem.
    pop_mask = (df["total_population"] < 50_000) | (df["total_population"] > 2_000_000)
    for _, row in df.loc[pop_mask.fillna(False)].iterrows():
        msg = (
            f"ACS {year}: implausible population {row['total_population']} "
            f"for {row['county_name']} (flagged, retained)"
        )
        logger.warning(msg)
        flags.append(msg)

    # Check 6: subgroup counts cannot exceed their universe
    if {"poverty_below_count", "poverty_universe"}.issubset(df.columns):
        bad = df["poverty_below_count"] > df["poverty_universe"]
        for _, row in df.loc[bad.fillna(False)].iterrows():
            msg = (
                f"ACS {year}: poverty count exceeds universe for "
                f"{row['county_name']} (flagged, retained)"
            )
            logger.warning(msg)
            flags.append(msg)

    ordered = ["fips", "county_name", "acs_year"] + value_cols
    return df[ordered], flags


def extract_census() -> tuple[pd.DataFrame, list[str]]:
    """
    Full Census extraction: all vintages, cleaned, validated, and written
    to data/raw/. Returns the combined dataframe and all quality flags.
    """
    if not CENSUS_API_KEY:
        raise RuntimeError(
            "CENSUS_API_KEY is not set. Copy .env.example to .env and add your key."
        )

    frames = []
    all_flags: list[str] = []

    for year in ACS_YEARS:
        raw = _fetch_year(year)
        clean, flags = _clean_and_validate(raw, year)
        frames.append(clean)
        all_flags.extend(flags)
        logger.info("ACS %d: %d rows, %d quality flags", year, len(clean), len(flags))

    combined = pd.concat(frames, ignore_index=True)

    stamp = datetime.now().strftime("%Y%m%d")
    out_path = DATA_RAW / f"census_acs5_{stamp}.csv"
    combined.to_csv(out_path, index=False)
    logger.info("Census extraction complete: %d rows -> %s", len(combined), out_path)

    return combined, all_flags


if __name__ == "__main__":
    df, flags = extract_census()
    print(f"\nExtracted {len(df)} county-year rows across {df['acs_year'].nunique()} vintages")
    print(f"Quality flags raised: {len(flags)}")
    print(df.head(10).to_string(index=False))
