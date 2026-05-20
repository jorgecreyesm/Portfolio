# Merced County Housing Market Dashboard

An Excel dashboard analyzing residential housing trends across 5 cities in Merced County, California — built from Redfin transaction data.

---

## Overview

This project pulls Redfin housing market data, cleans and reshapes it using Python, and loads the results into an Excel workbook with pivot tables and a one-page executive dashboard.

**Cities covered:** Merced, Los Banos, Atwater, Livingston, Hilmar  
**Coverage:** January 2023 – April 2026  

---

## Data Source

| Source | Dataset | What It Covers |
|---|---|---|
| Redfin | `redfin_housing_market_monthly_all_cities_key_metrics_2023_Jan_to_2026_Apr.csv` | Rolling 3-month transaction metrics by city |

---

## Cleaned Dataset

The raw Redfin file was filtered to the 5 Merced County cities, reshaped to long format, and exported to CSV using Python (`pandas`) before import into Excel.

**`redfin_active_clean.csv`** — 190 rows, long format

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

- All five cities were in a correction phase entering 2023 following the 2022 rate hikes
- **Los Banos** had the highest median sale prices and the steepest volume declines, reflecting Bay Area commuter demand sensitivity
- **Atwater** showed the fastest stabilization across the period
- **Hilmar and Livingston** are driven more by local agricultural employment than Bay Area spillover, resulting in different inventory patterns
- As of early 2026, market activity across all five cities is trending toward stabilization

---

## Requirements

- Microsoft Excel (2019+ or Microsoft 365)
- Python 3.x + `pandas` for data prep (optional — cleaned CSV is included)
