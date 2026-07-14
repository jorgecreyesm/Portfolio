"""
NASS transform module.

Pivots the raw long-format extract (one row per county-year-variable)
into one row per county-year, and derives two per-farm averages that
aren't published directly by Census of Agriculture: average sale value
per farm and average farm size.

Run standalone (reads the most recent raw extract from data/raw/):
    python -m src.transform.nass
"""

from datetime import datetime

import pandas as pd

from src.config import DATA_PROCESSED, DATA_RAW, NASS_VARIABLES
from src.utils.io import latest_file
from src.utils.logger import get_logger

logger = get_logger(__name__)


def transform_nass(raw: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Pivot the long-format NASS extract to wide and derive per-farm averages."""
    flags: list[str] = []

    wide = raw.pivot_table(
        index=["fips", "county_name", "nass_year"],
        columns="variable",
        values="value",
        aggfunc="first",
    ).reset_index()
    wide.columns.name = None

    for col in NASS_VARIABLES.values():
        if col not in wide.columns:
            wide[col] = pd.NA

    farm_count = wide["farm_operations_count"].where(wide["farm_operations_count"] > 0)
    wide["avg_sales_per_farm"] = (wide["total_ag_sales"] / farm_count).round(2)
    wide["avg_farm_size_acres"] = (wide["total_farm_land_acres"] / farm_count).round(2)

    # Sanity check: derived averages should be positive and finite
    for col in ["avg_sales_per_farm", "avg_farm_size_acres"]:
        bad = wide[col].notna() & (wide[col] <= 0)
        for _, row in wide.loc[bad].iterrows():
            msg = (
                f"NASS transform {row['nass_year']}: non-positive {col}={row[col]} "
                f"for {row['county_name']} (flagged, retained)"
            )
            logger.warning(msg)
            flags.append(msg)

    return wide, flags


if __name__ == "__main__":
    raw_path = latest_file(DATA_RAW, "nass_census_ag_")
    raw = pd.read_csv(raw_path, dtype={"fips": str})
    logger.info("Transforming %s", raw_path)

    df, flags = transform_nass(raw)

    stamp = datetime.now().strftime("%Y%m%d")
    out_path = DATA_PROCESSED / f"fact_nass_{stamp}.csv"
    df.to_csv(out_path, index=False)
    logger.info("NASS transform complete: %d rows -> %s", len(df), out_path)

    print(f"\nTransformed {len(df)} rows, {len(flags)} quality flags")
    print(df.to_string(index=False))
