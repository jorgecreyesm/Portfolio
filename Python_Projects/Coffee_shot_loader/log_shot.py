"""
Espresso Shot Tracker — log entry form.

Drop this into your Streamlit app (e.g. `streamlit run log_shot.py`) or
import `render_log_shot_form()` into your existing multipage app.

Assumes a Postgres table roughly like:

    CREATE TABLE shots (
        id              SERIAL PRIMARY KEY,
        shot_time       TIMESTAMPTZ NOT NULL,
        bean_name       TEXT        NOT NULL,
        roast_level     TEXT,
        grind_size      NUMERIC(4,1),
        grind_descriptor TEXT,
        dose_g          NUMERIC(5,2) NOT NULL,
        yield_g         NUMERIC(5,2) NOT NULL,
        extraction_s    NUMERIC(5,1) NOT NULL,
        brew_ratio      NUMERIC(5,2) NOT NULL,
        temperature     NUMERIC(5,1),
        temp_unit       TEXT,
        pressure_bar    NUMERIC(4,1),
        tasting_notes   TEXT,
        rating          SMALLINT,
        created_at      TIMESTAMPTZ DEFAULT NOW()
    );

Adjust the INSERT in `insert_shot()` if your column names differ.
"""

from __future__ import annotations

import os
from datetime import datetime, date, time
from typing import Optional

import streamlit as st

# psycopg (v3). If you're on psycopg2, swap the import + connection style.
try:
    import psycopg
    from psycopg.rows import dict_row
    _HAS_PSYCOPG = True
except ImportError:
    _HAS_PSYCOPG = False


# ---------------------------------------------------------------------------
# Theme — warm, minimal. Tweak these to match your existing app.
# ---------------------------------------------------------------------------

THEME_CSS = """
<style>
  :root {
    --bg:        #f7f3ee;
    --surface:   #ffffff;
    --ink:       #2a201a;
    --muted:     #7a6a5e;
    --line:      #e6dccf;
    --accent:    #6f4a2b;   /* espresso brown */
    --accent-hi: #8a5e38;
  }

  .stApp { background: var(--bg); }

  h1, h2, h3, h4 { color: var(--ink); font-weight: 600; letter-spacing: -0.01em; }

  .shot-header {
    border-bottom: 1px solid var(--line);
    padding-bottom: 0.75rem;
    margin-bottom: 1.25rem;
  }
  .shot-header .eyebrow {
    font-size: 0.75rem; letter-spacing: 0.14em; text-transform: uppercase;
    color: var(--muted); margin-bottom: 0.25rem;
  }
  .shot-header h1 { margin: 0; font-size: 1.75rem; }

  .ratio-pill {
    display: inline-flex; align-items: baseline; gap: 0.4rem;
    padding: 0.35rem 0.7rem; border-radius: 999px;
    background: var(--ink); color: #f7f3ee;
    font-variant-numeric: tabular-nums;
    font-size: 0.85rem;
  }
  .ratio-pill b { font-size: 1rem; }

  .stButton > button[kind="primary"] {
    background: var(--accent); color: #fff; border: none;
    border-radius: 8px; padding: 0.55rem 1.1rem; font-weight: 500;
  }
  .stButton > button[kind="primary"]:hover { background: var(--accent-hi); }

  .stTextInput input, .stNumberInput input, .stTextArea textarea,
  .stDateInput input, .stTimeInput input, .stSelectbox div[data-baseweb="select"] > div {
    background: var(--surface) !important;
    border-radius: 6px !important;
  }

  /* Slider accent */
  .stSlider [data-baseweb="slider"] div[role="slider"] { background: var(--accent) !important; }

  /* Quiet success banner */
  .shot-success {
    border: 1px solid #cfe3d4; background: #eef6f0; color: #234a2e;
    padding: 0.85rem 1rem; border-radius: 8px; margin-top: 1rem;
    font-size: 0.95rem;
  }
  .shot-success b { color: #1a3a22; }
</style>
"""


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

def get_conn():
    """Open a Postgres connection. Reads DATABASE_URL from env or st.secrets."""
    if not _HAS_PSYCOPG:
        raise RuntimeError("psycopg is not installed. `pip install psycopg[binary]`")
    url = os.getenv("DATABASE_URL") or st.secrets.get("DATABASE_URL", None)
    if not url:
        raise RuntimeError("DATABASE_URL not set (env or st.secrets).")
    return psycopg.connect(url, row_factory=dict_row)


def insert_shot(payload: dict) -> int:
    """Insert one row into `shots`. Returns the new id."""
    sql = """
        INSERT INTO shots (
            shot_time, bean_name, roast_level,
            grind_size, grind_descriptor,
            dose_g, yield_g, extraction_s, brew_ratio,
            temperature, temp_unit, pressure_bar,
            tasting_notes, rating
        ) VALUES (
            %(shot_time)s, %(bean_name)s, %(roast_level)s,
            %(grind_size)s, %(grind_descriptor)s,
            %(dose_g)s, %(yield_g)s, %(extraction_s)s, %(brew_ratio)s,
            %(temperature)s, %(temp_unit)s, %(pressure_bar)s,
            %(tasting_notes)s, %(rating)s
        )
        RETURNING id;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, payload)
        new_id = cur.fetchone()["id"]
        conn.commit()
    return new_id


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

ROAST_LEVELS = ["Light", "Medium-light", "Medium", "Medium-dark", "Dark"]
GRIND_DESCRIPTORS = [
    "Extra fine", "Fine", "Medium-fine", "Medium", "Medium-coarse", "Coarse",
]


def _calc_ratio(dose: float, yield_: float) -> Optional[float]:
    if dose and dose > 0 and yield_ and yield_ > 0:
        return round(yield_ / dose, 2)
    return None


def render_log_shot_form() -> None:
    st.markdown(THEME_CSS, unsafe_allow_html=True)

    st.markdown(
        """
        <div class="shot-header">
          <div class="eyebrow">Espresso Shot Tracker</div>
          <h1>Log a shot</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- live brew-ratio readout (outside the form so it updates as you type) ---
    live_dose = st.session_state.get("dose_g", 18.0)
    live_yield = st.session_state.get("yield_g", 36.0)
    live_ratio = _calc_ratio(live_dose, live_yield)
    ratio_html = (
        f'<div class="ratio-pill">Brew ratio &nbsp;<b>1 : {live_ratio}</b></div>'
        if live_ratio is not None
        else '<div class="ratio-pill" style="opacity:.5">Brew ratio &nbsp;<b>—</b></div>'
    )
    st.markdown(ratio_html, unsafe_allow_html=True)
    st.write("")

    with st.form("log_shot_form", clear_on_submit=False):
        # Row 1 — date + time
        c1, c2 = st.columns(2)
        with c1:
            d = st.date_input("Date", value=date.today())
        with c2:
            t = st.time_input("Time", value=datetime.now().time().replace(microsecond=0))

        # Row 2 — bean + roast
        c1, c2 = st.columns([2, 1])
        with c1:
            bean_name = st.text_input("Coffee bean", placeholder="e.g. Ethiopia Yirgacheffe")
        with c2:
            roast = st.selectbox("Roast", ROAST_LEVELS, index=2)

        # Row 3 — grind (numeric + descriptor)
        c1, c2 = st.columns(2)
        with c1:
            grind_size = st.number_input(
                "Grind size (numeric)",
                min_value=0.0, max_value=50.0, value=3.5, step=0.1,
                help="Whatever scale your grinder uses.",
            )
        with c2:
            grind_desc = st.selectbox("Grind feel", GRIND_DESCRIPTORS, index=2)

        # Row 4 — dose / yield / time
        c1, c2, c3 = st.columns(3)
        with c1:
            dose = st.number_input(
                "Dose (g)", min_value=0.0, max_value=50.0,
                value=18.0, step=0.1, key="dose_g",
            )
        with c2:
            yield_ = st.number_input(
                "Yield (g)", min_value=0.0, max_value=120.0,
                value=36.0, step=0.1, key="yield_g",
            )
        with c3:
            extraction_s = st.number_input(
                "Extraction time (s)", min_value=0.0, max_value=120.0,
                value=27.0, step=0.5,
            )

        # Row 5 — temp + unit + pressure
        c1, c2, c3 = st.columns([2, 1, 2])
        with c1:
            temp = st.number_input(
                "Temperature", min_value=0.0, max_value=250.0, value=200.0, step=0.5,
            )
        with c2:
            temp_unit = st.radio("Unit", ["°F", "°C"], horizontal=True, index=0)
        with c3:
            pressure = st.number_input(
                "Pressure (bars)", min_value=0.0, max_value=15.0, value=9.0, step=0.1,
            )

        # Row 6 — notes
        notes = st.text_area(
            "Tasting notes",
            placeholder="Body, acidity, sweetness, finish…",
            height=110,
        )

        # Row 7 — rating
        rating = st.slider("Overall rating", min_value=1, max_value=10, value=7)

        st.write("")
        submitted = st.form_submit_button("Log shot", type="primary")

    if not submitted:
        return

    # ---------- validation ----------
    errors = []
    if not bean_name.strip():
        errors.append("Coffee bean name is required.")
    if dose <= 0:
        errors.append("Dose must be greater than 0.")
    if yield_ <= 0:
        errors.append("Yield must be greater than 0.")
    if extraction_s <= 0:
        errors.append("Extraction time must be greater than 0.")
    if errors:
        for e in errors:
            st.error(e)
        return

    ratio = _calc_ratio(dose, yield_)
    shot_time = datetime.combine(d, t)

    payload = {
        "shot_time":        shot_time,
        "bean_name":        bean_name.strip(),
        "roast_level":      roast,
        "grind_size":       grind_size,
        "grind_descriptor": grind_desc,
        "dose_g":           dose,
        "yield_g":          yield_,
        "extraction_s":     extraction_s,
        "brew_ratio":       ratio,
        "temperature":      temp,
        "temp_unit":        temp_unit.replace("°", ""),  # store as "F" / "C"
        "pressure_bar":     pressure,
        "tasting_notes":    notes.strip() or None,
        "rating":           int(rating),
    }

    # ---------- insert ----------
    try:
        new_id = insert_shot(payload)
    except Exception as exc:
        st.error(f"Could not save shot: {exc}")
        return

    st.markdown(
        f"""
        <div class="shot-success">
          ✓ Shot <b>#{new_id}</b> logged ·
          {dose:g} g in &rarr; {yield_:g} g out in {extraction_s:g} s ·
          brew ratio <b>1 : {ratio}</b> · rated <b>{rating}/10</b>.
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    st.set_page_config(
        page_title="Log shot · Espresso Tracker",
        page_icon="☕",
        layout="centered",
    )
    render_log_shot_form()
