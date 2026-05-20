# Merced County Housing Market Dashboard

An Excel dashboard analyzing residential housing trends across 5 cities in Merced County, California — combining Zillow home value data with Redfin transaction metrics.

---

## Overview

This project pulls from two data sources, cleans and reshapes them using Python, and loads the results into an Excel workbook with pivot tables and a one-page executive dashboard.

**Cities covered:** Merced, Los Banos, Atwater, Livingston, Hilmar  
**Zillow coverage:** January 2021 – March 2026  
**Redfin coverage:** January 2023 – April 2026  

---

## Data Sources

| Source | Dataset | What It Covers |
|---|---|---|
| Zillow ZHVI | `city_homevalue_zillow.csv` | Monthly median home values, point-in-time |
| Redfin | `redfin_housing_market_monthly_all_cities_key_metrics_2023_Jan_to_2026_Apr.csv` | Rolling 3-month transaction metrics |

> **Note:** Zillow and Redfin use different time structures (monthly snapshots vs. rolling 3-month windows) and are kept as separate sheets rather than force-joined.

---

## Cleaned Datasets

Both sources were filtered, reshaped, and exported to CSV using Python (`pandas`) before import into Excel.

**`merced_clean.csv`** — Zillow ZHVI, long format

| Column | Description |
|---|---|
| `Date`, `Year`, `Month`, `Quarter` | Time dimensions |
| `City`, `State`, `Metro`, `CountyName` | Geography |
| `Home_Value` | Zillow median home value |
| `MoM_Change_Pct` | Month-over-month % change |
| `YoY_Change_Pct` | Year-over-year % change (12-month lag) |

**`redfin_active_clean.csv`** — Redfin rolling 3-month metrics, long format

| Column | Description |
|---|---|
| `Period_Begin`, `Period_End`, `Year`, `Month`, `Quarter` | Time dimensions |
| `City` | One of the 5 Merced County cities |
| `Homes_Sold`, `Homes_Sold_YOY_Pct` | Sales volume |
| `Median_Sale_Price`, `Median_Sale_Price_YOY_Pct` | Transaction price |
| `Median_Days_On_Market`, `Median_Days_On_Market_YOY_Pct` | Supply/demand signal |
| `New_Listings`, `Active_Listings`, `Pending_Sales` + YOY % | Inventory metrics |

---

## Workbook Structure

| Sheet | Description |
|---|---|
| `Clean_Data` | Redfin long-format data — 5 cities, 2023–2026 |
| `Pivot_Analysis` | Average active listings, homes sold, and median sale price by city and quarter |
| `Dashboard` | KPI cards + charts — Median Sale Price, Days on Market, Homes Sold, Active Listings |
| `Methodology` | Data sources, assumptions, and limitations |

---

## Key Findings

- All five cities peaked in **mid-2022** then corrected through 2023 as rates rose
- **Los Banos** saw the largest decline from peak (-6.44%) reflecting its Bay Area commuter exposure
- **Atwater** showed the fastest stabilization, recovering to within 0.29% of its peak by early 2026
- **Hilmar and Livingston** peaked later (early 2025) and are driven more by local agricultural employment than Bay Area spillover
- As of early 2026, most cities are stabilizing with modest upward momentum

---

## Requirements

- Microsoft Excel (2019+ or Microsoft 365)
- Python 3.x + `pandas` for data prep (optional — cleaned CSVs are included)
