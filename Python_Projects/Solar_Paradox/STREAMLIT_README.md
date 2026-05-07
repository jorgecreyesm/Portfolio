# Streamlit App: Solar Paradox — Interactive Analysis

An interactive web dashboard exploring the paradox of global solar energy adoption.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements_streamlit.txt
```

### 2. Run the App
```bash
streamlit run app_solar.py
```

Open: http://localhost:8501

---

## Features

**7 Interactive Pages:**

1. **🌍 Overview** - Project context and key questions
2. **📊 The Paradox** - Does sunlight predict solar adoption?
3. **💰 The ROI Paradox** - Best returns, but lowest adoption
4. **⏱️ The Payback Inequality** - Where solar takes longest to break even
5. **📉 The Adoption Gap** - Which regions waste the most potential
6. **⭐ The Outliers** - Countries beating structural odds
7. **🎯 Conclusions** - Key findings and implications

---

## Data

Requires: `solar_energy_worldwide.csv`
- 48 cities across 30 countries, 7 regions
- Metrics: GHI, installations, ROI, payback period, efficiency

---

## Deployment (Streamlit Cloud - Free)

1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Create new app → select this repo
4. Deploy `Python_Projects/Solar_Paradox/app_solar.py`

Public URL in 2-3 minutes!

---

## Technical Details

- **Data Aggregation:** City → country level averages
- **Features:** Efficiency Score, Adoption Gap Score
- **Regional Color-Coding:** For pattern recognition across 7 regions
- **Interactivity:** Sidebar navigation, dynamic plots, data tables

---

## Questions

See README_Solar_Paradox.md for full analysis methodology.
