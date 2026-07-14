"""
Central configuration for the Central Valley Community Health & Economic Dashboard.

All modules import county definitions, API settings, and file paths from here
so there is exactly one place to change them.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env at the project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

# ---------------------------------------------------------------------------
# Geography
# ---------------------------------------------------------------------------
CA_STATE_FIPS = "06"

# County name -> 3-digit county FIPS code (within California)
CENTRAL_VALLEY_COUNTIES = {
    "Fresno": "019",
    "Kings": "031",
    "Madera": "039",
    "Merced": "047",
    "San Joaquin": "077",
    "Stanislaus": "099",
    "Tulare": "107",
}

# Full 5-digit FIPS (state + county), used by CDC PLACES and for joins
COUNTY_FIPS_5 = {
    name: CA_STATE_FIPS + code for name, code in CENTRAL_VALLEY_COUNTIES.items()
}

# ---------------------------------------------------------------------------
# Census ACS 5-Year settings
# ---------------------------------------------------------------------------
CENSUS_API_KEY = os.getenv("CENSUS_API_KEY")
CENSUS_BASE_URL = "https://api.census.gov/data"

# ACS 5-year vintages to pull. Each vintage covers a 5-year window ending in
# that year, e.g. 2023 = 2019-2023 estimates. Pulling several vintages gives
# the dashboard its trend lines.
ACS_YEARS = [2018, 2019, 2020, 2021, 2022, 2023]
ACS_DATASET = "acs/acs5"

# Variable code -> human-readable column name.
# Detailed tables (B-prefix) return counts and medians; rates are derived
# in the transform step so the raw values stay auditable.
ACS_VARIABLES = {
    # Population
    "B01003_001E": "total_population",
    # Income
    "B19013_001E": "median_household_income",
    "B19301_001E": "per_capita_income",
    # Poverty (universe + below-poverty count; rate derived in transform)
    "B17001_001E": "poverty_universe",
    "B17001_002E": "poverty_below_count",
    # Education, population 25+ (rates derived in transform)
    "B15003_001E": "edu_universe_25plus",
    "B15003_017E": "edu_hs_diploma",
    "B15003_021E": "edu_associates",
    "B15003_022E": "edu_bachelors",
    "B15003_023E": "edu_masters",
    "B15003_024E": "edu_professional",
    "B15003_025E": "edu_doctorate",
    # Housing
    "B25077_001E": "median_home_value",
    "B25064_001E": "median_gross_rent",
    "B25003_001E": "housing_units_occupied",
    "B25003_002E": "housing_owner_occupied",
    "B25003_003E": "housing_renter_occupied",
    # Employment (civilian labor force 16+; unemployment rate derived)
    "B23025_003E": "civilian_labor_force",
    "B23025_005E": "unemployed_count",
}

# ---------------------------------------------------------------------------
# Inflation (CPI-U) for real-dollar deflation
# ---------------------------------------------------------------------------
# ACS income figures are nominal dollars. To compare purchasing power across
# vintages -- especially the post-COVID inflation spike -- we deflate income
# to constant dollars using the CPI-U annual average (all items, US city
# average, 1982-84=100). Values are the official BLS annual averages.
# Source: U.S. Bureau of Labor Statistics, CPI-U historical tables.
CPI_U_ANNUAL = {
    2018: 251.107,
    2019: 255.657,
    2020: 258.811,
    2021: 270.970,
    2022: 292.655,
    2023: 304.702,
}
# Base year real income is expressed in. 2023 = "in 2023 dollars".
CPI_BASE_YEAR = 2023

# ---------------------------------------------------------------------------
# USDA NASS Quick Stats settings
# ---------------------------------------------------------------------------
NASS_API_KEY = os.getenv("NASS_API_KEY")
NASS_BASE_URL = "https://quickstats.nass.usda.gov/api/api_GET/"

# County-level totals (sales, land value, acreage, farm counts) only exist
# in the Census of Agriculture, which runs every 5 years -- not annually
# like the ACS survey data. 2022 is the latest available vintage.
NASS_YEARS = [2012, 2017, 2022]
NASS_SOURCE_DESC = "CENSUS"
NASS_SECTOR_DESC = "ECONOMICS"

# short_desc -> human-readable column name.
# These are standard Census of Agriculture county-level totals reported
# under domain_desc=TOTAL (i.e. not broken out by farm size, tenure, etc).
NASS_VARIABLES = {
    "AG LAND, INCL BUILDINGS - ASSET VALUE, MEASURED IN $": "farm_land_building_value",
    "AG LAND - ACRES": "total_farm_land_acres",
    "COMMODITY TOTALS - SALES, MEASURED IN $": "total_ag_sales",
    "FARM OPERATIONS - NUMBER OF OPERATIONS": "farm_operations_count",
}

# Most variables expose an unbroken-out grand total under
# domain_desc=TOTAL (domaincat_desc="NOT SPECIFIED"). A few short_desc
# values have no TOTAL domain at all and instead report the grand total
# under a single, differently-named category -- for "AG LAND - ACRES"
# that's domain "IRRIGATION STATUS", category "(ANY ON OPERATION)", which
# is the only category NASS returns for that short_desc at county level.
# None here means "don't filter by domain_desc", since exactly one row
# per county-year already comes back.
NASS_DOMAIN_OVERRIDES = {
    "AG LAND - ACRES": None,
}
NASS_DEFAULT_DOMAIN = "TOTAL"

# ---------------------------------------------------------------------------
# CDC PLACES settings
# ---------------------------------------------------------------------------
# "PLACES: County Data (GIS Friendly Format), 2025 release" -- verified via
# the dataset's Socrata metadata endpoint. Unlike ACS/NASS this is a single
# snapshot, not a time series: one row per county, modeled from BRFSS
# 2022/2023 survey data. There is no year field to loop over.
CDC_PLACES_BASE_URL = "https://data.cdc.gov/resource/i46a-9kgh.json"
CDC_PLACES_RELEASE_YEAR = 2025
CDC_PLACES_SURVEY_YEARS = "2022-2023"  # underlying BRFSS vintage

# Socrata field name -> human-readable column name. Curated to the
# chronic disease, health behavior, and preventive care measures the
# README calls out, not the full ~40-measure set.
CDC_PLACES_MEASURES = {
    # Chronic disease prevalence
    "obesity_crudeprev": "obesity_pct",
    "diabetes_crudeprev": "diabetes_pct",
    "bphigh_crudeprev": "high_blood_pressure_pct",
    "highchol_crudeprev": "high_cholesterol_pct",
    "chd_crudeprev": "coronary_heart_disease_pct",
    "stroke_crudeprev": "stroke_pct",
    "copd_crudeprev": "copd_pct",
    "casthma_crudeprev": "asthma_pct",
    "cancer_crudeprev": "cancer_pct",
    "depression_crudeprev": "depression_pct",
    "ghlth_crudeprev": "poor_general_health_pct",
    # Health behaviors
    "csmoking_crudeprev": "smoking_pct",
    "binge_crudeprev": "binge_drinking_pct",
    "lpa_crudeprev": "no_leisure_activity_pct",
    "sleep_crudeprev": "short_sleep_pct",
    # Preventive care / access
    "access2_crudeprev": "no_health_insurance_pct",
    "checkup_crudeprev": "routine_checkup_pct",
    "cholscreen_crudeprev": "cholesterol_screening_pct",
    "dental_crudeprev": "dental_visit_pct",
}

CHHS_PORTAL_BASE_URL = "https://data.chhs.ca.gov/api/3/action"

# "Death Profiles by County" dataset, resource "2014-2024 Final Deaths by
# Year by County" -- verified via package_show against the live CKAN API.
# Residence-based (deaths among county residents, matching the ACS
# population denominators) and restricted to the Total Population strata
# so age/sex/race breakdowns don't multiply row counts.
CHHS_DEATH_RESOURCE_ID = "579cc04a-52d6-4c4c-b2df-ad901c9049b7"
CHHS_YEARS = [2018, 2019, 2020, 2021, 2022, 2023]
CHHS_GEOGRAPHY_TYPE = "Residence"
CHHS_STRATA = "Total Population"

# Cause code -> human-readable column name. Covers all 15 leading causes
# published in this resource, "ALL" is the all-cause total.
CHHS_CAUSE_CODES = {
    "ALL": "deaths_all_causes",
    "HTD": "deaths_heart_disease",
    "CAN": "deaths_cancer",
    "STK": "deaths_stroke",
    "CLD": "deaths_chronic_lower_respiratory",
    "DIA": "deaths_diabetes",
    "ALZ": "deaths_alzheimers",
    "INJ": "deaths_accidents",
    "NEP": "deaths_nephritis",
    "PNF": "deaths_influenza_pneumonia",
    "HYP": "deaths_hypertension",
    "PAR": "deaths_parkinsons",
    "LIV": "deaths_chronic_liver_disease",
    "SUI": "deaths_suicide",
    "HOM": "deaths_homicide",
}

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "cv_dashboard"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
}

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"
LOG_DIR = PROJECT_ROOT / "logs"

# ---------------------------------------------------------------------------
# HTTP behavior
# ---------------------------------------------------------------------------
REQUEST_TIMEOUT = 30        # seconds per request
MAX_RETRIES = 4             # attempts before giving up
BACKOFF_BASE = 2            # exponential backoff: 2s, 4s, 8s, ...
