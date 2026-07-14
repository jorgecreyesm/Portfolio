"""
PostgreSQL load module.

Upserts dim_county and all four fact tables from the latest processed
CSVs in data/processed/. Every load is idempotent -- rerunning the
pipeline for the same county-year overwrites that row rather than
duplicating it, via INSERT ... ON CONFLICT DO UPDATE keyed on each
table's primary key.

Run standalone (loads the most recent processed CSVs from data/processed/):
    python -m src.load.postgres
"""

from sqlalchemy import create_engine, text

from src.config import (
    CENTRAL_VALLEY_COUNTIES,
    CPI_BASE_YEAR,
    CPI_U_ANNUAL,
    DATA_PROCESSED,
    DB_CONFIG,
)
from src.utils.io import latest_file
from src.utils.logger import get_logger

import pandas as pd

logger = get_logger(__name__)


def get_engine():
    url = (
        f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password'] or ''}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
    )
    return create_engine(url)


def _upsert(engine, table: str, df: pd.DataFrame, pk_cols: list[str]) -> int:
    """
    Upsert a dataframe into `table` via INSERT ... ON CONFLICT DO UPDATE,
    one row at a time in a single transaction. Row-by-row rather than a
    bulk COPY so a single bad row logs and fails clearly instead of
    silently rejecting the whole batch.
    """
    cols = list(df.columns)
    update_cols = [c for c in cols if c not in pk_cols]

    insert_cols = ", ".join(cols)
    placeholders = ", ".join(f":{c}" for c in cols)
    conflict_cols = ", ".join(pk_cols)
    update_clause = ", ".join(f"{c} = EXCLUDED.{c}" for c in update_cols)

    stmt = text(
        f"INSERT INTO {table} ({insert_cols}) VALUES ({placeholders}) "
        f"ON CONFLICT ({conflict_cols}) DO UPDATE SET {update_clause}"
    )

    # NaN must be swapped for None on the plain Python dicts, not on the
    # dataframe itself: float64 columns have no true null, so
    # df.where(..., None) on a float column silently reverts back to NaN.
    records = df.to_dict(orient="records")
    for record in records:
        for key, value in record.items():
            if isinstance(value, float) and pd.isna(value):
                record[key] = None

    with engine.begin() as conn:
        for record in records:
            conn.execute(stmt, record)

    return len(records)


def load_dim_county(engine) -> int:
    df = pd.DataFrame(
        [{"fips": "06" + code, "county_name": name, "state_fips": "06"} for name, code in CENTRAL_VALLEY_COUNTIES.items()]
    )
    n = _upsert(engine, "dim_county", df, pk_cols=["fips"])
    logger.info("Loaded %d rows into dim_county", n)
    return n


def load_dim_cpi(engine) -> int:
    base_cpi = CPI_U_ANNUAL[CPI_BASE_YEAR]
    df = pd.DataFrame(
        [
            {"year": year, "cpi_u": cpi, "deflator_to_base": round(base_cpi / cpi, 5)}
            for year, cpi in sorted(CPI_U_ANNUAL.items())
        ]
    )
    n = _upsert(engine, "dim_cpi", df, pk_cols=["year"])
    logger.info("Loaded %d rows into dim_cpi", n)
    return n


def load_fact_acs(engine) -> int:
    path = latest_file(DATA_PROCESSED, "fact_acs_")
    df = pd.read_csv(path, dtype={"fips": str})
    df = df[[
        "fips", "acs_year", "total_population", "median_household_income", "per_capita_income",
        "median_household_income_real", "per_capita_income_real",
        "poverty_universe", "poverty_below_count", "poverty_rate",
        "edu_universe_25plus", "edu_hs_diploma", "edu_associates", "edu_bachelors",
        "edu_masters", "edu_professional", "edu_doctorate",
        "bachelors_or_higher_pct", "advanced_degree_pct",
        "median_home_value", "median_gross_rent", "housing_units_occupied",
        "housing_owner_occupied", "housing_renter_occupied", "homeownership_rate",
        "civilian_labor_force", "unemployed_count", "unemployment_rate",
    ]]
    n = _upsert(engine, "fact_acs", df, pk_cols=["fips", "acs_year"])
    logger.info("Loaded %d rows into fact_acs from %s", n, path)
    return n


def load_fact_nass(engine) -> int:
    path = latest_file(DATA_PROCESSED, "fact_nass_")
    df = pd.read_csv(path, dtype={"fips": str})
    df = df[[
        "fips", "nass_year", "farm_land_building_value", "total_farm_land_acres",
        "total_ag_sales", "farm_operations_count", "avg_sales_per_farm", "avg_farm_size_acres",
    ]]
    n = _upsert(engine, "fact_nass", df, pk_cols=["fips", "nass_year"])
    logger.info("Loaded %d rows into fact_nass from %s", n, path)
    return n


def load_fact_cdc_places(engine) -> int:
    path = latest_file(DATA_PROCESSED, "fact_cdc_places_")
    df = pd.read_csv(path, dtype={"fips": str})
    df = df.drop(columns=["county_name"])
    n = _upsert(engine, "fact_cdc_places", df, pk_cols=["fips", "release_year"])
    logger.info("Loaded %d rows into fact_cdc_places from %s", n, path)
    return n


def load_fact_chhs_deaths(engine) -> int:
    path = latest_file(DATA_PROCESSED, "fact_chhs_deaths_")
    df = pd.read_csv(path, dtype={"fips": str})
    df = df.drop(columns=["county_name"])
    n = _upsert(engine, "fact_chhs_deaths", df, pk_cols=["fips", "death_year"])
    logger.info("Loaded %d rows into fact_chhs_deaths from %s", n, path)
    return n


def load_all() -> dict[str, int]:
    engine = get_engine()
    counts = {
        "dim_county": load_dim_county(engine),
        "dim_cpi": load_dim_cpi(engine),
        "fact_acs": load_fact_acs(engine),
        "fact_nass": load_fact_nass(engine),
        "fact_cdc_places": load_fact_cdc_places(engine),
        "fact_chhs_deaths": load_fact_chhs_deaths(engine),
    }
    logger.info("Load complete: %s", counts)
    return counts


if __name__ == "__main__":
    counts = load_all()
    print("\nRows loaded:")
    for table, n in counts.items():
        print(f"  {table}: {n}")
