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
    "entry level data analyst",
    "entry level business analyst",
    "junior data analyst",
    "junior business analyst",
]

SEARCH_LOCATION = ""          # blank = nationwide
PAGES_PER_QUERY = 5           # 15 results per page on Indeed
REQUEST_DELAY   = (2.5, 5.0)  # random sleep range in seconds between requests
