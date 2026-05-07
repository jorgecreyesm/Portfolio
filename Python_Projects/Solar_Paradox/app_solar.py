"""
The Solar Paradox: Interactive Streamlit Dashboard
Why the World's Sunniest Countries Have the Least Solar Power
A Sociological Analysis of Global Solar Inequality

Author: Jorge Reyes-Ornelas
Analysis Tool: Streamlit (Interactive Web App)
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# PAGE CONFIG
st.set_page_config(
    page_title="Solar Paradox Analysis",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# STYLING
st.markdown("""
    <style>
    .header-section {
        border-bottom: 3px solid #F39C12;
        padding-bottom: 15px;
        margin-bottom: 25px;
    }
    .insight-box {
        background-color: #FEF5E7;
        padding: 15px;
        border-left: 4px solid #F39C12;
        border-radius: 5px;
        margin: 15px 0;
    }
    </style>
""", unsafe_allow_html=True)

# REGION COLOR PALETTE
REGION_PALETTE = {
    "North America": "#2980B9",
    "Europe":        "#16A085",
    "Oceania":       "#8E44AD",
    "Asia":          "#E67E22",
    "South America": "#27AE60",
    "Africa":        "#C0392B",
    "Middle East":   "#F39C12"
}

# ============================================================================
# DATA LOADING & CACHING
# ============================================================================

@st.cache_data
def load_data():
    """Load and prepare solar dataset"""
    import pathlib
    
    # Get path relative to this script
    current_dir = pathlib.Path(__file__).parent
    csv_file = current_dir / "solar_energy_worldwide.csv"
    
    df = pd.read_csv(csv_file)
    
    # Aggregate to country level
    country_df = (
        df.groupby(["Country", "Region"])[[
            "Solar_Installations_Count",
            "Annual_Sunlight_Hours",
            "GHI_kWh_per_m2",
            "Avg_Annual_Production_kWh",
            "Electricity_Price_USD_per_kWh",
            "Avg_System_Cost_USD",
            "Payback_Period_Years",
            "ROI_Percentage",
            "Estimated_Annual_Savings_USD",
            "CO2_Reduction_Tons_per_Year",
            "Solar_Viability_Score"
        ]]
        .mean()
        .reset_index()
    )
    
    # Engineer features
    country_df["Efficiency_Score"] = (
        country_df["Avg_Annual_Production_kWh"] /
        country_df["Solar_Installations_Count"]
    )
    
    country_df["Adoption_Gap"] = (
        country_df["GHI_kWh_per_m2"] /
        (country_df["Solar_Installations_Count"] + 1)
    ) * 1000
    
    return df, country_df

# Load data
df, country_df = load_data()

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

st.sidebar.markdown("# ☀️ Navigation")
page = st.sidebar.radio(
    "Select Analysis Section:",
    ["🌍 Overview", 
     "📊 The Paradox", 
     "💰 The ROI Paradox",
     "⏱️ The Payback Inequality",
     "📉 The Adoption Gap",
     "⭐ The Outliers",
     "🎯 Conclusions"]
)

# ============================================================================
# PAGE: OVERVIEW
# ============================================================================

if page == "🌍 Overview":
    st.markdown('<div class="header-section"><h1>☀️ The Solar Paradox</h1></div>', 
                unsafe_allow_html=True)
    st.markdown("### Why the World's Sunniest Countries Have the Least Solar Power")
    
    st.markdown("""
    ## The Question
    
    The transition to renewable energy is often framed as a **purely technical challenge** — 
    a question of panels, inverters, and grid infrastructure. But the global distribution of 
    solar adoption tells a different story.
    
    ### **The Paradox**
    
    Countries with the **highest solar potential** (measured by sunlight hours and solar irradiance) 
    are frequently **not** the countries with the **highest solar adoption**.
    
    ---
    
    ## The Data
    """)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Countries Analyzed", len(country_df))
    
    with col2:
        st.metric("Regions Covered", country_df['Region'].nunique())
    
    with col3:
        st.metric("Total Installations", f"{country_df['Solar_Installations_Count'].sum():,.0f}")
    
    with col4:
        st.metric("Avg GHI (kWh/m²)", f"{country_df['GHI_kWh_per_m2'].mean():.1f}")
    
    st.markdown("""
    ---
    
    ## The Core Argument
    
    This analysis applies a **sociological lens** to argue that the barriers to solar adoption 
    are **not geographic** — they are **structural**.
    
    **Capital access**, **institutional capacity**, and **historical inequality** shape the 
    global energy landscape as much as the sun itself.
    
    ### Key Questions Explored:
    
    1. **Does solar potential predict solar adoption?** → The Paradox
    2. **Which regions get the best ROI yet have the lowest adoption?** → The ROI Paradox
    3. **Where does solar take the longest to pay off?** → The Payback Inequality
    4. **Which regions are wasting the most potential?** → The Adoption Gap
    5. **Which countries are beating structural odds?** → The Outliers
    
    ---
    
    ## Methodology
    
    - **Data Source:** Global Solar Energy Dataset (48 cities, 30 countries, 7 regions)
    - **Aggregation:** City-level data rolled up to country averages
    - **Features Engineered:**
      - **Efficiency Score** = Annual production (kWh) per installation
      - **Adoption Gap** = GHI relative to installation count
    - **Visualization:** Regional color-coding for pattern recognition
    
    Navigate the sidebar to explore each analytical section.
    """)

# ============================================================================
# PAGE: THE PARADOX
# ============================================================================

elif page == "📊 The Paradox":
    st.markdown('<div class="header-section"><h1>📊 The Solar Paradox</h1></div>', 
                unsafe_allow_html=True)
    st.markdown("### Does solar potential predict solar adoption?")
    
    st.markdown("""
    This scatter plot reveals the central paradox of global solar adoption:
    
    - **Highest GHI regions (Africa, Middle East)** cluster at the bottom = lowest adoption
    - **Lowest GHI regions (Europe)** maintain highest adoption
    - **The sun is not the limiting factor**
    """)
    
    # Create the paradox plot
    fig, ax = plt.subplots(figsize=(14, 8))
    
    for region, group in country_df.groupby("Region"):
        ax.scatter(
            group["GHI_kWh_per_m2"],
            group["Solar_Installations_Count"],
            label=region,
            color=REGION_PALETTE.get(region, "#7F8C8D"),
            alpha=0.8,
            s=150,
            zorder=3,
            edgecolors='white',
            linewidth=1.5
        )
        
        for _, row in group.iterrows():
            ax.annotate(
                row["Country"],
                (row["GHI_kWh_per_m2"], row["Solar_Installations_Count"]),
                fontsize=8,
                alpha=0.7,
                xytext=(5, 5),
                textcoords="offset points"
            )
    
    ax.set_title(
        "The Solar Paradox: Solar Potential vs. Solar Adoption\n"
        "Does sunlight drive solar adoption?",
        fontsize=16, fontweight="bold", pad=20
    )
    ax.set_xlabel("Solar Potential — GHI (kWh per m²)", fontsize=13, fontweight='bold')
    ax.set_ylabel("Solar Installations Count", fontsize=13, fontweight='bold')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.grid(True, alpha=0.3)
    ax.legend(title="Region", bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=10)
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # Statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Highest GHI Regions")
        high_ghi = country_df.nlargest(5, 'GHI_kWh_per_m2')[['Country', 'Region', 'GHI_kWh_per_m2', 'Solar_Installations_Count']]
        st.dataframe(high_ghi, use_container_width=True)
    
    with col2:
        st.subheader("Highest Adoption Regions")
        high_adoption = country_df.nlargest(5, 'Solar_Installations_Count')[['Country', 'Region', 'GHI_kWh_per_m2', 'Solar_Installations_Count']]
        st.dataframe(high_adoption, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box">
    <strong>💡 Key Insight:</strong> The countries with the most sun are not the countries with the most solar panels. 
    This is not a market failure—it's a reflection of deeper structural inequality.
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# PAGE: ROI PARADOX
# ============================================================================

elif page == "💰 The ROI Paradox":
    st.markdown('<div class="header-section"><h1>💰 The ROI Paradox</h1></div>', 
                unsafe_allow_html=True)
    st.markdown("### Best Returns, Lowest Adoption")
    
    st.markdown("""
    Africa and the Middle East lead all regions in solar ROI (~14.5%) — yet have the fewest installations.
    
    **Why?** When the best financial returns don't drive investment, the barrier is **structural**: 
    **capital access**, not incentive, is the deciding factor.
    """)
    
    # Create ROI plot
    region_roi = (
        country_df.groupby("Region")[["ROI_Percentage", "Solar_Installations_Count"]]
        .mean()
        .reset_index()
        .sort_values("ROI_Percentage", ascending=True)
    )
    
    fig, ax = plt.subplots(figsize=(13, 7))
    
    bars = ax.barh(
        region_roi["Region"],
        region_roi["ROI_Percentage"],
        color=[REGION_PALETTE.get(r, "#7F8C8D") for r in region_roi["Region"]],
        alpha=0.85,
        edgecolor='white',
        linewidth=2
    )
    
    # Annotate with installation counts
    for bar, (_, row) in zip(bars, region_roi.iterrows()):
        ax.text(
            bar.get_width() + 0.2,
            bar.get_y() + bar.get_height() / 2,
            f"{int(row['Solar_Installations_Count']):,} installs",
            va="center", fontsize=11, fontweight='bold', color="#2C3E50"
        )
    
    ax.set_title(
        "The ROI Paradox: Best Returns, But Lowest Adoption\n"
        "Why don't investors follow the money?",
        fontsize=16, fontweight="bold", pad=20
    )
    ax.set_xlabel("Average ROI (%)", fontsize=12, fontweight='bold')
    ax.set_ylabel("Region", fontsize=12, fontweight='bold')
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.1f}%"))
    ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # Regional breakdown
    st.subheader("Regional ROI & Installation Counts")
    roi_table = region_roi[['Region', 'ROI_Percentage', 'Solar_Installations_Count']].copy()
    roi_table.columns = ['Region', 'Avg ROI (%)', 'Avg Installations']
    st.dataframe(roi_table, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box">
    <strong>💡 Key Insight:</strong> Africa averages 14.5% ROI but has ~1,000 installations. 
    Asia averages 11.2% ROI but has ~20,000 installations. 
    The difference isn't fundamentals—it's access to capital.
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# PAGE: PAYBACK INEQUALITY
# ============================================================================

elif page == "⏱️ The Payback Inequality":
    st.markdown('<div class="header-section"><h1>⏱️ The Payback Inequality</h1></div>', 
                unsafe_allow_html=True)
    st.markdown("### Where Solar Takes the Longest to Break Even")
    
    st.markdown("""
    This scatter reveals a stark structural inequality:
    
    - **Top-right quadrant** (high sun + long payback) = most disadvantaged
    - **High-GHI countries** face 13–15 year paybacks
    - **Lower-GHI countries** (Europe) face 13–15 year paybacks but have capital to absorb the wait
    """)
    
    # Create payback plot
    fig, ax = plt.subplots(figsize=(14, 8))
    
    for region, group in country_df.groupby("Region"):
        ax.scatter(
            group["GHI_kWh_per_m2"],
            group["Payback_Period_Years"],
            label=region,
            color=REGION_PALETTE.get(region, "#7F8C8D"),
            alpha=0.8,
            s=150,
            zorder=3,
            edgecolors='white',
            linewidth=1.5
        )
        
        for _, row in group.iterrows():
            ax.annotate(
                row["Country"],
                (row["GHI_kWh_per_m2"], row["Payback_Period_Years"]),
                fontsize=8,
                alpha=0.7,
                xytext=(5, 5),
                textcoords="offset points"
            )
    
    # Add median lines
    median_ghi = country_df["GHI_kWh_per_m2"].median()
    median_payback = country_df["Payback_Period_Years"].median()
    
    ax.axvline(median_ghi, color="gray", linestyle="--", alpha=0.5, linewidth=2, label="Median GHI")
    ax.axhline(median_payback, color="gray", linestyle=":", alpha=0.5, linewidth=2, label="Median Payback")
    
    ax.set_title(
        "The Payback Inequality: Solar Potential vs. Years to Break Even\n"
        "Top-right quadrant = high sun, longest wait = structural disadvantage",
        fontsize=16, fontweight="bold", pad=20
    )
    ax.set_xlabel("Solar Potential — GHI (kWh per m²)", fontsize=13, fontweight='bold')
    ax.set_ylabel("Payback Period (Years)", fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(title="Region", bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=10)
    
    plt.tight_layout()
    st.pyplot(fig)
    
    st.markdown("""
    <div class="insight-box">
    <strong>💡 Key Insight:</strong> Countries that need renewable energy most urgently 
    (high GHI but limited capital) face the longest payback periods. 
    Countries with capital (Europe) can absorb long paybacks. This is inequality encoded in physics and economics.
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# PAGE: ADOPTION GAP
# ============================================================================

elif page == "📉 The Adoption Gap":
    st.markdown('<div class="header-section"><h1>📉 The Adoption Gap</h1></div>', 
                unsafe_allow_html=True)
    st.markdown("### Which Regions Are Wasting the Most Solar Potential?")
    
    st.markdown("""
    The Adoption Gap Score measures how much solar potential is going unused per country.
    
    **Higher score = more potential being wasted = structural barrier preventing deployment**
    """)
    
    # Create adoption gap plot
    region_gap = (
        country_df.groupby("Region")["Adoption_Gap"]
        .mean()
        .reset_index()
        .sort_values("Adoption_Gap", ascending=True)
    )
    
    fig, ax = plt.subplots(figsize=(13, 7))
    
    ax.barh(
        region_gap["Region"],
        region_gap["Adoption_Gap"],
        color=[REGION_PALETTE.get(r, "#7F8C8D") for r in region_gap["Region"]],
        alpha=0.85,
        edgecolor='white',
        linewidth=2
    )
    
    ax.set_title(
        "The Adoption Gap: Wasted Solar Potential by Region\n"
        "How much free renewable energy is being left on the table?",
        fontsize=16, fontweight="bold", pad=20
    )
    ax.set_xlabel("Adoption Gap Score (Higher = More Wasted Potential)", fontsize=12, fontweight='bold')
    ax.set_ylabel("Region", fontsize=12, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    st.pyplot(fig)
    
    st.subheader("Adoption Gap by Region")
    gap_table = region_gap.copy()
    gap_table.columns = ['Region', 'Adoption Gap Score']
    st.dataframe(gap_table, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box">
    <strong>💡 Key Insight:</strong> South America, Middle East, and Africa have the highest adoption gap scores—
    the largest mismatch between potential and actual installations. 
    Europe and Oceania, which have converted their potential most efficiently, sit at the bottom.
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# PAGE: OUTLIERS
# ============================================================================

elif page == "⭐ The Outliers":
    st.markdown('<div class="header-section"><h1>⭐ Beating the Odds</h1></div>', 
                unsafe_allow_html=True)
    st.markdown("### Which High-Potential Countries Are Overperforming?")
    
    # Identify overperformers
    median_ghi = country_df["GHI_kWh_per_m2"].median()
    median_installs = country_df["Solar_Installations_Count"].median()
    
    overperformers = country_df[
        (country_df["GHI_kWh_per_m2"] >= median_ghi) &
        (country_df["Solar_Installations_Count"] >= median_installs)
    ].copy()
    
    underperformers = country_df[
        (country_df["GHI_kWh_per_m2"] >= median_ghi) &
        (country_df["Solar_Installations_Count"] < median_installs)
    ].copy()
    
    # Plot
    fig, ax = plt.subplots(figsize=(14, 8))
    
    ax.scatter(
        underperformers["GHI_kWh_per_m2"],
        underperformers["Solar_Installations_Count"],
        color="#C0392B", alpha=0.8, s=150,
        label="Underperforming (high sun, low adoption)", zorder=3,
        edgecolors='white', linewidth=1.5
    )
    
    ax.scatter(
        overperformers["GHI_kWh_per_m2"],
        overperformers["Solar_Installations_Count"],
        color="#27AE60", alpha=0.8, s=150,
        label="Overperforming (high sun, high adoption)", zorder=3,
        edgecolors='white', linewidth=1.5
    )
    
    for _, row in pd.concat([overperformers, underperformers]).iterrows():
        ax.annotate(
            row["Country"],
            (row["GHI_kWh_per_m2"], row["Solar_Installations_Count"]),
            fontsize=8, alpha=0.75,
            xytext=(5, 5), textcoords="offset points"
        )
    
    ax.axvline(median_ghi, color="gray", linestyle="--", alpha=0.5, linewidth=2, label="Median GHI")
    ax.axhline(median_installs, color="gray", linestyle=":", alpha=0.5, linewidth=2, label="Median Installations")
    
    ax.set_title(
        "Beating the Odds: Overperformers Among High Solar Potential Countries\n"
        "Which countries overcome structural barriers?",
        fontsize=16, fontweight="bold", pad=20
    )
    ax.set_xlabel("Solar Potential — GHI (kWh per m²)", fontsize=13, fontweight='bold')
    ax.set_ylabel("Solar Installations Count", fontsize=13, fontweight='bold')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.grid(True, alpha=0.3)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=10)
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # Show overperformers table
    st.subheader("🌟 Overperformers: Countries Beating Structural Odds")
    if len(overperformers) > 0:
        overperf_table = overperformers[['Country', 'Region', 'GHI_kWh_per_m2', 'Solar_Installations_Count', 'Payback_Period_Years']].copy()
        overperf_table.columns = ['Country', 'Region', 'GHI', 'Installations', 'Payback (yrs)']
        st.dataframe(overperf_table, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box">
    <strong>💡 Key Insight:</strong> India is the standout developing country beating structural odds—
    high GHI and 73,000+ installations. Spain and Greece represent European overperformers. 
    These outliers prove that policy intervention and institutional investment can overcome structural barriers.
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# PAGE: CONCLUSIONS
# ============================================================================

elif page == "🎯 Conclusions":
    st.markdown('<div class="header-section"><h1>🎯 Key Findings</h1></div>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    ## The Core Argument
    
    **The global solar map is not shaped by sunlight. It is shaped by the same forces that 
    shape every other form of capital investment — access, infrastructure, and institutional power.**
    
    ---
    
    ## Five Paradoxes Explained
    
    ### 1. **The Paradox** ☀️
    Solar potential (GHI) does **not** predict solar adoption. Africa and the Middle East — 
    the highest GHI regions — cluster at the bottom of the installation axis. Europe, with 
    some of the lowest solar potential, maintains meaningful adoption.
    
    **Finding:** *The sun is not the limiting factor.*
    
    ---
    
    ### 2. **The ROI Paradox** 💰
    Africa and the Middle East lead all regions in solar ROI at ~14.5% — yet have fewer than 
    1,000–1,100 installations each. Asia and North America, with lower ROI figures, have tens 
    of thousands of installations.
    
    **Finding:** *When the best financial returns don't drive investment, the barrier is structural 
    — capital access, not incentive, is the deciding factor.*
    
    ---
    
    ### 3. **The Payback Inequality** ⏱️
    High-GHI countries in Africa and the Middle East have some of the shortest payback periods 
    (6–7 years). Europe, which leads in adoption, faces payback periods of 13–15 years.
    
    **Finding:** *Countries are investing in solar where it takes the longest to break even, 
    while ignoring markets where returns are fastest.*
    
    ---
    
    ### 4. **The Adoption Gap** 📉
    South America, the Middle East, and Africa have the highest adoption gap scores — the largest 
    mismatch between potential and actual installations. Europe and Oceania, which have converted 
    their potential most efficiently, sit at the bottom.
    
    **Finding:** *The countries that need renewable energy most urgently are the least equipped to deploy it.*
    
    ---
    
    ### 5. **The Outliers** ⭐
    India is the standout developing country beating structural odds — high GHI and 73,000 installations. 
    Spain and Greece represent European overperformers.
    
    **Finding:** *Policy intervention and institutional investment can overcome structural barriers 
    when the will exists.*
    
    ---
    
    ## The Sociological Frame
    
    This is **not an energy problem. It is a sociological one.**
    
    The countries that **need renewable energy most urgently**, and would **benefit from it most 
    financially**, are the **least equipped to deploy it at scale**. This reflects deeper patterns 
    of global inequality:
    
    - **Capital Access**: Wealthy nations can absorb long payback periods
    - **Institutional Capacity**: Rich markets have financing, grid infrastructure, technical expertise
    - **Historical Inequality**: Colonial legacies and unequal development create structural disadvantages
    
    ---
    
    ## Data Summary
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Installations", f"{country_df['Solar_Installations_Count'].sum():,.0f}")
    
    with col2:
        st.metric("Average Payback Period", f"{country_df['Payback_Period_Years'].mean():.1f} years")
    
    with col3:
        st.metric("Average ROI", f"{country_df['ROI_Percentage'].mean():.1f}%")
    
    st.markdown("""
    ---
    
    ## What This Means
    
    The global solar map reveals that **renewable energy deployment is not primarily a technical 
    or economic problem**—it's a **structural inequality problem**.
    
    Solutions require not just better technology or economic incentives, but:
    
    1. **Capital mobilization** for high-potential, low-capital regions
    2. **Institutional capacity building** (financing, grid infrastructure, expertise)
    3. **Policy leverage** (see: India's success with deliberate policy intervention)
    4. **Technology transfer** from developed to developing markets
    
    The outliers prove it's possible. The question is whether we have the political will.
    """)

# FOOTER
st.markdown("""
---
**About This Analysis**

**Author:** Jorge Reyes-Ornelas  
**Data Source:** Global Solar Energy Dataset (48 cities, 30 countries, 7 regions)  
**Tools:** Python, Streamlit, pandas, matplotlib  
**Framework:** Sociological Analysis of Global Solar Inequality

*Bridging data analysis, structural thinking, and real-world impact.*
""")
