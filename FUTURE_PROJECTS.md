# Future Portfolio Projects

## R Projects
- [ ] **Merced County Housing Time Series** — SARIMA/ETS forecast using Zillow data to project 2026–2027 home values. Extends the Python housing series with predictive modeling.
- [ ] **California Rent vs. Ownership Regression** — Regression model using both Zillow datasets showing what predicts rent levels (county, population, home values). Policy-oriented story.
- [ ] **Winery Production Quality Control** — Statistical process control (SPC) charts in R for wine production metrics. Ties directly to wine operations background.

## Python Projects
- [ ] **Hyperparameter Tuning — ML Wine Quality** — Add GridSearchCV to Random Forest and XGBoost to reduce overfitting (1.0 train accuracy). Strengthens the existing ML project.
- [ ] **Merced County Housing Streamlit App** — Convert the 3-part housing series into a single multi-page Streamlit app similar to the Local Housing Market app.
- [ ] **Rental Market Streamlit App** — Add rental analysis as a new page to the Local Housing Market app.

## SQL Projects
- [ ] **Merced County Housing SQL Analysis** — Create a schema and analysis queries for the Zillow housing data. Mirrors the winery pipeline structure.

## Visualization Projects
- [ ] **Wine Quality Tableau Dashboard** — Visualize feature importance and model results from the ML Wine Quality project in Tableau.
- [ ] **Original Tableau Project** — Independent (non-coursework) Tableau dashboard on a public dataset. Replaces DTSC600 final as the primary Tableau showcase.

## Global Agriculture Projects

### Global Crop Competition — Central Valley vs. the World
- [ ] **Global Almond & Nut Market Analysis** — Compare California almond/walnut production, price, and export share against Australia (Riverland), Spain, and Chile using FAO and USDA FAS data. Track how Australian expansion correlates with California price erosion post-2015.
- [ ] **Peru & Chile Emerging Ag Exports** — Analyze Peru's Ica Valley and Chile's export growth in grapes, blueberries, and walnuts since 2010. Frame against California's cost and water constraints. Shows how new entrants reshaped global supply.
- [ ] **China Processing Tomato Competition** — Use UN Comtrade + FAO data to show China's growing share of global tomato paste/concentrate market vs. California. Tie to price trends for California processing contracts.
- [ ] **Global Water Stress × Ag Production** — Cross-reference FAO crop production data with World Resources Institute Aqueduct water stress scores by region. Show that California, Australia Murray-Darling, and Chile all face converging water constraints — no safe haven for water-intensive crops at scale.

**Possible Datasets:**
| Dataset | Source | Access | What It Covers |
|---------|--------|--------|----------------|
| FAOSTAT | UN FAO | Free, API | Production, yield, price, trade — 180+ countries, all major crops |
| PSD Online | USDA FAS | Free, download | Global commodity supply & distribution by country (almonds, walnuts, cotton) |
| UN Comtrade | UN | Free (rate-limited) | Import/export flows by commodity and country pair |
| ABARES | Australian Govt | Free, download | Australian crop production, water use, farm economics |
| WRI Aqueduct | World Resources Institute | Free, API | Water stress scores by watershed globally |
| ODEPA | Chilean Ag Ministry | Free, download | Chilean crop production and export prices |
| World Bank Ag | World Bank | Free, `wbstats` R pkg | Agricultural land, value added, rural population |

**R Packages for this work:**
```r
install.packages(c("FAOSTAT", "wbstats", "comtradr"))
# FAOSTAT: direct API access to FAO bulk data
# wbstats: World Bank indicators
# comtradr: UN Comtrade import/export flows
```

## Portfolio Gaps — High Priority

### A/B Testing / Hypothesis Testing
- [ ] **A/B Testing Case Study** — Simulate or use real experimental data to frame a business decision (conversion rates, pricing, etc.). Frame results as recommendations, not just statistics.

### API Data Pipeline
- [ ] **Live Data Pipeline** — Pull data from a public API (Census Bureau, BLS, USDA) into PostgreSQL or a flat file. Shows real-world data engineering vs. static CSV files.

### Unsupervised Learning / Clustering
- [ ] **Market Segmentation Project** — Apply K-means or DBSCAN clustering to a consumer or housing dataset. Fills the unsupervised ML gap and broadens ML coverage beyond wine quality classification.

### Education / Workforce Data
- [ ] **Substitute Teacher Shortage Analysis** — Use CDE staff data to analyze credentialed vs. emergency-permitted staff by district. Correlate staffing gaps with FRPM rates (poverty proxy) across Central Valley districts. Hyperlocal Los Banos/Merced County angle with lived domain expertise as a substitute teacher at Los Banos USD.
- [ ] **English Learner Outcomes in the Central Valley** — Compare EL reclassification rates, graduation rates, and test scores by district using CDE data. Focus on Merced County and surrounding agricultural communities. Policy-oriented narrative using sociology background.
