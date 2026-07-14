-- Central Valley Community Health & Economic Dashboard
-- Schema: one dimension table for the seven counties, plus one fact table
-- per data source. Sources are kept separate rather than merged into a
-- single wide table because they have different natural grains (ACS and
-- CHHS are annual, NASS is Census-of-Agriculture years, CDC PLACES is a
-- single current snapshot) -- forcing them into one table would mean
-- mostly-NULL rows for whichever sources don't share a given year.
--
-- Derived rate/rate-like columns (poverty_rate, unemployment_rate,
-- deaths_*_per_100k, etc.) are computed in the transform step, never in
-- SQL, so the pipeline's quality-flag log is the single source of truth
-- for how each number was derived.

CREATE TABLE IF NOT EXISTS dim_county (
    fips        CHAR(5) PRIMARY KEY,
    county_name TEXT NOT NULL,
    state_fips  CHAR(2) NOT NULL DEFAULT '06'
);

-- CPI-U annual average (BLS, all items, US city average, 1982-84=100) with
-- the deflator used to convert nominal dollars to constant base-year
-- dollars. Reference dimension, keyed by year; deflator = CPI(base) / CPI(year).
CREATE TABLE IF NOT EXISTS dim_cpi (
    year            SMALLINT PRIMARY KEY,
    cpi_u           NUMERIC(8,3) NOT NULL,
    deflator_to_base NUMERIC(8,5) NOT NULL
);

-- American Community Survey (5-year estimates), one row per county-vintage.
CREATE TABLE IF NOT EXISTS fact_acs (
    fips                        CHAR(5) NOT NULL REFERENCES dim_county(fips),
    acs_year                    SMALLINT NOT NULL,

    total_population            INTEGER,
    median_household_income     INTEGER,
    per_capita_income           INTEGER,
    -- Nominal income deflated to constant CPI_BASE_YEAR dollars, so
    -- purchasing power is comparable across the post-COVID inflation spike.
    median_household_income_real INTEGER,
    per_capita_income_real      INTEGER,

    poverty_universe            INTEGER,
    poverty_below_count         INTEGER,
    poverty_rate                NUMERIC(5,2),

    edu_universe_25plus         INTEGER,
    edu_hs_diploma              INTEGER,
    edu_associates              INTEGER,
    edu_bachelors               INTEGER,
    edu_masters                 INTEGER,
    edu_professional            INTEGER,
    edu_doctorate                INTEGER,
    bachelors_or_higher_pct     NUMERIC(5,2),
    advanced_degree_pct         NUMERIC(5,2),

    median_home_value           INTEGER,
    median_gross_rent           INTEGER,
    housing_units_occupied      INTEGER,
    housing_owner_occupied      INTEGER,
    housing_renter_occupied     INTEGER,
    homeownership_rate          NUMERIC(5,2),

    civilian_labor_force        INTEGER,
    unemployed_count            INTEGER,
    unemployment_rate           NUMERIC(5,2),

    PRIMARY KEY (fips, acs_year)
);

-- USDA NASS Census of Agriculture, one row per county-census year.
CREATE TABLE IF NOT EXISTS fact_nass (
    fips                        CHAR(5) NOT NULL REFERENCES dim_county(fips),
    nass_year                   SMALLINT NOT NULL,

    farm_land_building_value    NUMERIC,
    total_farm_land_acres       NUMERIC,
    total_ag_sales              NUMERIC,
    farm_operations_count       NUMERIC,
    avg_sales_per_farm          NUMERIC,
    avg_farm_size_acres         NUMERIC,

    PRIMARY KEY (fips, nass_year)
);

-- CDC PLACES, single-snapshot modeled estimates -- one row per
-- county-release (release_year distinguishes vintages if the pipeline is
-- ever re-run against a newer PLACES release).
CREATE TABLE IF NOT EXISTS fact_cdc_places (
    fips                        CHAR(5) NOT NULL REFERENCES dim_county(fips),
    release_year                SMALLINT NOT NULL,

    total_population             INTEGER,
    total_population_18plus      INTEGER,

    obesity_pct                  NUMERIC(5,2),
    diabetes_pct                 NUMERIC(5,2),
    high_blood_pressure_pct      NUMERIC(5,2),
    high_cholesterol_pct         NUMERIC(5,2),
    coronary_heart_disease_pct   NUMERIC(5,2),
    stroke_pct                   NUMERIC(5,2),
    copd_pct                     NUMERIC(5,2),
    asthma_pct                   NUMERIC(5,2),
    cancer_pct                   NUMERIC(5,2),
    depression_pct               NUMERIC(5,2),
    poor_general_health_pct      NUMERIC(5,2),

    smoking_pct                  NUMERIC(5,2),
    binge_drinking_pct           NUMERIC(5,2),
    no_leisure_activity_pct      NUMERIC(5,2),
    short_sleep_pct              NUMERIC(5,2),

    no_health_insurance_pct      NUMERIC(5,2),
    routine_checkup_pct          NUMERIC(5,2),
    cholesterol_screening_pct    NUMERIC(5,2),
    dental_visit_pct             NUMERIC(5,2),

    PRIMARY KEY (fips, release_year)
);

-- CHHS Death Profiles by County, one row per county-year with one
-- count/rate column pair per leading cause of death.
CREATE TABLE IF NOT EXISTS fact_chhs_deaths (
    fips                                    CHAR(5) NOT NULL REFERENCES dim_county(fips),
    death_year                              SMALLINT NOT NULL,

    deaths_all_causes                       INTEGER,
    deaths_all_causes_per_100k              NUMERIC(8,2),
    deaths_heart_disease                    INTEGER,
    deaths_heart_disease_per_100k           NUMERIC(8,2),
    deaths_cancer                           INTEGER,
    deaths_cancer_per_100k                  NUMERIC(8,2),
    deaths_stroke                           INTEGER,
    deaths_stroke_per_100k                  NUMERIC(8,2),
    deaths_chronic_lower_respiratory        INTEGER,
    deaths_chronic_lower_respiratory_per_100k NUMERIC(8,2),
    deaths_diabetes                         INTEGER,
    deaths_diabetes_per_100k                NUMERIC(8,2),
    deaths_alzheimers                       INTEGER,
    deaths_alzheimers_per_100k              NUMERIC(8,2),
    deaths_accidents                        INTEGER,
    deaths_accidents_per_100k               NUMERIC(8,2),
    deaths_nephritis                        INTEGER,
    deaths_nephritis_per_100k               NUMERIC(8,2),
    deaths_influenza_pneumonia              INTEGER,
    deaths_influenza_pneumonia_per_100k     NUMERIC(8,2),
    deaths_hypertension                     INTEGER,
    deaths_hypertension_per_100k            NUMERIC(8,2),
    deaths_parkinsons                       INTEGER,
    deaths_parkinsons_per_100k              NUMERIC(8,2),
    deaths_chronic_liver_disease            INTEGER,
    deaths_chronic_liver_disease_per_100k   NUMERIC(8,2),
    deaths_suicide                          INTEGER,
    deaths_suicide_per_100k                 NUMERIC(8,2),
    deaths_homicide                         INTEGER,
    deaths_homicide_per_100k                NUMERIC(8,2),

    PRIMARY KEY (fips, death_year)
);

CREATE INDEX IF NOT EXISTS idx_fact_acs_year ON fact_acs (acs_year);
CREATE INDEX IF NOT EXISTS idx_fact_nass_year ON fact_nass (nass_year);
CREATE INDEX IF NOT EXISTS idx_fact_chhs_deaths_year ON fact_chhs_deaths (death_year);
