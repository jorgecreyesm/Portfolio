# 🏠 California Housing Market Analysis

## 📁 Project Structure

This folder contains both the **interactive Streamlit app** and the **original research notebook**:

### 🌐 Interactive App (Primary)
- **`app.py`** - Production Streamlit application with 7 interactive pages
- **`requirements.txt`** - Python dependencies
- **`.streamlit/config.toml`** - App styling and configuration
- **`STREAMLIT_README.md`** - App usage guide
- **`city_homevalue_zillow.csv`** - Zillow housing dataset (87.8 MB)

### 📊 Original Research Files (Reference)
- **`Local_housing_market.ipynb`** - Original Jupyter notebook
  - Contains exploratory data analysis and methodology
  - Documents the research process, findings, and conclusions
  - Includes markdown explanations of analytical decisions
  - Shows full 5-year trend analysis (2021-2026)
  - Useful for understanding the housing market insights
- **`Merced_County_Housing.ipynb`** - Part 2: Merced County deep dive (through Mar 2026)
  - City-by-city comparison: Merced, Los Banos, Atwater, Livingston, Hilmar
  - Includes decline-from-peak analysis, indexed appreciation, and 6-month momentum
- **`Merced_County_Housing_Summer2026.ipynb`** - Part 2 Summer 2026 update (through May 2026)
  - Same layout and cities as the original Merced County notebook
  - Refreshed with updated Zillow ZHVI dataset extending to May 2026
  - Source: `City_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv` (not committed — see Data Sources)

## 🚀 Running the App

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 📖 Why Both Files Exist

1. **Transparency** - Shows the research-to-production pipeline
2. **Documentation** - Notebook serves as extended methodology reference
3. **Reproducibility** - Original analysis can be re-run and verified
4. **Portfolio Value** - Demonstrates full analytics workflow (notebook → interactive app → cloud deployment)
5. **Learning** - Shows how to convert static analysis into interactive experiences

## ☁️ Live Deployment

The app is deployed on **Streamlit Cloud** and accessible publicly.

Get the URL from your Streamlit Cloud dashboard at https://share.streamlit.io

## 📊 Data Sources

| File | Used by | Raw coverage | In repo |
|------|---------|--------------|---------|
| `city_homevalue_zillow.csv` | `app.py`, `Local_housing_market.ipynb`, `Merced_County_Housing.ipynb` | Jan 2000 – Mar 2026 (315 months) | Yes (Git LFS, 88 MB) |
| `City_rental_data_zillow.csv` | `Local_rental_market.ipynb` | Jan 2015 – Mar 2026 (135 months) | Yes (Git LFS, 4.5 MB) |
| `City_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv` | `Merced_County_Housing_Summer2026.ipynb` | Jan 2000 – May 2026 (325 months) | No — 88 MB, download below |

Raw coverage is what each file contains; the analyses slice a narrower window at run time.
Parts 1 and 2 report Jan 2021 – Mar 2026 (63 months); the Summer 2026 notebook reports
Jan 2021 – May 2026 (65 months) for the 5 Merced County cities. No intermediate file is written.

The Summer 2026 raw dump is gitignored to stay within the Git LFS quota. To re-run
`Merced_County_Housing_Summer2026.ipynb`, download the ZHVI file and place it in this folder:

<https://www.zillow.com/research/data/> → *Home Values* → ZHVI All Homes (SFR/Condo), Smoothed & Seasonally Adjusted, **City** geography.

- **Index**: Zillow Home Value Index (ZHVI) — SFR/Condo, middle tier (33rd–67th percentile)
- **Geography**: California cities; Merced County deep dive (5 cities)
- **Focus**: Los Banos commuter market (Part 1) + Merced County city comparison (Part 2)
