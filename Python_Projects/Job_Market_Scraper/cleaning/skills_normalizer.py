import re

SKILL_MAP: dict[str, tuple[str, str]] = {
    # raw keyword -> (normalized, category)
    # SQL / Databases
    "sql":            ("SQL",        "SQL"),
    "mysql":          ("MySQL",      "SQL"),
    "postgresql":     ("PostgreSQL", "SQL"),
    "postgres":       ("PostgreSQL", "SQL"),
    "sql server":     ("SQL Server", "SQL"),
    "t-sql":          ("T-SQL",      "SQL"),
    "tsql":           ("T-SQL",      "SQL"),
    "bigquery":       ("BigQuery",   "SQL"),
    "redshift":       ("Redshift",   "SQL"),
    "snowflake":      ("Snowflake",  "SQL"),
    "hive":           ("Hive",       "SQL"),
    "presto":         ("Presto",     "SQL"),
    "oracle":         ("Oracle SQL", "SQL"),
    # Python
    "python":         ("Python",     "Python"),
    "pandas":         ("Pandas",     "Python"),
    "numpy":          ("NumPy",      "Python"),
    "matplotlib":     ("Matplotlib", "Python"),
    "seaborn":        ("Seaborn",    "Python"),
    "scikit-learn":   ("Scikit-learn","Python"),
    "sklearn":        ("Scikit-learn","Python"),
    "jupyter":        ("Jupyter",    "Python"),
    "pyspark":        ("PySpark",    "Python"),
    # Excel / Spreadsheets
    "excel":          ("Excel",      "Excel"),
    "google sheets":  ("Google Sheets","Excel"),
    "spreadsheet":    ("Excel",      "Excel"),
    "pivot table":    ("Excel",      "Excel"),
    "vlookup":        ("Excel",      "Excel"),
    # Visualization
    "tableau":        ("Tableau",    "Visualization"),
    "power bi":       ("Power BI",   "Visualization"),
    "powerbi":        ("Power BI",   "Visualization"),
    "looker":         ("Looker",     "Visualization"),
    "qlik":           ("Qlik",       "Visualization"),
    "qlikview":       ("Qlik",       "Visualization"),
    "qliksense":      ("Qlik",       "Visualization"),
    "superset":       ("Superset",   "Visualization"),
    "metabase":       ("Metabase",   "Visualization"),
    "domo":           ("Domo",       "Visualization"),
    # Cloud / Data Platforms
    "aws":            ("AWS",        "Cloud"),
    "azure":          ("Azure",      "Cloud"),
    "gcp":            ("GCP",        "Cloud"),
    "google cloud":   ("GCP",        "Cloud"),
    "databricks":     ("Databricks", "Cloud"),
    "dbt":            ("dbt",        "Cloud"),
    "airflow":        ("Airflow",    "Cloud"),
    # Statistics
    "statistics":     ("Statistics", "Statistics"),
    "statistical analysis": ("Statistics","Statistics"),
    "regression":     ("Regression", "Statistics"),
    "a/b testing":    ("A/B Testing","Statistics"),
    "ab testing":     ("A/B Testing","Statistics"),
    "hypothesis testing": ("Hypothesis Testing","Statistics"),
    # R
    "r programming":  ("R",          "R"),
    "rstudio":        ("R",          "R"),
    "tidyverse":      ("R",          "R"),
    "ggplot":         ("R",          "R"),
    # Communication / Reporting
    "powerpoint":     ("PowerPoint", "Communication"),
    "google slides":  ("Google Slides","Communication"),
    "presentation":   ("Presentation","Communication"),
    # Other
    "spark":          ("Spark",        "Other"),
    "etl":            ("ETL",          "Other"),
    "data modeling":  ("Data Modeling","Other"),
    "data warehouse": ("Data Warehouse","Other"),
    "jira":           ("Jira",         "Other"),
    "confluence":     ("Confluence",   "Other"),
    "git":            ("Git",          "Other"),
    "github":         ("Git",          "Other"),
    "api":            ("API",          "Other"),
    # Python — additional libraries
    "streamlit":      ("Streamlit",    "Python"),
    "plotly":         ("Plotly",       "Python"),
    "machine learning": ("Machine Learning", "Python"),
    "random forest":  ("Random Forest","Python"),
    # R — additional aliases
    "r studio":       ("R",            "R"),
    # Statistics — additional
    "time series":    ("Time Series",  "Statistics"),
    "forecasting":    ("Forecasting",  "Statistics"),
    "eda":            ("EDA",          "Statistics"),
}


def extract_skills(description: str) -> list[dict]:
    """Find known skills in a job description and return normalized records."""
    if not description:
        return []
    text = description.lower()
    found = {}
    for keyword, (normalized, category) in SKILL_MAP.items():
        pattern = r"\b" + re.escape(keyword) + r"\b"
        if re.search(pattern, text):
            if normalized not in found:
                found[normalized] = {
                    "raw":        keyword,
                    "normalized": normalized,
                    "category":   category,
                }
    return list(found.values())
