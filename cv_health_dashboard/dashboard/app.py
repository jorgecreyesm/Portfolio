"""
Central Valley Community Health & Economic Dashboard -- Streamlit app.

Reads directly from PostgreSQL (dim_county + the four fact tables) and
lays out five views: an overview, economic trends, health outcomes,
agricultural economics, and a correlations explorer. Every chart uses a
fixed county->color mapping so the same county reads as the same color
everywhere in the app.

Run:
    streamlit run dashboard/app.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.config import CPI_BASE_YEAR
from src.load.postgres import get_engine

# ---------------------------------------------------------------------------
# Palette -- fixed categorical order, validated for colorblind-safe adjacent
# contrast. Counties are assigned a slot in a stable order so the same
# county is always the same color across every chart in the app.
# ---------------------------------------------------------------------------
COUNTY_COLORS = {
    "Fresno": "#2a78d6",       # blue
    "Kings": "#1baf7a",        # aqua
    "Madera": "#eda100",       # yellow
    "Merced": "#008300",       # green
    "San Joaquin": "#4a3aa7",  # violet
    "Stanislaus": "#e34948",   # red
    "Tulare": "#e87ba4",       # magenta
}
SEQUENTIAL_BLUE = ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]

st.set_page_config(
    page_title="Central Valley Community Health & Economic Dashboard",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
def _database_url() -> str | None:
    """
    Connection string for the deployed app. Streamlit Community Cloud
    supplies secrets through st.secrets rather than the environment, so
    read it here and hand it to get_engine(); locally there is no secrets
    file and get_engine() falls back to .env. Accessing st.secrets with no
    secrets configured raises, hence the guard.
    """
    try:
        return st.secrets["DATABASE_URL"]
    except Exception:
        return None


@st.cache_data(ttl=600)
def load_data() -> dict[str, pd.DataFrame]:
    engine = get_engine(_database_url())
    county = pd.read_sql("SELECT * FROM dim_county", engine)
    acs = pd.read_sql("SELECT * FROM fact_acs ORDER BY acs_year", engine)
    nass = pd.read_sql("SELECT * FROM fact_nass ORDER BY nass_year", engine)
    cdc = pd.read_sql("SELECT * FROM fact_cdc_places", engine)
    chhs = pd.read_sql("SELECT * FROM fact_chhs_deaths ORDER BY death_year", engine)

    for df in (acs, nass, cdc, chhs):
        df["fips"] = df["fips"].astype(str).str.zfill(5)
    county["fips"] = county["fips"].astype(str).str.zfill(5)

    acs = acs.merge(county, on="fips")
    nass = nass.merge(county, on="fips")
    cdc = cdc.merge(county, on="fips")
    chhs = chhs.merge(county, on="fips")

    return {"county": county, "acs": acs, "nass": nass, "cdc": cdc, "chhs": chhs}


try:
    data = load_data()
except Exception as exc:
    st.error(
        "Could not connect to PostgreSQL. Make sure the database is running and "
        "the pipeline has been loaded at least once (`python -m src.pipeline`).\n\n"
        f"Error: {exc}"
    )
    st.stop()

acs, nass, cdc, chhs = data["acs"], data["nass"], data["cdc"], data["chhs"]
all_counties = sorted(data["county"]["county_name"])


def color_map(counties: list[str]) -> dict[str, str]:
    return {c: COUNTY_COLORS[c] for c in counties}


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
st.sidebar.title("Filters")
selected_counties = st.sidebar.multiselect(
    "Counties", options=all_counties, default=all_counties
)
if not selected_counties:
    st.sidebar.warning("Select at least one county.")
    st.stop()

st.sidebar.markdown("---")
st.sidebar.caption(
    "**Data vintages**\n\n"
    f"- ACS 5-year: {int(acs['acs_year'].min())}–{int(acs['acs_year'].max())}\n"
    f"- NASS Census of Ag: {', '.join(str(y) for y in sorted(nass['nass_year'].unique()))}\n"
    f"- CDC PLACES: {int(cdc['release_year'].iloc[0])} release (BRFSS 2022–23)\n"
    f"- CHHS deaths: {int(chhs['death_year'].min())}–{int(chhs['death_year'].max())}"
)

acs_f = acs[acs["county_name"].isin(selected_counties)]
nass_f = nass[nass["county_name"].isin(selected_counties)]
cdc_f = cdc[cdc["county_name"].isin(selected_counties)]
chhs_f = chhs[chhs["county_name"].isin(selected_counties)]

cmap = color_map(selected_counties)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("Central Valley Community Health & Economic Dashboard")
st.markdown(
    "Economic conditions and community health outcomes across seven San Joaquin "
    "Valley counties: Fresno, Kings, Madera, Merced, San Joaquin, Stanislaus, and Tulare."
)

tab_overview, tab_econ, tab_health, tab_ag, tab_covid, tab_corr, tab_data = st.tabs(
    ["Overview", "Economic Trends", "Health Outcomes", "Agriculture",
     "COVID Impact", "Correlations", "Data"]
)

# ---------------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------------
with tab_overview:
    latest_year = int(acs_f["acs_year"].max())
    latest = acs_f[acs_f["acs_year"] == latest_year]
    latest_chhs = chhs_f[chhs_f["death_year"] == int(chhs_f["death_year"].max())]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(f"Avg. poverty rate ({latest_year})", f"{latest['poverty_rate'].mean():.1f}%")
    col2.metric(f"Avg. unemployment ({latest_year})", f"{latest['unemployment_rate'].mean():.1f}%")
    col3.metric("Avg. all-cause deaths /100k", f"{latest_chhs['deaths_all_causes_per_100k'].mean():.0f}")
    col4.metric("Avg. diabetes prevalence", f"{cdc_f['diabetes_pct'].mean():.1f}%")

    st.markdown(f"#### Poverty rate by county, {latest_year}")
    fig = px.bar(
        latest.sort_values("poverty_rate"),
        x="poverty_rate", y="county_name", orientation="h",
        color="county_name", color_discrete_map=cmap,
        labels={"poverty_rate": "Poverty rate (%)", "county_name": ""},
    )
    fig.update_layout(showlegend=False, template="plotly_white")
    st.plotly_chart(fig, width="stretch")

    st.info(
        "**Limitations:** ACS 5-year estimates are rolling averages, not point-in-time "
        "figures. CDC PLACES values are model-based small-area estimates. Correlations "
        "shown elsewhere in this dashboard are county-level associations across a small "
        "sample of counties and years -- they do not establish causation and are "
        "vulnerable to ecological fallacy."
    )

# ---------------------------------------------------------------------------
# Economic Trends
# ---------------------------------------------------------------------------
with tab_econ:
    st.markdown("#### Economic indicators over time (ACS 5-year estimates)")

    metric = st.selectbox(
        "Metric",
        options=[
            ("poverty_rate", "Poverty rate (%)"),
            ("unemployment_rate", "Unemployment rate (%)"),
            ("median_household_income", "Median household income ($)"),
            ("homeownership_rate", "Homeownership rate (%)"),
            ("bachelors_or_higher_pct", "Bachelor's degree or higher (%)"),
        ],
        format_func=lambda x: x[1],
    )
    col, label = metric

    fig = px.line(
        acs_f.sort_values("acs_year"),
        x="acs_year", y=col, color="county_name",
        color_discrete_map=cmap, markers=True,
        labels={"acs_year": "ACS 5-year vintage", col: label, "county_name": "County"},
    )
    fig.update_layout(template="plotly_white", hovermode="x unified")
    st.plotly_chart(fig, width="stretch")

# ---------------------------------------------------------------------------
# Health Outcomes
# ---------------------------------------------------------------------------
with tab_health:
    st.markdown("#### Chronic disease & behavior prevalence (CDC PLACES)")

    measure = st.selectbox(
        "Measure",
        options=[
            ("obesity_pct", "Obesity"), ("diabetes_pct", "Diabetes"),
            ("high_blood_pressure_pct", "High blood pressure"),
            ("coronary_heart_disease_pct", "Coronary heart disease"),
            ("copd_pct", "COPD"), ("asthma_pct", "Asthma"),
            ("depression_pct", "Depression"), ("smoking_pct", "Smoking"),
            ("no_health_insurance_pct", "No health insurance"),
            ("no_leisure_activity_pct", "No leisure-time physical activity"),
        ],
        format_func=lambda x: x[1],
    )
    mcol, mlabel = measure

    fig = px.bar(
        cdc_f.sort_values(mcol),
        x=mcol, y="county_name", orientation="h",
        color="county_name", color_discrete_map=cmap,
        labels={mcol: f"{mlabel} (%)", "county_name": ""},
    )
    fig.update_layout(showlegend=False, template="plotly_white")
    st.plotly_chart(fig, width="stretch")

    st.markdown("#### Mortality rate by leading cause, over time (CHHS)")
    cause = st.selectbox(
        "Cause of death",
        options=[
            ("deaths_all_causes_per_100k", "All causes"),
            ("deaths_heart_disease_per_100k", "Heart disease"),
            ("deaths_cancer_per_100k", "Cancer"),
            ("deaths_stroke_per_100k", "Stroke"),
            ("deaths_diabetes_per_100k", "Diabetes"),
            ("deaths_chronic_lower_respiratory_per_100k", "Chronic lower respiratory disease"),
            ("deaths_suicide_per_100k", "Suicide"),
        ],
        format_func=lambda x: x[1],
    )
    ccol, clabel = cause

    fig2 = px.line(
        chhs_f.sort_values("death_year"),
        x="death_year", y=ccol, color="county_name",
        color_discrete_map=cmap, markers=True,
        labels={"death_year": "Year", ccol: f"{clabel} deaths per 100k", "county_name": "County"},
    )
    fig2.update_layout(template="plotly_white", hovermode="x unified")
    st.plotly_chart(fig2, width="stretch")
    st.caption("Deaths among county residents, regardless of where death occurred.")

# ---------------------------------------------------------------------------
# Agriculture
# ---------------------------------------------------------------------------
with tab_ag:
    st.markdown("#### Farm economics, Census of Agriculture years")

    ag_metric = st.selectbox(
        "Metric",
        options=[
            ("total_ag_sales", "Total agricultural sales ($)"),
            ("avg_sales_per_farm", "Average sales per farm ($)"),
            ("farm_land_building_value", "Farm land & building value ($)"),
            ("avg_farm_size_acres", "Average farm size (acres)"),
            ("farm_operations_count", "Number of farm operations"),
        ],
        format_func=lambda x: x[1],
    )
    acol, alabel = ag_metric

    fig = px.line(
        nass_f.sort_values("nass_year"),
        x="nass_year", y=acol, color="county_name",
        color_discrete_map=cmap, markers=True,
        labels={"nass_year": "Census of Agriculture year", acol: alabel, "county_name": "County"},
    )
    fig.update_layout(template="plotly_white", hovermode="x unified")
    st.plotly_chart(fig, width="stretch")
    st.caption(
        "County-level agricultural totals only exist in the Census of Agriculture "
        "(every 5 years), not the annual NASS survey."
    )

# ---------------------------------------------------------------------------
# COVID Impact
# ---------------------------------------------------------------------------
with tab_covid:
    st.markdown("### The pandemic and the inflation that followed")
    st.markdown(
        "Two shocks land back to back in this data: a mortality spike in 2020–2021, "
        "then the 2021–2023 inflation surge that eroded the income gains counties "
        "posted on paper. This view separates the signal from the nominal numbers."
    )

    BASELINE_YEARS = [2018, 2019]

    # --- Excess mortality vs. pre-pandemic baseline ---
    st.markdown("#### Excess all-cause mortality vs. 2018–19 baseline")

    baseline = (
        chhs_f[chhs_f["death_year"].isin(BASELINE_YEARS)]
        .groupby(["fips", "county_name"])["deaths_all_causes_per_100k"]
        .mean()
        .reset_index()
        .rename(columns={"deaths_all_causes_per_100k": "baseline"})
    )
    excess = chhs_f.merge(baseline, on=["fips", "county_name"])
    excess["excess_per_100k"] = excess["deaths_all_causes_per_100k"] - excess["baseline"]

    peak_year = int(
        excess.groupby("death_year")["excess_per_100k"].mean().idxmax()
    )
    peak_excess = excess[excess["death_year"] == peak_year]["excess_per_100k"].mean()
    latest_death_year = int(excess["death_year"].max())
    latest_excess = excess[excess["death_year"] == latest_death_year]["excess_per_100k"].mean()

    m1, m2, m3 = st.columns(3)
    m1.metric("Peak excess-mortality year", str(peak_year))
    m2.metric(f"Avg. excess deaths /100k ({peak_year})", f"+{peak_excess:.0f}")
    m3.metric(
        f"Still above baseline ({latest_death_year})",
        f"+{latest_excess:.0f}",
        help="Deaths per 100k above the 2018–19 average. A positive value means "
             "mortality had not returned to its pre-pandemic level.",
    )

    fig = px.line(
        excess.sort_values("death_year"),
        x="death_year", y="excess_per_100k", color="county_name",
        color_discrete_map=cmap, markers=True,
        labels={"death_year": "Year", "excess_per_100k": "Excess deaths per 100k",
                "county_name": "County"},
    )
    fig.add_hline(y=0, line_dash="dash", line_color="#52514e",
                  annotation_text="2018–19 baseline", annotation_position="top left")
    fig.update_layout(template="plotly_white", hovermode="x unified")
    st.plotly_chart(fig, width="stretch")
    st.caption(
        "Baseline is each county's own 2018–19 average all-cause death rate, so every "
        "line starts from that county's normal, not a shared one."
    )

    # --- Nominal vs. real income ---
    st.markdown(f"#### Nominal vs. real median household income (constant {CPI_BASE_YEAR} dollars)")

    income_county = st.selectbox(
        "County", options=sorted(acs_f["county_name"].unique()), key="covid_income_county"
    )
    inc = acs_f[acs_f["county_name"] == income_county].sort_values("acs_year")
    inc_long = inc.melt(
        id_vars="acs_year",
        value_vars=["median_household_income", "median_household_income_real"],
        var_name="measure", value_name="income",
    )
    inc_long["measure"] = inc_long["measure"].map({
        "median_household_income": "Nominal (as reported)",
        "median_household_income_real": f"Real ({CPI_BASE_YEAR} dollars)",
    })

    fig2 = px.line(
        inc_long, x="acs_year", y="income", color="measure",
        color_discrete_map={
            "Nominal (as reported)": "#2a78d6",
            f"Real ({CPI_BASE_YEAR} dollars)": "#eb6834",
        },
        markers=True,
        labels={"acs_year": "ACS 5-year vintage", "income": "Median household income ($)",
                "measure": ""},
    )
    fig2.update_layout(template="plotly_white", hovermode="x unified")
    st.plotly_chart(fig2, width="stretch")

    nominal_change = (inc["median_household_income"].iloc[-1] / inc["median_household_income"].iloc[0] - 1) * 100
    real_change = (inc["median_household_income_real"].iloc[-1] / inc["median_household_income_real"].iloc[0] - 1) * 100
    first_year, last_year = int(inc["acs_year"].iloc[0]), int(inc["acs_year"].iloc[-1])
    c1, c2 = st.columns(2)
    c1.metric(f"Nominal income change {first_year}→{last_year}", f"+{nominal_change:.0f}%")
    c2.metric(
        f"Real income change {first_year}→{last_year}", f"{real_change:+.0f}%",
        help="The gap between these two numbers is inflation eating the paycheck. "
             "Deflated with the BLS CPI-U annual average.",
    )
    st.caption(
        "Real income deflated using the CPI-U annual average (all items, U.S. city "
        "average, BLS). The lines diverge as post-2021 inflation outpaces wage growth."
    )

# ---------------------------------------------------------------------------
# Correlations
# ---------------------------------------------------------------------------
with tab_corr:
    st.markdown("#### Economic condition vs. health outcome")
    st.warning(
        f"This compares **{len(selected_counties)} counties** at a single point in "
        "time. A correlation coefficient over this few observations is illustrative, "
        "not statistically robust -- treat it as a starting hypothesis, not a finding. "
        "See the Limitations note on the Overview tab."
    )

    econ_options = [
        ("poverty_rate", "Poverty rate (%)"),
        ("unemployment_rate", "Unemployment rate (%)"),
        ("median_household_income", "Median household income ($)"),
        ("bachelors_or_higher_pct", "Bachelor's degree or higher (%)"),
    ]
    health_options = [
        ("obesity_pct", "Obesity (%)"), ("diabetes_pct", "Diabetes (%)"),
        ("high_blood_pressure_pct", "High blood pressure (%)"),
        ("smoking_pct", "Smoking (%)"),
        ("deaths_all_causes_per_100k", "All-cause deaths per 100k"),
        ("deaths_heart_disease_per_100k", "Heart disease deaths per 100k"),
    ]

    c1, c2 = st.columns(2)
    x_choice = c1.selectbox("Economic metric (x-axis)", econ_options, format_func=lambda x: x[1])
    y_choice = c2.selectbox("Health metric (y-axis)", health_options, format_func=lambda x: x[1])

    latest_acs_year = int(acs_f["acs_year"].max())
    x_df = acs_f[acs_f["acs_year"] == latest_acs_year][["county_name", x_choice[0]]]

    if y_choice[0].startswith("deaths_"):
        latest_death_year = int(chhs_f["death_year"].max())
        y_df = chhs_f[chhs_f["death_year"] == latest_death_year][["county_name", y_choice[0]]]
    else:
        y_df = cdc_f[["county_name", y_choice[0]]]

    merged = x_df.merge(y_df, on="county_name").dropna()

    if len(merged) >= 3:
        r = np.corrcoef(merged[x_choice[0]], merged[y_choice[0]])[0, 1]
    else:
        r = float("nan")

    fig = px.scatter(
        merged, x=x_choice[0], y=y_choice[0], color="county_name",
        color_discrete_map=cmap, text="county_name",
        labels={x_choice[0]: x_choice[1], y_choice[0]: y_choice[1]},
    )
    fig.update_traces(textposition="top center", marker=dict(size=12))

    if len(merged) >= 3 and merged[x_choice[0]].std() > 0:
        slope, intercept = np.polyfit(merged[x_choice[0]], merged[y_choice[0]], 1)
        x_range = np.linspace(merged[x_choice[0]].min(), merged[x_choice[0]].max(), 50)
        fig.add_trace(go.Scatter(
            x=x_range, y=slope * x_range + intercept, mode="lines",
            line=dict(color="#52514e", width=2, dash="dot"),
            name="Trend", showlegend=False,
        ))

    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, width="stretch")

    if not np.isnan(r):
        st.metric("Pearson correlation (r)", f"{r:.2f}", help="n = " + str(len(merged)))
    else:
        st.caption("Not enough overlapping data points to compute a correlation.")

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
with tab_data:
    st.markdown("#### Underlying data")
    source = st.selectbox("Table", ["fact_acs", "fact_nass", "fact_cdc_places", "fact_chhs_deaths"])
    table_map = {"fact_acs": acs_f, "fact_nass": nass_f, "fact_cdc_places": cdc_f, "fact_chhs_deaths": chhs_f}
    df_view = table_map[source]
    st.dataframe(df_view, width="stretch")
    st.download_button(
        "Download as CSV",
        df_view.to_csv(index=False).encode("utf-8"),
        file_name=f"{source}.csv",
        mime="text/csv",
    )
