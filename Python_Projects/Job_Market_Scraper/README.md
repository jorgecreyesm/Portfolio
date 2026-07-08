# Job Market Scraper — Entry-Level DA / BA Postings

A Python pipeline that scrapes entry-level Data Analyst and Business Analyst job postings from Indeed, stores them in PostgreSQL, normalizes skills into categories, flags staffing agencies, and generates a summary analysis report.

---

## Features

- Scrapes job title, company, location, remote/onsite status, salary, and full description
- Deduplicates by URL — safe to re-run without creating duplicate records
- Detects staffing agencies vs direct employers using keyword matching
- Normalizes extracted skills into categories: SQL, Python, Excel, Visualization, Cloud, Statistics, R, Communication
- Summary report: top skills, salary ranges, agency vs direct ratio, top hiring locations

---

## Tech Stack

| Layer | Tool |
|-------|------|
| Scraping | `requests`, `BeautifulSoup4`, `fake-useragent` |
| Database | PostgreSQL + `psycopg2` |
| Cleaning | Custom keyword matching |
| Analysis | `pandas`, `tabulate` |

---

## Project Structure

```
Job_Market_Scraper/
├── main.py                    # CLI entry point
├── config.py                  # Search queries, DB config, rate limits
├── schema.sql                 # PostgreSQL table definitions
├── requirements.txt
├── .env.example
├── scraper/
│   ├── base_scraper.py        # Session, rate limiting, retry logic
│   └── indeed_scraper.py      # Indeed search + card parsing
├── database/
│   ├── connection.py          # DB connection + init
│   └── models.py              # Insert / fetch queries
├── cleaning/
│   ├── skills_normalizer.py   # Skill extraction and categorization
│   └── agency_detector.py     # Staffing agency keyword detection
└── analysis/
    └── summary.py             # Summary report printed to terminal
```

---

## Setup

**1. Clone and install dependencies**
```bash
git clone <repo-url>
cd Job_Market_Scraper
pip install -r requirements.txt
```

**2. Configure environment**
```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials
```

**3. Create the database**
```sql
CREATE DATABASE job_market;
```

**4. Initialize tables**
```bash
python main.py init
```

---

## Usage

Run each stage individually or all at once:

```bash
# Full pipeline
python main.py run-all

# Or step by step
python main.py init       # Create DB tables
python main.py scrape     # Scrape Indeed (respects rate limits)
python main.py clean      # Re-run agency detection + skill extraction
python main.py analyze    # Print summary report to terminal
```

Configure search queries, location, and pages per query in `config.py`:

```python
SEARCH_QUERIES  = ["entry level data analyst", "entry level business analyst", ...]
SEARCH_LOCATION = "California"   # blank = nationwide
PAGES_PER_QUERY = 5              # 15 results per page
```

---

## Automation

Runs automatically Mon–Fri at 7:00 AM via a macOS `launchd` LaunchAgent
(`com.jorgereyeso.jobscraper`), invoking:

```bash
/opt/anaconda3/bin/python3 main.py run-all --save
```

Key points for running this unattended:

- `WorkingDirectory` is set to the project root — `schema.sql`, `reports/`,
  `profile.json`, and `.env` are all loaded via relative paths, so the
  scheduler must `cd` here first
- The full path to the conda interpreter is used explicitly, since a bare
  `python3` on a scheduler's minimal `PATH` won't resolve to the
  environment with `jobspy`/`psycopg2` installed
- `--save` is required for `analyze`/`match` to write CSVs to `reports/` —
  omitting it runs the full pipeline with no file output
- stdout/stderr are logged to `~/Library/Logs/jobscraper.log` /
  `jobscraper.error.log`
- Requires PostgreSQL to be running (via Postgres.app) at the scheduled
  time, which in turn requires an active GUI login session

---

## Sample Output

```
============================================================
  JOB MARKET ANALYSIS — Entry-Level DA / BA Postings
============================================================

Total postings scraped :  312
Direct employer        :  198 (63.5%)
Staffing agency        :  114 (36.5%)
Remote / hybrid        :   87 (27.9%)

--- Top 15 Required Skills ---
skill_normalized     count    % of postings
-----------------  -------  ---------------
SQL                    241             77.2
Excel                  198             63.5
Python                 175             56.1
Tableau                142             45.5
Power BI               118             37.8
...
```

---

## Ethics & Rate Limiting

- Requests are delayed 2.5–5 seconds between calls to avoid overloading servers
- User agents are rotated on every request
- Deduplication prevents redundant scraping of the same listing
- This project is for educational and portfolio purposes. Review Indeed's Terms of Service before deploying at scale.

---

## Author

**Jorge Reyes-Ornelas** — M.S. Data Analytics (in progress), Eastern University
[GitHub](https://github.com/jorgecreyesm)
