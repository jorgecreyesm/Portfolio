# Wine Distribution Analysis

**Tools:** Python · pandas · statsmodels · matplotlib · numpy · DuckDB · SQL  
**Data Source:** Warehouse and Retail Sales Dataset (Maryland Alcohol Control)

---

## Overview

This folder contains two related projects that together tell a story of analytical growth. Both projects use the same core dataset — warehouse and retail alcohol sales data — but represent different stages of methodology, complexity, and thinking.

The progression from the first project to the second reflects a key principle in data science: **the first model is never the final model.**

---

## Project 1 — Alcohol Sales Forecasting (Starting Point)

**File:** `Alcohol_sales.ipynb`

The first attempt at building a wine volume forecast using SARIMA. This project establishes the foundation — loading the dataset, filtering to wine only, building a monthly time series, and generating a basic 12-month projection.

What this project does well:
- Clean data pipeline from raw CSV to time series
- Correct application of SARIMA with seasonal order
- Clear visualization of historical trend and forecast

What this project does not yet address:
- A 16-month dead air gap in 2017–2018 that distorts the model
- COVID-19 demand spikes in 2020 that inflate the seasonal baseline
- No outlier handling or data intervention strategy

This notebook is preserved intentionally as a honest record of where the analysis began.

---

## Project 2 — Wine Volume Forecasting in a Volatile Market (Refined Approach)

**File:** `wine_forecasting.ipynb`

The second project revisits the same forecasting problem with a more critical eye. After identifying that raw data contained structural problems that would corrupt any model trained on it, this project introduces a deliberate **data intervention strategy** before modeling.

Key improvements over Project 1:

**Problem 1 — Dead Air Gap (2017–2018)**
A 16-month stretch of near-zero values created a flat interpolated line that destabilized the seasonal model. Solution: series truncated to begin from June 2019, focusing the model on reliable data only.

**Problem 2 — COVID-19 Demand Spikes (2020)**
Pandemic-driven purchasing created abnormal volume spikes that do not reflect the wine industry's true seasonal rhythm. Solution: **Winsorization** — capping values at the 95th percentile to neutralize outliers while preserving the overall trend shape.

The refined model produces a 12-month projection with a 95% confidence interval, maintaining a realistic seasonal trajectory that accurately reflects holiday demand surges in Q4.

---

## The Core Lesson

The jump from Project 1 to Project 2 is not about using a more complex model — both use SARIMA. The difference is **knowing when the data is lying to you** and having the tools to correct it before modeling.

Data cleaning and critical context are more valuable than model sophistication alone.

---

## How to Run

1. Clone the repository
2. Place `Warehouse_and_Retail_Sales.csv` in the project directory
3. Open either notebook in Jupyter and run all cells top to bottom

**Required packages:** `pandas`, `numpy`, `statsmodels`, `matplotlib`  
**Install:** `pip install pandas numpy statsmodels matplotlib`
