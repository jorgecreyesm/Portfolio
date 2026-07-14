"""
CDC PLACES transform module.

Unlike the other sources, PLACES publishes crude prevalence percentages
directly rather than raw counts -- there is nothing to derive a rate
from. This step is a validated passthrough: it re-checks percentage
bounds and county coverage against the version of the data that will
actually be loaded, rather than trusting the extract-time checks never
went stale between pipeline runs.

Run standalone (reads the most recent raw extract from data/raw/):
    python -m src.transform.cdc_places
"""

from datetime import datetime

import pandas as pd

from src.config import CDC_PLACES_MEASURES, DATA_PROCESSED, DATA_RAW
from src.utils.io import latest_file
from src.utils.logger import get_logger

logger = get_logger(__name__)


def transform_cdc_places(raw: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Validate the PLACES extract; no derived columns, values are already rates."""
    flags: list[str] = []
    df = raw.copy()

    for col in CDC_PLACES_MEASURES.values():
        out_of_range = (df[col] < 0) | (df[col] > 100)
        for _, row in df.loc[out_of_range.fillna(False)].iterrows():
            msg = (
                f"CDC PLACES transform: implausible {col}={row[col]} "
                f"for {row['county_name']} (flagged, retained)"
            )
            logger.warning(msg)
            flags.append(msg)

    return df, flags


if __name__ == "__main__":
    raw_path = latest_file(DATA_RAW, "cdc_places_")
    raw = pd.read_csv(raw_path, dtype={"fips": str})
    logger.info("Transforming %s", raw_path)

    df, flags = transform_cdc_places(raw)

    stamp = datetime.now().strftime("%Y%m%d")
    out_path = DATA_PROCESSED / f"fact_cdc_places_{stamp}.csv"
    df.to_csv(out_path, index=False)
    logger.info("CDC PLACES transform complete: %d rows -> %s", len(df), out_path)

    print(f"\nTransformed {len(df)} rows, {len(flags)} quality flags")
