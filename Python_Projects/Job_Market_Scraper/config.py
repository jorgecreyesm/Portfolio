import os
from dotenv import load_dotenv

load_dotenv()

DB = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     int(os.getenv("DB_PORT", 5432)),
    "dbname":   os.getenv("DB_NAME", "job_market"),
    "user":     os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}

SEARCH_QUERIES = [
    "data analyst entry level remote",
    "business analyst entry level remote",
    "junior data analyst remote",
    "reporting analyst entry level remote",
    "financial analyst entry level remote",
    "commercial analyst entry level remote",
    "insights analyst entry level remote",
    "analytics analyst entry level remote",
    "junior analyst remote Python SQL",
    "data analyst remote 0-2 years",
    "data analyst remote 1-3 years",
    "data analyst remote master's degree",
]

SEARCH_LOCATION = ""          # blank = nationwide
PAGES_PER_QUERY = 5           # 15 results per page on Indeed
REQUEST_DELAY   = (2.5, 5.0)  # random sleep range in seconds between requests

# ── Filter configuration ──────────────────────────────────────────────
EXCLUDE_TITLE_KEYWORDS = [
    "senior", "sr.", "lead", "manager", "director",
    "principal", "head of", "vp", "vice president",
    "associate director", "iv", "iii",
    # "staff" intentionally omitted — would block "Staff Services Analyst" (CalCareers target)
]

EXCLUDE_BODY_KEYWORDS = [
    "5+ years", "6+ years", "7+ years", "8+ years", "10+ years",
    "five years", "six years", "seven years",
    "h1b", "opt", "cpt", "f1 visa", "visa sponsorship",
    "staffing agency", "we place candidates",
    "we are not the eor", "connecting candidates with employers",
    "on-site only", "must be on-site",
    "relocate to", "relocation required",
    "credit check required",
]

POSITIVE_SIGNALS = [
    "python", "sql", "r programming", "tableau", "power bi",
    "pandas", "numpy", "etl", "machine learning",
    "data visualization", "statistical analysis",
    "entry level", "0-2 years", "1-3 years",
    "bachelor", "master", "recent graduate",
]

FAKE_COMPANY_PATTERNS = [
    r"tech\s*solutions",
    r"global\s*it",
    r"ai\s*cloud",
    r"staffsolutions",
    r"data\s*consulting\s*inc",
    r"nexus\s*security",
    r"dhatronictech",
    r"aicloudprotection",
    r"amgtech",
]

SALARY_CONFIG = {
    "min_annual":    45_000,   # hard floor — reject below this
    "max_annual":   110_000,   # upper bound for entry-level targeting
    "target_min":    55_000,   # realistic target floor (used in scoring)
    "target_max":    95_000,   # realistic target ceiling
}
