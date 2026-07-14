"""
CHHS transform module.

Pivots the raw long-format death extract (one row per county-year-cause)
into one row per county-year, and derives a per-100k rate for every
cause by dividing against the matching county-year's ACS total
population. This is the one transform step with a cross-source
dependency -- it needs fact_acs to already be transformed -- so
pipeline.py must run the census transform before this one.

Run standalone (reads the most recent raw CHHS and ACS extracts from
data/raw/):
    python -m src.transform.chhs
"""

from datetime import datetime

import pandas as pd

from src.config import CHHS_CAUSE_CODES, DATA_PROCESSED, DATA_RAW
from src.utils.io import latest_file
from src.utils.logger import get_logger

logger = get_logger(__name__)

CAUSE_COLUMNS = list(CHHS_CAUSE_CODES.values())


def transform_chhs(raw: pd.DataFrame, population: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """
    Pivot the long-format CHHS extract to wide and derive per-100k rates.

    `population` must have columns fips, acs_year, total_population --
    typically fact_acs after the census transform step.
    """
    flags: list[str] = []

    wide = raw.pivot_table(
        index=["fips", "county_name", "death_year"],
        columns="cause",
        values="death_count",
        aggfunc="first",
    ).reset_index()
    wide.columns.name = None

    for col in CAUSE_COLUMNS:
        if col not in wide.columns:
            wide[col] = pd.NA

    pop_lookup = population[["fips", "acs_year", "total_population"]].rename(
        columns={"acs_year": "death_year"}
    )
    wide = wide.merge(pop_lookup, on=["fips", "death_year"], how="left")

    missing_pop = wide["total_population"].isna()
    for _, row in wide.loc[missing_pop].iterrows():
        msg = (
            f"CHHS transform {row['death_year']}: no matching ACS population for "
            f"{row['county_name']}, per-100k rates will be NULL"
        )
        logger.warning(msg)
        flags.append(msg)

    pop = wide["total_population"].where(wide["total_population"] > 0)
    for col in CAUSE_COLUMNS:
        rate_col = f"{col}_per_100k"
        wide[rate_col] = (wide[col] / pop * 100_000).round(2)

    ordered_cols = ["fips", "county_name", "death_year"]
    for col in CAUSE_COLUMNS:
        ordered_cols += [col, f"{col}_per_100k"]

    return wide[ordered_cols], flags


if __name__ == "__main__":
    raw_path = latest_file(DATA_RAW, "chhs_deaths_")
    acs_path = latest_file(DATA_PROCESSED, "fact_acs_")
    raw = pd.read_csv(raw_path, dtype={"fips": str})
    population = pd.read_csv(acs_path, dtype={"fips": str})
    logger.info("Transforming %s against population from %s", raw_path, acs_path)

    df, flags = transform_chhs(raw, population)

    stamp = datetime.now().strftime("%Y%m%d")
    out_path = DATA_PROCESSED / f"fact_chhs_deaths_{stamp}.csv"
    df.to_csv(out_path, index=False)
    logger.info("CHHS transform complete: %d rows -> %s", len(df), out_path)

    print(f"\nTransformed {len(df)} rows, {len(flags)} quality flags")
    cols = ["county_name", "death_year", "deaths_all_causes", "deaths_all_causes_per_100k"]
    print(df[cols].to_string(index=False))
