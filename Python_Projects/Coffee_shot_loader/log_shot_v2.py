"""
Espresso Shot Tracker — polished dark-mode logging page.

Run:    streamlit run log_shot_v2.py
Or:     from log_shot_v2 import render_log_shot_page

Requires:
    pip install streamlit psycopg[binary]

Postgres connection comes from DATABASE_URL (env or st.secrets).
Adjust the INSERT in `insert_shot()` if your `shots` columns differ.
"""

from __future__ import annotations

import os
from datetime import datetime, date
from typing import Optional, Tuple

import streamlit as st

try:
    import psycopg
    from psycopg.rows import dict_row
    _HAS_PSYCOPG = True
except ImportError:
    _HAS_PSYCOPG = False


# ────────────────────────────────────────────────────────────────────────────
# Theme
# ────────────────────────────────────────────────────────────────────────────

THEME_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Manrope:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  :root {
    --bg:        #15110d;
    --bg-2:      #1b1612;
    --surface:   #221b14;
    --surface-2: #2a2118;
    --line:      #322619;
    --line-2:    #3d2f20;
    --ink:       #f0e6d6;
    --ink-dim:   #c8b9a4;
    --muted:     #8a7864;
    --amber:     #d4a574;
    --amber-hi:  #e8b87a;
    --amber-dim: #8a6a44;
    --good:      #7bc48a;
    --bad:       #d97766;
  }

  html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background: var(--bg) !important;
    color: var(--ink) !important;
    font-family: 'Manrope', system-ui, sans-serif !important;
  }
  [data-testid="stHeader"] { background: transparent !important; }
  #MainMenu, footer { visibility: hidden; }

  .block-container { padding-top: 2rem !important; max-width: 880px; }

  /* Typography */
  h1, h2, h3, h4 { color: var(--ink); letter-spacing: -0.015em; font-weight: 600; }
  label, .stMarkdown p { color: var(--ink-dim) !important; }
  .stMarkdown small { color: var(--muted); }

  /* Eyebrow header */
  .et-eyebrow {
    font-size: 0.72rem; letter-spacing: 0.22em; text-transform: uppercase;
    color: var(--amber); font-weight: 600; margin-bottom: 0.4rem;
  }
  .et-title {
    font-family: 'Instrument Serif', serif; font-weight: 400;
    font-size: 2.6rem; line-height: 1; color: var(--ink); margin: 0 0 0.3rem 0;
    letter-spacing: -0.02em;
  }
  .et-title em { font-style: italic; color: var(--amber); }
  .et-subtitle { color: var(--muted); font-size: 0.92rem; margin-bottom: 1.8rem; }

  /* Cards */
  .et-card {
    background: linear-gradient(180deg, var(--surface) 0%, var(--bg-2) 100%);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 1.4rem 1.5rem;
    box-shadow: 0 1px 0 rgba(255,255,255,0.02) inset,
                0 10px 30px -12px rgba(0,0,0,0.6);
    margin-bottom: 1.1rem;
  }
  .et-card-head {
    display: flex; align-items: baseline; justify-content: space-between;
    margin-bottom: 1rem;
  }
  .et-card-title {
    font-size: 0.78rem; letter-spacing: 0.18em; text-transform: uppercase;
    color: var(--muted); font-weight: 600;
  }
  .et-card-step {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem; color: var(--amber-dim); letter-spacing: 0.08em;
  }

  /* Brew ratio hero card */
  .ratio-hero {
    background: radial-gradient(120% 140% at 0% 0%, #2c2117 0%, #1c1611 60%, #15110d 100%);
    border: 1px solid var(--line-2);
    border-radius: 18px;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.4rem;
    position: relative;
    overflow: hidden;
  }
  .ratio-hero::before {
    content: ""; position: absolute; inset: 0;
    background: radial-gradient(60% 100% at 100% 0%, rgba(212,165,116,0.10) 0%, transparent 60%);
    pointer-events: none;
  }
  .ratio-row {
    display: flex; align-items: flex-end; justify-content: space-between; gap: 1rem;
    position: relative;
  }
  .ratio-label {
    font-size: 0.72rem; letter-spacing: 0.24em; text-transform: uppercase;
    color: var(--muted); font-weight: 600;
  }
  .ratio-number {
    font-family: 'Instrument Serif', serif; font-style: italic;
    font-size: 4.2rem; line-height: 0.95; letter-spacing: -0.02em;
    margin-top: 0.4rem;
    transition: color 0.25s ease;
  }
  .ratio-number .colon { font-style: normal; padding: 0 0.15em; opacity: 0.55; }
  .ratio-meta {
    text-align: right; font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem; color: var(--ink-dim);
  }
  .ratio-meta .row { display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 0.2rem; }
  .ratio-meta .row span:first-child { color: var(--muted); }

  .ratio-status {
    margin-top: 1rem; display: inline-flex; align-items: center; gap: 0.5rem;
    font-size: 0.82rem; letter-spacing: 0.02em;
    padding: 0.32rem 0.7rem; border-radius: 999px;
    background: rgba(255,255,255,0.04); border: 1px solid var(--line-2);
  }
  .ratio-status .dot {
    width: 7px; height: 7px; border-radius: 50%;
    box-shadow: 0 0 10px currentColor;
  }
  .is-good  { color: var(--good); }
  .is-good  .dot { background: var(--good);  }
  .is-amber { color: var(--amber-hi); }
  .is-amber .dot { background: var(--amber-hi); }
  .is-bad   { color: var(--bad); }
  .is-bad   .dot { background: var(--bad); }

  .is-good .ratio-number  { color: var(--good); }
  .is-amber .ratio-number { color: var(--amber-hi); }
  .is-bad .ratio-number   { color: var(--bad); }

  /* Inputs */
  .stTextInput input, .stNumberInput input, .stTextArea textarea,
  .stDateInput input, .stTimeInput input,
  .stSelectbox div[data-baseweb="select"] > div {
    background: var(--bg-2) !important;
    color: var(--ink) !important;
    border: 1px solid var(--line) !important;
    border-radius: 10px !important;
    font-family: 'Manrope', sans-serif !important;
  }
  .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
    border-color: var(--amber) !important;
    box-shadow: 0 0 0 3px rgba(212,165,116,0.12) !important;
  }
  .stNumberInput button {
    background: var(--surface-2) !important; color: var(--amber) !important;
    border-color: var(--line) !important;
  }
  .stTextArea textarea { min-height: 110px; }

  /* Slider */
  .stSlider [data-baseweb="slider"] > div > div { background: var(--line-2) !important; }
  .stSlider [data-baseweb="slider"] > div > div > div { background: var(--amber) !important; }
  .stSlider [role="slider"] {
    background: var(--amber) !important;
    border: 3px solid #2a1f14 !important;
    box-shadow: 0 0 0 1px var(--amber-hi), 0 4px 10px rgba(0,0,0,0.4) !important;
  }

  /* Buttons */
  .stButton > button {
    background: var(--amber) !important;
    color: #1a1108 !important;
    border: none !important; border-radius: 12px !important;
    padding: 0.85rem 1.4rem !important;
    font-weight: 600 !important; font-size: 1rem !important;
    letter-spacing: 0.01em;
    width: 100%;
    box-shadow: 0 8px 20px -8px rgba(212,165,116,0.5),
                0 1px 0 rgba(255,255,255,0.15) inset;
    transition: transform 0.08s ease, box-shadow 0.2s ease, background 0.2s ease;
  }
  .stButton > button:hover {
    background: var(--amber-hi) !important;
    transform: translateY(-1px);
    box-shadow: 0 12px 24px -8px rgba(212,165,116,0.55);
  }
  .stButton > button:active { transform: translateY(0); }

  /* Radio (temp unit) */
  .stRadio label, .stRadio div { color: var(--ink-dim) !important; }
  .stRadio [role="radiogroup"] label > div:first-child {
    border-color: var(--amber-dim) !important;
  }

  /* Star rating */
  .star-row {
    display: flex; gap: 0.18rem; font-size: 1.4rem;
    font-family: 'JetBrains Mono', monospace;
    align-items: center;
  }
  .star-row .star { color: var(--line-2); transition: color 0.15s; }
  .star-row .star.on { color: var(--amber); text-shadow: 0 0 8px rgba(212,165,116,0.4); }
  .star-row .num {
    margin-left: 0.8rem; font-family: 'Instrument Serif', serif; font-style: italic;
    font-size: 1.4rem; color: var(--ink);
  }
  .star-row .num small {
    font-family: 'JetBrains Mono', monospace; font-style: normal;
    color: var(--muted); font-size: 0.7rem; margin-left: 0.2rem;
  }

  /* Success card */
  @keyframes et-rise {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  @keyframes et-draw {
    from { stroke-dashoffset: 60; }
    to   { stroke-dashoffset: 0; }
  }
  .et-success {
    animation: et-rise 0.45s ease-out both;
    background: linear-gradient(180deg, #1d2a1d 0%, #161e16 100%);
    border: 1px solid #2f4731;
    border-radius: 16px; padding: 1.4rem 1.6rem; margin-top: 1.2rem;
    display: flex; gap: 1.1rem; align-items: center;
  }
  .et-success .check {
    width: 44px; height: 44px; border-radius: 50%;
    background: #2a3f2c; display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; border: 1px solid #3d5a40;
  }
  .et-success .check svg path {
    stroke: var(--good); stroke-width: 2.5; fill: none;
    stroke-linecap: round; stroke-linejoin: round;
    stroke-dasharray: 60; animation: et-draw 0.5s ease-out 0.15s both;
  }
  .et-success h3 {
    font-family: 'Instrument Serif', serif; font-style: italic; font-weight: 400;
    margin: 0 0 0.2rem 0; font-size: 1.4rem; color: var(--ink);
  }
  .et-success p {
    margin: 0; color: var(--ink-dim); font-size: 0.9rem;
    font-family: 'JetBrains Mono', monospace;
  }
  .et-success p b { color: var(--good); }

  /* Top bar */
  .et-topbar {
    display: flex; justify-content: space-between; align-items: center;
    padding-bottom: 1.2rem; margin-bottom: 1.5rem;
    border-bottom: 1px solid var(--line);
  }
  .et-brand {
    display: flex; align-items: center; gap: 0.6rem;
    font-weight: 600; color: var(--ink); letter-spacing: 0.01em;
  }
  .et-brand .mark {
    width: 28px; height: 28px; border-radius: 8px;
    background: linear-gradient(135deg, var(--amber), #a87445);
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 4px 10px -4px rgba(212,165,116,0.5);
  }
  .et-brand small {
    color: var(--muted); font-weight: 400; font-size: 0.75rem;
    letter-spacing: 0.06em; margin-left: 0.4rem;
  }
  .et-clock {
    font-family: 'JetBrains Mono', monospace; color: var(--muted);
    font-size: 0.8rem; letter-spacing: 0.06em;
  }
  .et-clock b { color: var(--ink-dim); font-weight: 500; }
</style>
"""


# ────────────────────────────────────────────────────────────────────────────
# DB
# ────────────────────────────────────────────────────────────────────────────

def get_conn():
    if not _HAS_PSYCOPG:
        raise RuntimeError("psycopg not installed — `pip install psycopg[binary]`")
    url = os.getenv("DATABASE_URL") or st.secrets.get("DATABASE_URL", None)
    if not url:
        raise RuntimeError("DATABASE_URL not set (env or st.secrets).")
    return psycopg.connect(url, row_factory=dict_row)


def insert_shot(payload: dict) -> int:
    sql = """
        INSERT INTO shots (
            shot_time, bean_name, roast_level,
            grind_size,
            dose_g, yield_g, extraction_s, brew_ratio,
            temperature, temp_unit, pressure_bar,
            tasting_notes, rating
        ) VALUES (
            %(shot_time)s, %(bean_name)s, %(roast_level)s,
            %(grind_size)s,
            %(dose_g)s, %(yield_g)s, %(extraction_s)s, %(brew_ratio)s,
            %(temperature)s, %(temp_unit)s, %(pressure_bar)s,
            %(tasting_notes)s, %(rating)s
        ) RETURNING id;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, payload)
        new_id = cur.fetchone()["id"]
        conn.commit()
    return new_id


# ────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────

ROAST_LEVELS = ["Light", "Medium-light", "Medium", "Medium-dark", "Dark"]


def calc_ratio(dose: float, yield_: float) -> Optional[float]:
    if dose and dose > 0 and yield_ and yield_ > 0:
        return round(yield_ / dose, 2)
    return None


def ratio_status(ratio: Optional[float]) -> Tuple[str, str, str]:
    """Return (css_class, label, hint)."""
    if ratio is None:
        return ("is-amber", "Awaiting input", "Enter dose & yield to see the ratio")
    if 2.0 <= ratio <= 2.5:
        return ("is-good", "In the pocket", "Balanced extraction range")
    if 1.5 <= ratio < 2.0:
        return ("is-bad", "Under-extracted", "Ristretto territory — try a finer grind or higher yield")
    if 2.5 < ratio <= 3.0:
        return ("is-bad", "Over-extracted", "Lungo territory — try a coarser grind or lower yield")
    if ratio < 1.5:
        return ("is-bad", "Very tight", "Yield is unusually low for the dose")
    return ("is-bad", "Very loose", "Yield is unusually high for the dose")


def star_row_html(rating: int) -> str:
    stars = "".join(
        f'<span class="star{" on" if i < rating else ""}">★</span>' for i in range(10)
    )
    return (
        f'<div class="star-row">{stars}'
        f'<span class="num">{rating}<small>/10</small></span></div>'
    )


# ────────────────────────────────────────────────────────────────────────────
# Page
# ────────────────────────────────────────────────────────────────────────────

def render_log_shot_page() -> None:
    st.markdown(THEME_CSS, unsafe_allow_html=True)

    now = datetime.now()

    # Top bar
    st.markdown(
        f"""
        <div class="et-topbar">
          <div class="et-brand">
            <span class="mark">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                <path d="M4 9h13a4 4 0 0 1 0 8h-1M4 9v6a4 4 0 0 0 4 4h5a4 4 0 0 0 4-4V9H4z"
                      stroke="#1a1108" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M8 3v3M12 3v3" stroke="#1a1108" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </span>
            Espresso Tracker <small>· shot log</small>
          </div>
          <div class="et-clock"><b>{now.strftime('%A')}</b> · {now.strftime('%b %d, %Y · %H:%M')}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Header
    st.markdown(
        """
        <div class="et-eyebrow">New entry</div>
        <h1 class="et-title">Pull a <em>shot</em>.</h1>
        <div class="et-subtitle">Capture the variables while the cup's still warm.</div>
        """,
        unsafe_allow_html=True,
    )

    # ── Live ratio readout (outside form so it updates on each rerun) ──
    dose = st.session_state.get("dose_g", 18.0)
    yield_ = st.session_state.get("yield_g", 36.0)
    ext_s = st.session_state.get("ext_s", 27.0)
    ratio = calc_ratio(dose, yield_)
    css_class, status_label, status_hint = ratio_status(ratio)

    ratio_display = (
        f'1<span class="colon">:</span>{ratio:.1f}' if ratio is not None else "1<span class=\"colon\">:</span>—"
    )
    flow_rate = f"{yield_ / ext_s:.2f}" if ext_s and ext_s > 0 and yield_ else "—"

    st.markdown(
        f"""
        <div class="ratio-hero {css_class}">
          <div class="ratio-row">
            <div>
              <div class="ratio-label">Brew ratio</div>
              <div class="ratio-number">{ratio_display}</div>
              <div class="ratio-status {css_class}">
                <span class="dot"></span>{status_label} · <span style="color:var(--muted)">{status_hint}</span>
              </div>
            </div>
            <div class="ratio-meta">
              <div class="row"><span>dose</span><span>{dose:g} g</span></div>
              <div class="row"><span>yield</span><span>{yield_:g} g</span></div>
              <div class="row"><span>time</span><span>{ext_s:g} s</span></div>
              <div class="row"><span>flow</span><span>{flow_rate} g/s</span></div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Form ──
    with st.form("log_shot_form", clear_on_submit=False):
        # Card 1 — Bean
        st.markdown(
            """
            <div class="et-card-head">
              <span class="et-card-title">The bean</span>
              <span class="et-card-step">01 / 04</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns([2, 1])
        with c1:
            bean_name = st.text_input("Coffee name", placeholder="e.g. Ethiopia Yirgacheffe — Heirloom",
                                       label_visibility="visible")
        with c2:
            roast = st.selectbox("Roast level", ROAST_LEVELS, index=2)

        c1, c2 = st.columns(2)
        with c1:
            d = st.date_input("Date", value=now.date())
        with c2:
            t = st.time_input("Time", value=now.time().replace(microsecond=0))

        st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

        # Card 2 — Grind / dose / yield / time
        st.markdown(
            """
            <div class="et-card-head">
              <span class="et-card-title">The pull</span>
              <span class="et-card-step">02 / 04</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        grind = st.slider("Grind size", min_value=1.0, max_value=30.0, value=3.5, step=0.1,
                          help="Use your grinder's scale.")
        c1, c2, c3 = st.columns(3)
        with c1:
            dose_in = st.number_input("Dose (g)", min_value=0.0, max_value=50.0,
                                       value=18.0, step=0.1, key="dose_g")
        with c2:
            yield_in = st.number_input("Yield (g)", min_value=0.0, max_value=120.0,
                                        value=36.0, step=0.1, key="yield_g")
        with c3:
            ext_in = st.number_input("Time (s)", min_value=0.0, max_value=120.0,
                                      value=27.0, step=0.5, key="ext_s")

        st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

        # Card 3 — Machine
        st.markdown(
            """
            <div class="et-card-head">
              <span class="et-card-title">The machine</span>
              <span class="et-card-step">03 / 04</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        c1, c2, c3 = st.columns([2, 1, 2])
        with c1:
            temp = st.number_input("Temperature", min_value=0.0, max_value=250.0,
                                    value=200.0, step=0.5)
        with c2:
            temp_unit = st.radio("Unit", ["°F", "°C"], horizontal=True, index=0,
                                  label_visibility="visible")
        with c3:
            pressure = st.number_input("Pressure (bars)", min_value=0.0, max_value=15.0,
                                        value=9.0, step=0.1)

        st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

        # Card 4 — Tasting + rating
        st.markdown(
            """
            <div class="et-card-head">
              <span class="et-card-title">In the cup</span>
              <span class="et-card-step">04 / 04</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        notes = st.text_area(
            "Tasting notes",
            placeholder="Body, acidity, sweetness, finish…",
        )
        rating = st.slider("Overall rating", min_value=1, max_value=10, value=7)
        st.markdown(star_row_html(rating), unsafe_allow_html=True)

        st.markdown("<div style='height:1.6rem'></div>", unsafe_allow_html=True)

        # Submit
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            submitted = st.form_submit_button("☕  Log this shot", type="primary")

    if not submitted:
        return

    # ── Validate ──
    errors = []
    if not bean_name.strip():
        errors.append("Coffee name is required.")
    if dose_in <= 0:
        errors.append("Dose must be greater than 0.")
    if yield_in <= 0:
        errors.append("Yield must be greater than 0.")
    if ext_in <= 0:
        errors.append("Extraction time must be greater than 0.")
    if errors:
        for e in errors:
            st.error(e)
        return

    final_ratio = calc_ratio(dose_in, yield_in)
    shot_time = datetime.combine(d, t)

    payload = {
        "shot_time":     shot_time,
        "bean_name":     bean_name.strip(),
        "roast_level":   roast,
        "grind_size":    float(grind),
        "dose_g":        float(dose_in),
        "yield_g":       float(yield_in),
        "extraction_s":  float(ext_in),
        "brew_ratio":    float(final_ratio) if final_ratio else None,
        "temperature":   float(temp),
        "temp_unit":     temp_unit.replace("°", ""),
        "pressure_bar":  float(pressure),
        "tasting_notes": notes.strip() or None,
        "rating":        int(rating),
    }

    try:
        new_id = insert_shot(payload)
    except Exception as exc:
        st.error(f"Could not save shot: {exc}")
        return

    # Success card + balloons
    st.markdown(
        f"""
        <div class="et-success">
          <div class="check">
            <svg width="22" height="22" viewBox="0 0 24 24">
              <path d="M5 12.5 l5 5 L20 7" />
            </svg>
          </div>
          <div>
            <h3>Shot logged.</h3>
            <p>#{new_id} &nbsp;·&nbsp; {dose_in:g} g → {yield_in:g} g in {ext_in:g} s
               &nbsp;·&nbsp; ratio <b>1 : {final_ratio}</b>
               &nbsp;·&nbsp; rated {rating}/10</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.balloons()


if __name__ == "__main__":
    st.set_page_config(
        page_title="Log a shot · Espresso Tracker",
        page_icon="☕",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    render_log_shot_page()
