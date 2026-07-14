"""
USDA NASS Quick Stats extraction module.

Pulls Census of Agriculture county-level totals (farm land value, acreage,
sales, farm counts) for the seven Central Valley counties, validates the
response, and writes one raw CSV per run to data/raw/.

Design decisions worth noting for reviewers:
- County-level agricultural *totals* only exist in the Census of
  Agriculture, which runs every 5 years (2012, 2017, 2022), unlike the
  annual ACS survey. NASS_YEARS in config reflects that.
- One request per variable (short_desc) is made, with all seven counties
  and all three census years filtered via repeated query params (NASS's
  API treats repeated keys as OR), rather than one request per
  county-year, to stay well under the 50,000-record response cap.
- NASS uses disclosure/suppression flags instead of sentinel numbers:
  "(D)" = withheld to avoid disclosing individual operations, "(Z)" =
  effectively zero, "(NA)" = not applicable, "(L)" = below reporting
  threshold. These are converted to NULL and logged, never dropped.

Run standalone:
    python -m src.extract.nass
"""

from datetime import datetime

import pandas as pd

from src.config import (
    CENTRAL_VALLEY_COUNTIES,
    DATA_RAW,
    NASS_API_KEY,
    NASS_BASE_URL,
    NASS_DEFAULT_DOMAIN,
    NASS_DOMAIN_OVERRIDES,
    NASS_SECTOR_DESC,
    NASS_SOURCE_DESC,
    NASS_VARIABLES,
    NASS_YEARS,
)
from src.utils.api_client import fetch_json
from src.utils.logger import get_logger

logger = get_logger(__name__)

# NASS suppression/disclosure flags that mean "no numeric estimate", not
# real data. Mapped to a short reason for the quality-flag log line.
SUPPRESSION_FLAGS = {
    "(D)": "withheld to avoid disclosing individual operations",
    "(Z)": "effectively zero",
    "(NA)": "not available",
    "(L)": "below reporting threshold",
}

EXPECTED_COUNTY_COUNT = len(CENTRAL_VALLEY_COUNTIES)


def _fetch_variable(short_desc: str) -> pd.DataFrame:
    """Fetch one variable for all seven counties across all census years."""
    params = {
        "key": NASS_API_KEY,
        "short_desc": short_desc,
        "source_desc": NASS_SOURCE_DESC,
        "sector_desc": NASS_SECTOR_DESC,
        "agg_level_desc": "COUNTY",
        "state_alpha": "CA",
        "county_ansi": list(CENTRAL_VALLEY_COUNTIES.values()),
        "year": [str(y) for y in NASS_YEARS],
        "format": "JSON",
    }

    domain = NASS_DOMAIN_OVERRIDES.get(short_desc, NASS_DEFAULT_DOMAIN)
    if domain is not None:
        params["domain_desc"] = domain

    logger.info("Requesting NASS variable: %s", short_desc)
    raw = fetch_json(NASS_BASE_URL, params=params, source="nass")

    records = raw.get("data", [])
    if not records:
        logger.warning("NASS: no data records returned for %s", short_desc)
        return pd.DataFrame(columns=["county_name", "county_ansi", "year", "Value"])

    df = pd.DataFrame(records)
    df["variable"] = short_desc
    return df


def _clean_and_validate(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """
    Rename columns, coerce types, replace suppression flags with NULL,
    and run data quality checks. Returns the cleaned frame plus a list of
    human-readable quality flags for the run report.
    """
    flags: list[str] = []

    df = df.rename(columns={
        "county_name": "county_name_raw",
        "county_ansi": "county_fips",
        "year": "nass_year",
        "Value": "value_raw",
    })
    df["county_name"] = df["county_name_raw"].str.title()
    df["fips"] = "06" + df["county_fips"]
    df["nass_year"] = pd.to_numeric(df["nass_year"], errors="coerce")

    # Check 1: flag suppressed/non-numeric values, convert to NULL
    def _parse_value(raw_value, county, year, variable):
        if raw_value in SUPPRESSION_FLAGS:
            msg = (
                f"NASS {year}: {variable} for {county} suppressed "
                f"({raw_value} - {SUPPRESSION_FLAGS[raw_value]}), set to NULL"
            )
            logger.warning(msg)
            flags.append(msg)
            return pd.NA
        cleaned = str(raw_value).replace(",", "")
        try:
            return float(cleaned)
        except ValueError:
            msg = f"NASS {year}: unparseable value '{raw_value}' for {variable} in {county}, set to NULL"
            logger.warning(msg)
            flags.append(msg)
            return pd.NA

    df["value"] = [
        _parse_value(row.value_raw, row.county_name, row.nass_year, row.variable)
        for row in df.itertuples()
    ]

    # Check 2: negative values are impossible for these totals
    neg_mask = df["value"] < 0
    for _, row in df.loc[neg_mask.fillna(False)].iterrows():
        msg = (
            f"NASS {row['nass_year']}: negative value {row['value']} in "
            f"{row['variable']} for {row['county_name']} (flagged, retained)"
        )
        logger.warning(msg)
        flags.append(msg)

    return df[["fips", "county_name", "nass_year", "variable", "value"]], flags


def _check_coverage(wide: pd.DataFrame) -> list[str]:
    """All seven counties should appear for each census year, per variable."""
    flags: list[str] = []
    for year in NASS_YEARS:
        present = set(wide.loc[wide["nass_year"] == year, "county_name"])
        missing = set(CENTRAL_VALLEY_COUNTIES) - present
        if missing:
            msg = f"NASS {year}: missing counties in response: {sorted(missing)}"
            logger.warning(msg)
            flags.append(msg)
    return flags


def extract_nass() -> tuple[pd.DataFrame, list[str]]:
    """
    Full NASS extraction: all configured variables, all census years,
    cleaned, validated, and written to data/raw/. Returns the combined
    dataframe (long format: one row per county-year-variable) and all
    quality flags.
    """
    if not NASS_API_KEY:
        raise RuntimeError(
            "NASS_API_KEY is not set. Copy .env.example to .env and add your key."
        )

    frames = []
    all_flags: list[str] = []

    for short_desc in NASS_VARIABLES:
        raw = _fetch_variable(short_desc)
        if raw.empty:
            continue
        clean, flags = _clean_and_validate(raw)
        frames.append(clean)
        all_flags.extend(flags)
        logger.info(
            "NASS %s: %d rows, %d quality flags", short_desc, len(clean), len(flags)
        )

    combined = pd.concat(frames, ignore_index=True)
    combined["variable"] = combined["variable"].map(NASS_VARIABLES)

    all_flags.extend(_check_coverage(combined))

    stamp = datetime.now().strftime("%Y%m%d")
    out_path = DATA_RAW / f"nass_census_ag_{stamp}.csv"
    combined.to_csv(out_path, index=False)
    logger.info("NASS extraction complete: %d rows -> %s", len(combined), out_path)

    return combined, all_flags


if __name__ == "__main__":
    df, flags = extract_nass()
    print(f"\nExtracted {len(df)} county-year-variable rows across {df['nass_year'].nunique()} census years")
    print(f"Quality flags raised: {len(flags)}")
    print(df.head(15).to_string(index=False))
