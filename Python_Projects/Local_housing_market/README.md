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

## 📊 Data Source

- **Dataset**: Zillow Home Value Index (ZHVI)
- **Geography**: California (960 cities)
- **Time Period**: 2021-2026 (63 months)
- **Focus**: Los Banos commuter market case study
