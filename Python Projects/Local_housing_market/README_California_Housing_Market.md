# California Housing Market Analysis: A Zillow Data Exploration
An investigation into home value trends across California, with a deep dive into the Los Banos commuter market (2021 – 2026).

**Tools:** Python · pandas · seaborn · matplotlib · statsmodels  
**Data Source:** Zillow Home Value Index (ZHVI) — City Level

---

## Overview

California's housing market is one of the most discussed and least understood in the United States. This project uses Zillow's longitudinal home value dataset to move beyond statewide generalizations and examine how local market dynamics diverge from the California average.

The focal point is **Los Banos, CA** — a mid-Central Valley city that functions as a commuter hub for Silicon Valley workers priced out of the Bay Area. By placing Los Banos in the context of the broader California market, this analysis explores how geographic pressure, demographic growth, and commuter economics interact to shape home values in a city most analysts overlook.

---

## Key Questions

- How have California home values trended from 2021 to 2026 following the post-COVID surge?
- How does Los Banos diverge from the California average — and what sociological forces explain that divergence?
- Is the current Los Banos market experiencing a controlled reset or a structural decline?

---

## Analytical Structure

**I. Statewide Baseline**
The full California ZHVI dataset is filtered, reshaped from wide to long format, and aggregated into a monthly average home value trend — establishing the statewide baseline against which local markets are compared.

**II. Los Banos Case Study**
Los Banos is isolated and analyzed through three lenses:

- **The Bay Area Pressure Valve** — Silicon Valley workers seeking affordability have driven sustained demand for single-family housing in the Central Valley corridor
- **Rapid Urbanization** — Population growth from ~36,000 in 2010 to ~49,000 in 2026 has transformed the city's economic landscape faster than its infrastructure
- **The Pacheco Pass Effect** — Proximity to Highway 152 makes Los Banos uniquely tied to Bay Area employment cycles, creating price volatility that tracks tech sector health more than local economic conditions

**III. Momentum Analysis**
Month-over-month percentage change is calculated across the last 12 months to determine whether the current market trajectory represents a controlled correction or a structural breakdown.

---

## Findings

- Los Banos home values tracked significantly below the California average throughout the analysis period, consistent with its role as an affordability market
- The post-2022 cooldown hit Los Banos harder and faster than the statewide average, reflecting its sensitivity to interest rate increases and remote work policy reversals
- Monthly momentum analysis reveals a gradual deceleration rather than a sharp collapse — consistent with a market reset rather than a structural crash

---

## How to Run

1. Clone the repository
2. Place `city_homevalue_zillow.csv` in the project directory
3. Open `Local_housing_market.ipynb` in Jupyter
4. Run all cells top to bottom

**Required packages:** `pandas`, `seaborn`, `matplotlib`, `statsmodels`  
**Install:** `pip install pandas seaborn matplotlib statsmodels`
