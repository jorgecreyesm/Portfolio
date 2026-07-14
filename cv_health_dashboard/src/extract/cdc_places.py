"""
CDC PLACES extraction module.

Pulls county-level chronic disease, health behavior, and preventive care
estimates for the seven Central Valley counties from the Socrata API,
validates the response, and writes one raw CSV per run to data/raw/.

Design decisions worth noting for reviewers:
- No API key required (Socrata public dataset).
- Unlike ACS/NASS, PLACES publishes a single current-vintage snapshot per
  release rather than a year-over-year time series -- each row is one
  county's latest modeled estimate. CDC_PLACES_RELEASE_YEAR in config
  records which release this is, for provenance in the database.
- Values are model-based small-area estimates (crude prevalence, not
  age-adjusted), so they're comparable across counties but should not be
  read as direct measurements -- see the README's Limitations section.
- Socrata returns null for county-measure combinations without enough
  survey data to model; these are logged, not silently dropped.

Run standalone:
    python -m src.extract.cdc_places
"""

from datetime import datetime

import pandas as pd

from src.config import (
    CDC_PLACES_BASE_URL,
    CDC_PLACES_MEASURES,
    CDC_PLACES_RELEASE_YEAR,
    CENTRAL_VALLEY_COUNTIES,
    COUNTY_FIPS_5,
    DATA_RAW,
)
from src.utils.api_client import fetch_json
from src.utils.logger import get_logger

logger = get_logger(__name__)

EXPECTED_COUNTY_COUNT = len(CENTRAL_VALLEY_COUNTIES)


def _fetch() -> pd.DataFrame:
    """Fetch all configured measures for all seven counties in one request."""
    fips_list = ",".join(f"'{f}'" for f in COUNTY_FIPS_5.values())
    fields = ["countyfips", "countyname", "totalpopulation", "totalpop18plus"]
    fields += list(CDC_PLACES_MEASURES.keys())

    params = {
        "$select": ",".join(fields),
        "$where": f"countyfips in ({fips_list})",
        "$limit": 50,
    }

    logger.info("Requesting CDC PLACES measures for %d counties", EXPECTED_COUNTY_COUNT)
    raw = fetch_json(CDC_PLACES_BASE_URL, params=params, source="cdc_places")
    return pd.DataFrame(raw)


def _clean_and_validate(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """
    Rename columns, coerce types, and run data quality checks. Returns the
    cleaned frame plus a list of human-readable quality flags for the run
    report.
    """
    flags: list[str] = []

    df = df.rename(columns=CDC_PLACES_MEASURES)
    df = df.rename(columns={
        "countyfips": "fips",
        "countyname": "county_name",
        "totalpopulation": "total_population",
        "totalpop18plus": "total_population_18plus",
    })
    df["release_year"] = CDC_PLACES_RELEASE_YEAR

    # Check 1: all seven counties present
    missing = set(CENTRAL_VALLEY_COUNTIES) - set(df["county_name"])
    if missing:
        msg = f"CDC PLACES: missing counties in response: {sorted(missing)}"
        logger.warning(msg)
        flags.append(msg)

    # Check 2: no unexpected extra rows
    if len(df) != EXPECTED_COUNTY_COUNT:
        msg = f"CDC PLACES: expected {EXPECTED_COUNTY_COUNT} rows, got {len(df)}"
        logger.warning(msg)
        flags.append(msg)

    # Coerce numeric columns
    numeric_cols = ["total_population", "total_population_18plus"] + list(CDC_PLACES_MEASURES.values())
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

        # Check 3: missing modeled estimates, logged per occurrence
        null_mask = df[col].isna()
        for _, row in df.loc[null_mask].iterrows():
            msg = f"CDC PLACES: no modeled estimate for {col} in {row['county_name']} (NULL)"
            logger.warning(msg)
            flags.append(msg)

    # Check 4: crude prevalence measures must fall in [0, 100]
    measure_cols = list(CDC_PLACES_MEASURES.values())
    for col in measure_cols:
        out_of_range = (df[col] < 0) | (df[col] > 100)
        for _, row in df.loc[out_of_range.fillna(False)].iterrows():
            msg = (
                f"CDC PLACES: implausible value {row[col]} in {col} for "
                f"{row['county_name']} (flagged, retained)"
            )
            logger.warning(msg)
            flags.append(msg)

    # Check 5: sanity range on total population, same bounds used for ACS
    pop_mask = (df["total_population"] < 50_000) | (df["total_population"] > 2_000_000)
    for _, row in df.loc[pop_mask.fillna(False)].iterrows():
        msg = (
            f"CDC PLACES: implausible population {row['total_population']} "
            f"for {row['county_name']} (flagged, retained)"
        )
        logger.warning(msg)
        flags.append(msg)

    ordered = ["fips", "county_name", "release_year", "total_population", "total_population_18plus"] + measure_cols
    return df[ordered], flags


def extract_cdc_places() -> tuple[pd.DataFrame, list[str]]:
    """
    Full CDC PLACES extraction: all configured measures for all seven
    counties, cleaned, validated, and written to data/raw/. Returns the
    cleaned dataframe and all quality flags.
    """
    raw = _fetch()
    clean, flags = _clean_and_validate(raw)
    logger.info("CDC PLACES: %d rows, %d quality flags", len(clean), len(flags))

    stamp = datetime.now().strftime("%Y%m%d")
    out_path = DATA_RAW / f"cdc_places_{stamp}.csv"
    clean.to_csv(out_path, index=False)
    logger.info("CDC PLACES extraction complete: %d rows -> %s", len(clean), out_path)

    return clean, flags


if __name__ == "__main__":
    df, flags = extract_cdc_places()
    print(f"\nExtracted {len(df)} county rows, release year {CDC_PLACES_RELEASE_YEAR}")
    print(f"Quality flags raised: {len(flags)}")
    print(df.to_string(index=False))
