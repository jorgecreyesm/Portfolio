# Data Science vs. Business Analyst: The Social Architecture of Tech Compensation

**Tools:** R · tidyverse · ggplot2 · lubridate  
**Data Sources:** Levels.fyi (~62,000 salary entries) · Zillow Home Value Index (ZHVI) · Zillow Observed Rent Index (ZORI)

---

## Overview

The tech industry often presents itself as a meritocracy — a field where skill alone determines economic outcome. This project challenges that assumption.

Using nearly 62,000 compensation entries from Levels.fyi, merged with Zillow's longitudinal housing and rental data, this analysis applies **Stratification Theory** to quantify how education, experience, geography, and institutional placement shape earnings for Data Scientists and Business Analysts across the United States.

---

## Key Questions

- Does a Master's or Doctorate degree yield the same compensation return for a Business Analyst as it does for a Data Scientist?
- Does the pay gap between roles widen, shrink, or remain parallel over a 20-year career?
- How much of a compensation premium does California impose — and is it offset by housing costs?
- Are tech salaries high enough to act as a structural shield against regional rent burden?

---

## Data Engineering

Three datasets were cleaned and merged into a single analytical table:

- **Salaries** — filtered to Data Scientists and Business Analysts, location parsed into state codes, education consolidated into sociological categories (Bachelors / Masters / Doctorate), and a custom **Tenure Ratio** engineered (`years at company / years of experience`)
- **Housing (ZHVI)** — pivoted from wide to long format, aggregated to annual state-level averages to match salary years
- **Rental (ZORI)** — same transformation, enabling rent burden calculations by state and role

---

## Findings

| Visualization | Sociological Concept | Finding |
|---|---|---|
| Market Valuation | Labor Stratification | Data Scientists maintain a significantly higher median and ceiling than Business Analysts across all experience levels |
| Education Premium | Credentialism | Advanced degrees raise the floor for both roles, but role selection is a stronger economic driver than degree attainment alone |
| Experience Curve | Cumulative Advantage | The compensation gap does not close over time — parallel trajectories confirm that initial role placement dictates long-term wealth accumulation |
| The Churn Factor | Institutional Attachment | High concentration of low tenure ratios reveals that pay growth is driven by job-hopping, not internal promotion |
| California Premium | Spatial Inequality | California median earners frequently out-earn the 75th percentile of the rest of the US |
| Spatial Tax | Regional Extraction | Both roles remain under the 30% rent burden threshold — high salaries act as a structural shield against housing cost pressure |
| Purchasing Power Frontier | Institutional Exclusion | For Business Analysts in coastal states, the price-to-income ratio begins crossing the traditional 4x affordability threshold |

---

## How to Run

1. Clone the repository
2. Place the following source files in the project directory:
   - `data_science_salaries.csv`
   - `housing_values_zillow.csv`
   - `rental_cost_zillow.csv`
3. Open `Data_Science_Salaries_Insights.Rmd` in RStudio
4. Knit to GitHub document or HTML

**Required packages:** `tidyverse`, `lubridate`, `ggplot2`, `scales`
