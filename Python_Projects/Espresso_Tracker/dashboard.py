import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_conn

st.set_page_config(page_title="Espresso Tracker", page_icon="☕", layout="wide")
st.title("Espresso Shot Tracker")

@st.cache_data(ttl=30)
def load_shots():
    query = """
        SELECT
            s.id,
            s.shot_at,
            b.name        AS bean,
            b.roast_level AS roast,
            s.dose_g,
            s.yield_g,
            s.ratio,
            s.time_sec,
            s.grind_setting,
            s.taste_rating,
            s.notes
        FROM shots s
        JOIN beans b ON b.id = s.bean_id
        ORDER BY s.shot_at DESC
    """
    with get_conn() as conn:
        return pd.read_sql(query, conn)

df = load_shots()

if df.empty:
    st.info("No shots logged yet. Run `python log_shot.py` to add your first shot.")
    st.stop()

# --- Summary row ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Shots", len(df))
col2.metric("Avg Taste", f"{df['taste_rating'].mean():.1f} / 5")
col3.metric("Avg Ratio", f"1:{df['ratio'].mean():.2f}")
col4.metric("Avg Time", f"{df['time_sec'].mean():.0f}s")

st.divider()

# --- Taste over time ---
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Taste Rating Over Time")
    fig = px.scatter(
        df.sort_values("shot_at"),
        x="shot_at", y="taste_rating",
        color="bean", size_max=10,
        hover_data=["dose_g", "yield_g", "ratio", "time_sec", "grind_setting", "notes"],
        labels={"shot_at": "Date", "taste_rating": "Rating (1–5)"},
    )
    fig.update_yaxes(range=[0, 5.5], dtick=1)
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.subheader("Brew Ratio vs Taste")
    fig2 = px.scatter(
        df,
        x="ratio", y="taste_rating",
        color="bean", trendline="ols",
        hover_data=["dose_g", "yield_g", "time_sec", "grind_setting", "notes"],
        labels={"ratio": "Brew Ratio (yield/dose)", "taste_rating": "Rating (1–5)"},
    )
    fig2.update_yaxes(range=[0, 5.5], dtick=1)
    st.plotly_chart(fig2, use_container_width=True)

# --- Shot time distribution ---
col_c, col_d = st.columns(2)

with col_c:
    st.subheader("Shot Time vs Taste")
    fig3 = px.scatter(
        df,
        x="time_sec", y="taste_rating",
        color="bean", trendline="ols",
        labels={"time_sec": "Shot Time (s)", "taste_rating": "Rating (1–5)"},
    )
    fig3.update_yaxes(range=[0, 5.5], dtick=1)
    st.plotly_chart(fig3, use_container_width=True)

with col_d:
    st.subheader("Best Shots (Rating ≥ 4)")
    best = df[df["taste_rating"] >= 4][
        ["shot_at", "bean", "dose_g", "yield_g", "ratio", "time_sec", "grind_setting", "taste_rating", "notes"]
    ].rename(columns={
        "shot_at": "Date", "bean": "Bean", "dose_g": "Dose (g)",
        "yield_g": "Yield (g)", "ratio": "Ratio", "time_sec": "Time (s)",
        "grind_setting": "Grind", "taste_rating": "Rating", "notes": "Notes"
    })
    best["Date"] = best["Date"].dt.strftime("%Y-%m-%d %H:%M")
    st.dataframe(best, use_container_width=True, hide_index=True)

# --- Full log ---
st.divider()
st.subheader("Full Shot Log")
display = df.copy()
display["shot_at"] = display["shot_at"].dt.strftime("%Y-%m-%d %H:%M")
display.columns = [c.replace("_", " ").title() for c in display.columns]
st.dataframe(display, use_container_width=True, hide_index=True)
