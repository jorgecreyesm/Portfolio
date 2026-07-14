"""
Census ACS transform module.

Takes the raw, validated ACS extract and derives the rate columns that
fact_acs stores: poverty rate, education attainment shares, homeownership
rate, and unemployment rate. Raw counts pass through unchanged so every
derived number can be traced back to its source columns.

Run standalone (reads the most recent raw extract from data/raw/):
    python -m src.transform.census
"""

from datetime import datetime

import pandas as pd

from src.config import CPI_BASE_YEAR, CPI_U_ANNUAL, DATA_PROCESSED, DATA_RAW
from src.utils.io import latest_file
from src.utils.logger import get_logger

logger = get_logger(__name__)


def _rate(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """Percentage, NULL (not zero) when the denominator is missing or zero."""
    result = (numerator / denominator * 100).round(2)
    return result.where(denominator > 0)


def _validate_rate(df: pd.DataFrame, col: str, flags: list[str], year_col: str = "acs_year") -> None:
    out_of_range = (df[col] < 0) | (df[col] > 100)
    for _, row in df.loc[out_of_range.fillna(False)].iterrows():
        msg = (
            f"ACS transform {row[year_col]}: implausible {col}={row[col]} "
            f"for {row['county_name']} (flagged, retained)"
        )
        logger.warning(msg)
        flags.append(msg)


def transform_census(raw: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Derive rate columns from a raw ACS extract dataframe."""
    flags: list[str] = []
    df = raw.copy()

    df["poverty_rate"] = _rate(df["poverty_below_count"], df["poverty_universe"])
    df["bachelors_or_higher_pct"] = _rate(
        df["edu_bachelors"] + df["edu_masters"] + df["edu_professional"] + df["edu_doctorate"],
        df["edu_universe_25plus"],
    )
    df["advanced_degree_pct"] = _rate(
        df["edu_masters"] + df["edu_professional"] + df["edu_doctorate"],
        df["edu_universe_25plus"],
    )
    df["homeownership_rate"] = _rate(df["housing_owner_occupied"], df["housing_units_occupied"])
    df["unemployment_rate"] = _rate(df["unemployed_count"], df["civilian_labor_force"])

    # Deflate nominal income to constant CPI_BASE_YEAR dollars:
    #   real = nominal * CPI(base) / CPI(year)
    # A year with no CPI entry gets a NULL deflator and NULL real income,
    # logged, rather than a silently wrong number.
    base_cpi = CPI_U_ANNUAL[CPI_BASE_YEAR]
    deflator = df["acs_year"].map(lambda y: base_cpi / CPI_U_ANNUAL[y] if y in CPI_U_ANNUAL else pd.NA)
    missing_cpi = deflator.isna()
    for year in sorted(df.loc[missing_cpi, "acs_year"].unique()):
        msg = f"ACS transform: no CPI-U entry for {year}, real income set to NULL"
        logger.warning(msg)
        flags.append(msg)

    deflator_num = pd.to_numeric(deflator, errors="coerce")
    df["median_household_income_real"] = (df["median_household_income"] * deflator_num).round()
    df["per_capita_income_real"] = (df["per_capita_income"] * deflator_num).round()

    for col in ["poverty_rate", "bachelors_or_higher_pct", "advanced_degree_pct", "homeownership_rate", "unemployment_rate"]:
        _validate_rate(df, col, flags)

    return df, flags


if __name__ == "__main__":
    raw_path = latest_file(DATA_RAW, "census_acs5_")
    raw = pd.read_csv(raw_path, dtype={"fips": str})
    logger.info("Transforming %s", raw_path)

    df, flags = transform_census(raw)

    stamp = datetime.now().strftime("%Y%m%d")
    out_path = DATA_PROCESSED / f"fact_acs_{stamp}.csv"
    df.to_csv(out_path, index=False)
    logger.info("Census transform complete: %d rows -> %s", len(df), out_path)

    print(f"\nTransformed {len(df)} rows, {len(flags)} quality flags")
    cols = ["county_name", "acs_year", "poverty_rate", "bachelors_or_higher_pct", "homeownership_rate", "unemployment_rate"]
    print(df[cols].to_string(index=False))
