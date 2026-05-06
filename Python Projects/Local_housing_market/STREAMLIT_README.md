# Streamlit App: California Housing Market Analysis

An interactive web application for exploring California's housing market (2021–2026) with a focus on Los Banos, CA.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_streamlit.txt
```

### 2. Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## Features

The app includes 7 interactive analysis sections:

1. **📊 Overview** - Project context and key metrics
2. **📈 Statewide Baseline** - California-wide housing trends
3. **🏘️ Los Banos Case Study** - Deep dive into the case study city
4. **📉 Market Momentum** - Month-to-month price velocity
5. **📅 Seasonality** - Seasonal pattern analysis
6. **🚨 Spring Surge Analysis** - 2026 vs. historical patterns
7. **💡 Conclusions** - Key findings and implications

---

## Data Requirements

The app expects `city_homevalue_zillow.csv` in the same directory. This file should contain:
- Zillow Home Value Index (ZHVI) data
- One row per city
- Columns: `RegionID`, `RegionName`, `State`, `CountyName`, `SizeRank`, plus date columns (YYYY-MM-DD format)

---

## Deployment Options

### Option 1: Streamlit Cloud (Free, Recommended)

1. Push this repo to GitHub
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
3. Connect your GitHub account
4. Deploy directly from this repo
5. Share the public URL

### Option 2: Heroku

```bash
# Create Procfile
echo "web: streamlit run app.py --server.port $PORT" > Procfile

# Push to Heroku
git push heroku main
```

### Option 3: AWS/Azure/GCP

Deploy the app as a containerized service using Docker or serverless functions.

---

## Architecture

```
app.py
├── Data Loading (@st.cache_data)
├── Page 1: Overview
├── Page 2: Statewide Baseline
├── Page 3: Los Banos Case Study
├── Page 4: Market Momentum
├── Page 5: Seasonality
├── Page 6: Spring Surge Analysis
└── Page 7: Conclusions
```

---

## Key Technologies

- **Streamlit**: Interactive web framework
- **Pandas**: Data manipulation
- **Matplotlib**: Visualizations
- **Python 3.8+**: Programming language

---

## Notes

- Data is cached on first load for performance
- All visualizations are responsive and interactive
- The app requires the CSV file to be in the same directory
- Sidebar navigation allows jumping between sections

---

## Future Enhancements

- [ ] Upload CSV file directly in UI
- [ ] Time period selector
- [ ] Additional cities for comparison
- [ ] Forecasting models
- [ ] Export analysis as PDF
- [ ] Real-time data updates

---

## Contact

**Author**: Jorge Reyes-Ornelas  
Data Analyst | Wine Operations Specialist | MS Data Analytics Candidate

Questions? File an issue or contact via GitHub.
