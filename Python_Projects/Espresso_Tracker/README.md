# Espresso Shot Tracker

Personal tool to log and analyze espresso shots. Built with PostgreSQL, Python, and Streamlit.

## Setup (first time only)

```bash
pip install -r requirements.txt
```

Create a `.env` file in this folder:
```
DB_HOST=localhost
DB_NAME=espresso
DB_USER=jorgereyeso
DB_PASSWORD=
DB_PORT=5432
```

Run the schema in pgAdmin or psql:
```bash
psql -d espresso -f schema.sql
```

## Daily Use

**Register a new bag of beans (once per bag):**
```bash
python add_bean.py
```

**Log a shot (run right after pulling):**
```bash
python log_shot.py
```

**Open the dashboard:**
```bash
streamlit run dashboard.py
```

## What Gets Tracked

| Field | Description |
|---|---|
| Bean | Which bag you're pulling from |
| Dose | Grams in |
| Yield | Grams out |
| Ratio | Auto-calculated (yield / dose) |
| Time | Shot time in seconds |
| Grind | Your grinder setting |
| Rating | 1–5 taste score |
| Notes | Any observations |
