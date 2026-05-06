"""
California Housing Market Analysis: Interactive Streamlit App
Local Housing Market Case Study with Los Banos Deep Dive

This app visualizes home value trends across California (2021-2026) with a focus
on Los Banos, a mid-Central Valley city functioning as a Bay Area affordability hub.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# PAGE CONFIGURATION
st.set_page_config(
    page_title="CA Housing Market Analysis",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CUSTOM STYLING
st.markdown("""
    <style>
    .metric-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .header-section {
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# LOAD AND PREPARE DATA
@st.cache_data
def load_data():
    """Load and transform the Zillow dataset"""
    housing_df = pd.read_csv("city_homevalue_zillow.csv")
    
    # Filter to California
    ca_housing = housing_df[housing_df['State'] == 'CA'].copy()
    
    # Get date columns from 2021 onward
    all_dates = [col for col in ca_housing.columns if col.startswith(('19', '20'))]
    recent_dates = [col for col in all_dates if col >= '2021-01-01']
    
    # Reshape to long format
    cols_to_keep = ['RegionName', 'CountyName', 'SizeRank'] + recent_dates
    ca_recent = ca_housing[cols_to_keep]
    
    ca_long = pd.melt(ca_recent, 
                      id_vars=['RegionName', 'CountyName', 'SizeRank'], 
                      value_vars=recent_dates, 
                      var_name='Date', 
                      value_name='HomeValue')
    
    ca_long['Date'] = pd.to_datetime(ca_long['Date'])
    ca_long = ca_long.sort_values(['RegionName', 'Date']).reset_index(drop=True)
    
    # Extract Los Banos
    los_banos_raw = ca_recent[ca_recent['RegionName'] == 'Los Banos'].copy()
    date_cols = [col for col in los_banos_raw.columns if col.startswith(('19', '20'))]
    
    lb_long = pd.melt(los_banos_raw, 
                      id_vars=['RegionName', 'CountyName'], 
                      value_vars=date_cols, 
                      var_name='Date', 
                      value_name='HomeValue')
    
    lb_long['Date'] = pd.to_datetime(lb_long['Date'])
    lb_long = lb_long.sort_values('Date').reset_index(drop=True)
    
    # Calculate momentum metrics
    lb_long['PctChange'] = lb_long['HomeValue'].pct_change() * 100
    lb_long['Month'] = lb_long['Date'].dt.month
    lb_long['Year'] = lb_long['Date'].dt.year
    
    return ca_long, lb_long

# Load data
ca_long, lb_long = load_data()

# Calculate statewide baseline
ca_trend = ca_long.groupby('Date')['HomeValue'].mean().reset_index()

# Calculate key metrics
lb_peak = lb_long['HomeValue'].max()
lb_peak_date = lb_long[lb_long['HomeValue'] == lb_peak]['Date'].values[0]
lb_current = lb_long['HomeValue'].iloc[-1]
lb_decline = ((lb_current - lb_peak) / lb_peak) * 100

ca_peak = ca_trend['HomeValue'].max()
ca_peak_date = ca_trend[ca_trend['HomeValue'] == ca_peak]['Date'].values[0]
ca_current = ca_trend['HomeValue'].iloc[-1]
ca_decline = ((ca_current - ca_peak) / ca_peak) * 100

lb_start = lb_long['HomeValue'].iloc[0]
lb_total_appreciation = ((lb_current - lb_start) / lb_start) * 100

# SIDEBAR NAVIGATION
st.sidebar.markdown("# Navigation")
page = st.sidebar.radio(
    "Select Analysis Section:",
    ["📊 Overview", "📈 Statewide Baseline", "🏘️ Los Banos Case Study", 
     "📉 Market Momentum", "📅 Seasonality", "🚨 Spring Surge Analysis", "💡 Conclusions"]
)

# ============================================================================
# PAGE: OVERVIEW
# ============================================================================
if page == "📊 Overview":
    st.markdown('<div class="header-section"><h1>🏠 California Housing Market Analysis (2021–2026)</h1></div>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    ## Project Overview
    
    This analysis investigates California's housing market during a period of dramatic volatility:
    - **Post-COVID surge** (2021–mid-2022)
    - **Federal Reserve rate hikes** (mid-2022–2023)
    - **Market correction and stabilization** (2024–2026)
    
    ### Focus: Los Banos, CA
    
    Los Banos represents a critical but often-overlooked segment of California's housing market. 
    As a mid-Central Valley city with ~49,000 residents, it functions as an **affordability pressure valve** 
    for Silicon Valley workers priced out of Bay Area markets.
    
    **Key Questions:**
    1. How have California home values trended from 2021 to 2026?
    2. How does Los Banos diverge from the California average?
    3. Is the current market experiencing a controlled reset or structural decline?
    """)
    
    # Key metrics in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Los Banos Current Value",
            value=f"${lb_current:,.0f}",
            delta=f"{lb_total_appreciation:+.1f}% (since Jan 2021)"
        )
    
    with col2:
        st.metric(
            label="California Current Value",
            value=f"${ca_current:,.0f}",
            delta=f"{((ca_current - ca_peak) / ca_peak) * 100:+.1f}% (from peak)"
        )
    
    with col3:
        st.metric(
            label="Divergence",
            value=f"{abs(lb_decline - ca_decline):.2f}pp",
            delta="LB declining FASTER"
        )
    
    st.info("""
    💡 **Key Insight**: Los Banos has declined **4.14 percentage points MORE** than the state average,
    suggesting structural vulnerability in satellite commuter markets during rate hikes and employment uncertainty.
    """)

# ============================================================================
# PAGE: STATEWIDE BASELINE
# ============================================================================
elif page == "📈 Statewide Baseline":
    st.markdown('<div class="header-section"><h1>📈 California Statewide Trends (2021–2026)</h1></div>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    Before analyzing Los Banos, we establish a baseline for the entire California market. 
    This trend reveals the **statewide economic forces** that shape local markets.
    """)
    
    # Plot
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(ca_trend['Date'], ca_trend['HomeValue'], color='#1f77b4', linewidth=3, label='CA Average')
    ax.axvline(pd.Timestamp(ca_peak_date), color='red', linestyle='--', alpha=0.5, 
               label=f'Peak: {pd.Timestamp(ca_peak_date).strftime("%b %Y")}')
    
    ax.set_title('California Average Home Value Trend (2021 - 2026)', fontsize=16, fontweight='bold')
    ax.set_ylabel('Average Home Value ($)', fontsize=12)
    ax.set_xlabel('Year', fontsize=12)
    ax.grid(True, alpha=0.2)
    ax.legend(fontsize=11)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e6:.1f}M'))
    
    st.pyplot(fig)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Peak Value", f"${ca_peak:,.0f}")
    
    with col2:
        st.metric("Peak Date", pd.Timestamp(ca_peak_date).strftime("%b %Y"))
    
    with col3:
        st.metric("Current Value", f"${ca_current:,.0f}")
    
    with col4:
        st.metric("Decline from Peak", f"{ca_decline:.2f}%")
    
    st.markdown("""
    ### Interpretation
    
    - **2021–Mid-2022**: Sharp price appreciation (+23.5%) driven by pandemic-era demand and low rates
    - **Mid-2022–Mid-2023**: Steep decline (-7.1%) following Fed rate hikes to combat inflation
    - **Mid-2023–2026**: Volatile stabilization—prices recovered partially but remain well below peak
    - **Current Status**: Down 2.3% from peak, suggesting **controlled correction rather than freefall**
    """)

# ============================================================================
# PAGE: LOS BANOS CASE STUDY
# ============================================================================
elif page == "🏘️ Los Banos Case Study":
    st.markdown('<div class="header-section"><h1>🏘️ Los Banos, CA: The Bay Area Pressure Valve</h1></div>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    ### Why Los Banos?
    
    Los Banos is a critical test case for understanding how **structural economic forces** ripple through 
    peripheral housing markets.
    
    **Characteristics:**
    - **Location**: 90 miles from Silicon Valley via Pacheco Pass (Highway 152)
    - **Population**: ~49,000 (36% growth since 2010)
    - **Role**: Affordability market for tech workers priced out of Bay Area
    - **Sensitivity**: High share of first-time buyers (rate-vulnerable) and tech-employment-dependent
    """)
    
    # Comparison visualization
    fig, ax = plt.subplots(figsize=(14, 8))
    
    ax.plot(ca_trend['Date'], ca_trend['HomeValue'], label='California Average', 
            color='gray', linestyle='--', linewidth=2.5, alpha=0.7)
    ax.plot(lb_long['Date'], lb_long['HomeValue'], label='Los Banos', 
            color='#d62728', linewidth=3)
    
    ax.set_title('Housing Market Divergence: Los Banos vs. California Average (2021–2026)', 
                 fontsize=16, fontweight='bold')
    ax.set_ylabel('Home Value ($)', fontsize=12)
    ax.set_xlabel('Year', fontsize=12)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.2)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e3:.0f}K'))
    
    st.pyplot(fig)
    
    # Comparative metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Los Banos")
        st.metric("Peak", f"${lb_peak:,.0f}")
        st.metric("Peak Date", pd.Timestamp(lb_peak_date).strftime("%b %Y"))
        st.metric("Current", f"${lb_current:,.0f}")
        st.metric("Decline from Peak", f"{lb_decline:.2f}%")
    
    with col2:
        st.subheader("California Average")
        st.metric("Peak", f"${ca_peak:,.0f}")
        st.metric("Peak Date", pd.Timestamp(ca_peak_date).strftime("%b %Y"))
        st.metric("Current", f"${ca_current:,.0f}")
        st.metric("Decline from Peak", f"{ca_decline:.2f}%")
    
    st.warning(f"""
    🚨 **Critical Insight**: Los Banos has declined **{abs(lb_decline - ca_decline):.2f} percentage points MORE** 
    than the California average. This **2.8x steeper decline** suggests structural vulnerability in satellite 
    commuter markets during economic uncertainty.
    """)

# ============================================================================
# PAGE: MARKET MOMENTUM
# ============================================================================
elif page == "📉 Market Momentum":
    st.markdown('<div class="header-section"><h1>📉 Market Momentum: Reset vs. Crash?</h1></div>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    ### Measuring Velocity
    
    Month-to-month percentage change reveals whether the market is **stabilizing** (controlled reset) 
    or **accelerating downward** (crash). Consistent, mild negative momentum suggests equilibrium at a new price floor.
    """)
    
    # Last 12 months momentum
    cutoff_date = lb_long['Date'].max() - pd.DateOffset(months=12)
    last_12_months = lb_long[lb_long['Date'] >= cutoff_date].copy()
    
    avg_monthly_change = last_12_months['PctChange'].mean()
    median_monthly_change = last_12_months['PctChange'].median()
    momentum_volatility = last_12_months['PctChange'].std()
    
    # Momentum visualization
    fig, ax = plt.subplots(figsize=(14, 6))
    
    colors = ['#e74c3c' if x < 0 else '#2ecc71' for x in last_12_months['PctChange'].values]
    ax.bar(last_12_months['Date'], last_12_months['PctChange'], color=colors, alpha=0.8)
    ax.axhline(0, color='black', linewidth=0.8)
    ax.axhline(avg_monthly_change, color='blue', linestyle='--', linewidth=2, 
               label=f'Avg: {avg_monthly_change:+.3f}%')
    
    ax.set_title('Los Banos: Monthly Price Momentum (Last 12 Months)', fontsize=14, fontweight='bold')
    ax.set_ylabel('% Monthly Change', fontsize=11)
    ax.set_xlabel('Date', fontsize=11)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    st.pyplot(fig)
    
    # Momentum stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Average Monthly Change", f"{avg_monthly_change:+.3f}%")
    
    with col2:
        st.metric("Median Monthly Change", f"{median_monthly_change:+.3f}%")
    
    with col3:
        st.metric("Min Month", f"{last_12_months['PctChange'].min():+.3f}%")
    
    with col4:
        st.metric("Volatility (Std Dev)", f"{momentum_volatility:.3f}%")
    
    # Interpretation
    if avg_monthly_change < -0.1:
        status = "⚠️ **Consistent Downward Pressure**"
        interpretation = f"Averaging {abs(avg_monthly_change):.2f}% decline per month. Market is not stabilizing."
    elif abs(avg_monthly_change) < 0.1:
        status = "✓ **Market Stabilizing**"
        interpretation = "Essentially flat trading—classic reset pattern."
    else:
        status = "✓ **Market Recovering**"
        interpretation = f"Averaging {avg_monthly_change:+.2f}% growth per month."
    
    st.info(f"""
    {status}
    
    {interpretation} The consistent downward pressure combined with stable volatility suggests 
    we're in a **controlled reset phase**—not a crash, but a deliberate repricing to a new equilibrium.
    """)

# ============================================================================
# PAGE: SEASONALITY
# ============================================================================
elif page == "📅 Seasonality":
    st.markdown('<div class="header-section"><h1>📅 Seasonal Patterns: The Spring Surge</h1></div>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    ### Housing Market Seasons
    
    Family-oriented markets like Los Banos typically show strong seasonal patterns:
    - **Spring (Mar–May)**: Surge in demand, families move during school calendar
    - **Summer (Jun–Aug)**: Peak season, but supply increases
    - **Fall (Sep–Nov)**: Transition period
    - **Winter (Dec–Feb)**: Slowdown phase
    
    The question: **Is 2026 following historical patterns, or have structural forces overridden seasonality?**
    """)
    
    # Calculate seasonality
    monthly_seasonality = lb_long.groupby('Month')['PctChange'].mean()
    
    # Dual plot
    col1, col2 = st.columns(2)
    
    with col1:
        fig, ax = plt.subplots(figsize=(8, 6))
        colors = ['#2ecc71' if x > 0 else '#e74c3c' for x in monthly_seasonality.values]
        ax.bar(monthly_seasonality.index, monthly_seasonality.values, color=colors, alpha=0.8)
        ax.axhline(0, color='black', linewidth=0.8)
        ax.set_title('Historical Seasonal Pattern\n(Avg % Change by Month)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Average % Monthly Change', fontsize=10)
        ax.set_xlabel('Month', fontsize=10)
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'])
        ax.grid(axis='y', alpha=0.3)
        st.pyplot(fig)
    
    with col2:
        fig, ax = plt.subplots(figsize=(8, 6))
        for year in sorted(lb_long['Year'].unique()):
            year_data = lb_long[lb_long['Year'] == year].groupby('Month')['PctChange'].mean()
            ax.plot(year_data.index, year_data.values, marker='o', label=str(year), linewidth=2)
        ax.axhline(0, color='black', linewidth=0.8)
        ax.set_title('Monthly Pattern by Year\n(Are patterns breaking down?)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Average % Monthly Change', fontsize=10)
        ax.set_xlabel('Month', fontsize=10)
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'])
        ax.legend(fontsize=9)
        ax.grid(alpha=0.3)
        st.pyplot(fig)
    
    # Seasonal metrics
    spring_months = [3, 4, 5]
    spring_avg = lb_long[lb_long['Month'].isin(spring_months)]['PctChange'].mean()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Spring Avg (Mar-May)", f"{spring_avg:+.3f}%")
    
    with col2:
        st.metric("Historical Overall Avg", f"{monthly_seasonality.mean():+.3f}%")
    
    with col3:
        st.metric("Spring Relative Strength", 
                 "Above avg" if spring_avg > monthly_seasonality.mean() else "Below avg")

# ============================================================================
# PAGE: SPRING SURGE ANALYSIS
# ============================================================================
elif page == "🚨 Spring Surge Analysis":
    st.markdown('<div class="header-section"><h1>🚨 The 2026 Spring Surge Failure</h1></div>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    ### The Paradox
    
    **Historical Pattern**: Spring months (especially April) show **+0.75% to +0.78%** average growth in Los Banos.
    
    **2026 Reality**: The market has NOT followed this pattern. We compare what *should* have happened 
    against what *actually* happened.
    
    **Why It Matters**: If historical seasonal patterns have collapsed, structural forces 
    (interest rates, employment, buyer confidence) now override seasonal demand factors.
    """)
    
    # Build comparison
    historical_data = lb_long[lb_long['Year'] < 2025].copy()
    historical_avg_by_month = historical_data.groupby('Month')['PctChange'].mean()
    current_2026 = lb_long[lb_long['Year'] == 2026].copy()
    
    # Divergence plot
    fig, ax = plt.subplots(figsize=(14, 7))
    
    x_months = sorted(historical_avg_by_month.index)
    ax.plot(x_months, historical_avg_by_month.values, 
            marker='o', linewidth=3, markersize=8, color='gray', 
            linestyle='--', label='Historical Average (Expected)', alpha=0.7)
    
    if len(current_2026) > 0:
        months_2026 = sorted(current_2026['Month'].unique())
        values_2026 = [current_2026[current_2026['Month'] == m]['PctChange'].values[0] 
                       for m in months_2026]
        ax.plot(months_2026, values_2026, 
                marker='s', linewidth=3, markersize=8, color='#e74c3c', 
                label='Actual 2026 (Reality)', zorder=5)
    
    ax.axhline(0, color='black', linewidth=0.8)
    ax.set_title('The Spring Surge Failure: Expected vs. Actual 2026', fontsize=16, fontweight='bold')
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('% Monthly Change', fontsize=12)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    ax.legend(fontsize=11)
    ax.grid(alpha=0.3)
    
    st.pyplot(fig)
    
    # Divergence breakdown
    st.subheader("Month-by-Month Analysis")
    
    divergence_data = []
    for month in [1, 2, 3]:
        historical_val = historical_avg_by_month.get(month, 0)
        actual_2026 = current_2026[current_2026['Month'] == month]['PctChange'].values
        
        if len(actual_2026) > 0:
            actual_val = actual_2026[0]
            divergence = actual_val - historical_val
            month_name = ['January', 'February', 'March'][month-1]
            
            divergence_data.append({
                'Month': month_name,
                'Expected': f"{historical_val:+.3f}%",
                'Actual': f"{actual_val:+.3f}%",
                'Divergence': f"{divergence:+.3f}pp"
            })
    
    divergence_df = pd.DataFrame(divergence_data)
    st.table(divergence_df)
    
    st.error("""
    🚨 **The Pattern Has Broken**
    
    March 2026 should have shown +0.91% growth (historical average). Instead, it showed -0.13%.
    
    This **1.04 percentage point divergence** signals that structural economic forces now override 
    seasonal demand factors. The "commuter ceiling" is real—there's a limit to how far out workers 
    will live for affordability when rates spike and employment becomes uncertain.
    """)

# ============================================================================
# PAGE: CONCLUSIONS
# ============================================================================
elif page == "💡 Conclusions":
    st.markdown('<div class="header-section"><h1>💡 Key Findings & Implications</h1></div>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    ### Summary of Findings
    """)
    
    # Summary table
    summary_data = {
        'Dimension': [
            'Statewide Trend',
            'Los Banos Performance',
            'Market Momentum',
            'Seasonal Patterns',
            'Spring Surge (2026)'
        ],
        'Finding': [
            '-2.30% decline from peak',
            '-6.44% decline from peak',
            '-0.27% avg/month (last 12mo)',
            'Historical patterns held until 2026',
            '-1.04pp below historical average'
        ],
        'Implication': [
            'Controlled market correction',
            '2.8x steeper than state avg',
            'Consistent downward pressure',
            'Structural patterns persistent',
            'Historic patterns have collapsed'
        ]
    }
    
    summary_df = pd.DataFrame(summary_data)
    st.table(summary_df)
    
    st.markdown("""
    ### Direct Answers to Research Questions
    
    **Q1: How have California home values trended from 2021 to 2026?**
    
    Sharp rise (2021–mid-2022), sharp decline (mid-2022–mid-2023), volatile stabilization (2023–2026). 
    Currently down 2.3% from peak, trending sideways rather than recovering. The market has found a new equilibrium.
    
    ---
    
    **Q2: How does Los Banos diverge from the California average?**
    
    Los Banos declines **2.8x faster** than the state average. This 4.14 percentage point excess decline 
    points to structural factors beyond simple supply/demand: tech employment volatility, buyer rate sensitivity, 
    and exhaustion of the affordability arbitrage premium.
    
    ---
    
    **Q3: Is the current Los Banos market experiencing a controlled reset or structural decline?**
    
    **A controlled reset that will likely face further downward pressure.** The -0.27% monthly momentum 
    is stable (reset, not crash), but the consistent pressure and failure of seasonal patterns suggest 
    we've not yet reached equilibrium. Expect prices to stabilize 5–10% below peak values.
    
    ---
    
    ### The Sociological Interpretation
    
    Housing markets are **not efficient**. Los Banos does not simply reflect local supply/demand—it reflects:
    - Bay Area employment volatility
    - Federal Reserve policy
    - Remote work culture shifts
    - First-time buyer credit access
    - Tech sector health
    
    The city acts as a **transducer**, amplifying macro forces into local price action.
    
    The "commuter ceiling" is real: there is a limit to how far out workers will live for affordability 
    when rates spike and employment becomes unstable. Los Banos is discovering that limit in real-time.
    
    ---
    
    ### Future Work
    
    - **Forecasting**: Build SARIMA model to project 2026–2027 prices
    - **Cohort Analysis**: Segment transactions by price point
    - **Employment Correlation**: Cross-reference Bay Area tech jobs with prices
    - **Rent-to-Own**: Compare housing prices to rental costs
    """)
    
    # About section
    st.markdown("""
    ---
    
    ### About This Analysis
    
    **Data Source**: Zillow Home Value Index (ZHVI) — City Level  
    **Period**: January 2021 – March 2026  
    **Geography**: California, 960 cities  
    **Focus**: Los Banos, CA (Merced County)  
    **Tools**: Python, pandas, matplotlib, seaborn, statsmodels  
    
    **Author**: Jorge Reyes-Ornelas  
    Data Analyst | Wine Operations Specialist | MS Data Analytics Candidate
    
    Bridging industrial operations, sociological insights, and technical rigor.
    """)

# FOOTER
st.markdown("""
---
*Interactive Analysis • Data-Driven Insights • Structural Perspective*
""")
