# Espresso Tracker (Web App)

A mobile-first web app for logging and reviewing espresso shots. React front end,
FastAPI back end, PostgreSQL storage — deployed as a single service and installable
to your phone's home screen as a PWA.

This is the web/PWA version. A CLI + Streamlit version lives in
[`../Espresso_Tracker`](../Espresso_Tracker).

## Architecture

```
index.html + *.jsx  ──serves──┐
                              FastAPI (api.py)  ──►  PostgreSQL (beans, shots)
/api/shots  (GET, POST)  ─────┘
```

- **One service.** `api.py` serves both the JSON API (`/api/shots`) and the static
  front end (`/`) via `StaticFiles`. No separate front-end host.
- **Relative fetches.** The front end calls `/api/shots`, so it works at any origin.
- **`DATABASE_URL`-first.** Uses `DATABASE_URL` if set (hosted Postgres), otherwise
  the individual `DB_*` vars (local Postgres).
- **Self-initializing.** On startup the API applies `schema.sql` with
  `CREATE TABLE IF NOT EXISTS`, so a fresh database needs no manual migration step.

The front end loads React and transpiles JSX in the browser via Babel (CDN). That's
fine for personal use; a Vite build is the upgrade path if this ever heads to an app store.

## Local development

Use a virtual environment and call it explicitly (`.venv/bin/python -m ...`).
This sidesteps PATH/`activate`/shell-hash issues — especially under conda's
`(base)` env, where a bare `uvicorn` can resolve to the wrong interpreter and
fail with `ModuleNotFoundError: No module named 'psycopg2'`.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env                      # then edit for your local Postgres
.venv/bin/python -m uvicorn api:app --reload --port 8000
```

To point at hosted Postgres instead of the `.env` values, export a URL first:

```bash
export DATABASE_URL='postgresql://user:pass@host/db?sslmode=require'
.venv/bin/python -m uvicorn api:app --port 8000
```

Open <http://localhost:8000>. Tables are created automatically on first run.

> Prefer `.venv/bin/python -m uvicorn` over a bare `uvicorn`, even after
> `source .venv/bin/activate` — the explicit form always runs the venv's
> interpreter where the dependencies are installed.

## Deploy to Fly.io + Neon

Prerequisites: a [Fly.io](https://fly.io) account, `flyctl` installed
(`brew install flyctl`), and a [Neon](https://neon.tech) Postgres database (free tier).

1. **Get the Neon connection string** — from the Neon dashboard, copy the pooled
   `postgresql://...?sslmode=require` URL.

2. **Pick a unique app name.** Edit `app = "espresso-tracker"` in `fly.toml`
   (names are global), or run `fly launch --no-deploy` to have Fly generate one.

3. **Create the app and set the secret:**
   ```bash
   fly apps create <your-app-name>          # skip if fly launch already made it
   fly secrets set DATABASE_URL="postgresql://user:pass@host/db?sslmode=require"
   ```

4. **Deploy:**
   ```bash
   fly deploy
   ```
   On first boot the API applies `schema.sql` to the Neon database automatically.

5. **Open it:** `fly open` (or visit `https://<your-app-name>.fly.dev`).

`fly.toml` keeps one machine always running (`min_machines_running = 1`,
`auto_stop_machines = false`) so there's no cold start when you open it on your phone.

## Install on your phone

- **iPhone (Safari):** open the site → Share → **Add to Home Screen**.
- **Android (Chrome):** open the site → menu → **Install app** / **Add to Home Screen**.

It launches full-screen with its own icon (see `manifest.json`, `sw.js`).

## Notes

- Single-user by design — no auth, all shots in one table. Fine for a personal tracker.
  Shipping to other users would mean adding accounts + a `user_id` column.
- `log_shot.py` / `log_shot_v2.py` are older standalone CLI loggers, kept for reference
  and excluded from the deploy image (`.dockerignore`).
