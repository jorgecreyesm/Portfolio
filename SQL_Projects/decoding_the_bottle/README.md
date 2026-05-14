# Decoding the Bottle: A Sociological and Operational Analysis of Alcohol Distribution

**Tools:** Python · DuckDB · SQL · pandas · matplotlib · seaborn  
**Data Source:** Warehouse and Retail Sales Dataset (Maryland Alcohol Control)

---

## Overview

In the wine and spirits industry, "taste" is not purely a personal preference — it is a socially constructed phenomenon shaped by institutional supply chains, cultural capital, and consumer agency.

This project investigates the structural mismatch between **retail consumer demand ("Pull")** and **warehouse-driven distribution ("Push")** using SQL inside a Python environment. Drawing on a background in both sociology and wine operations, the analysis identifies where individual consumer choice diverges from institutional habit — and where that divergence creates measurable operational inefficiency.

---

## Key Questions

- Which products are consumers actively seeking out that the warehouse hasn't prioritized?
- Which products dominate the supply chain due to institutional habit rather than actual consumer demand?
- Where does over-transferring inventory create "Dead Stock" — shelf space occupied without generating revenue?

---

## Technical Approach

This project uses **DuckDB** to run SQL directly within a Jupyter notebook, combining the flexibility of Python with the power of relational query logic.

Key SQL techniques used:
- `CREATE VIEW` for reusable query logic across analysis sections
- **Window Functions** (`RANK() OVER`) to independently rank items by retail demand and warehouse supply
- **Aggregation with HAVING** to filter Dead Stock above a meaningful operational threshold
- Logarithmic scatter visualization to expose the Power Law distribution of alcohol sales volume

---

## Findings

**Retail Stars vs. Warehouse Workhorses**

By computing a `rank_gap` (warehouse rank minus retail rank), products fall into two sociological categories:

- **Retail Stars** (positive rank gap) — products consumers seek out that the warehouse underindexes. These often represent *Cultural Capital*: premium or niche varietals chosen to signal taste or status at the shelf level.
- **Warehouse Workhorses** (negative rank gap) — products that dominate bulk distribution not by consumer choice, but by institutional placement in hotels, banquet halls, and large-scale hospitality. These represent *Institutionalized Taste*.

**Dead Stock: The Operational Efficiency Gap**

Defined as `Transfers − Sales`, dead stock identifies inventory moved to retail that failed to reach the consumer. High dead stock volume in seasonal items (notably Egg Nog) points to a need for better predictive modeling in purchasing and operations planning.

**The Visualization**

A log-scale scatter plot maps every wine SKU by retail sales vs. warehouse sales volume. The red diagonal reference line represents a perfectly efficient market. The dense cluster in the lower-left quadrant — the Long Tail — reveals the scale of the mismatch between what institutions supply and what consumers actually choose.

---

## Why This Project Matters

Most distribution analyses stop at volume rankings. This project goes further by framing the data through **Stratification Theory** — treating the supply chain itself as a social structure where institutional power and consumer agency compete. The result is an analysis that is both operationally actionable and theoretically grounded.

---

## How to Run

1. Clone the repository
2. Place `Warehouse_and_Retail_Sales.csv` in the project directory
3. Open `Alcohol_Sociological_Analysis.ipynb` in Jupyter
4. Run all cells top to bottom

**Required packages:** `duckdb`, `pandas`, `matplotlib`, `seaborn`  
**Install:** `pip install duckdb pandas matplotlib seaborn`
