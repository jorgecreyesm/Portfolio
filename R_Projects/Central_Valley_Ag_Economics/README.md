# Central Valley Crop Economics

An interactive business analysis dashboard examining agricultural economics across
seven Central Valley counties from 2010 to 2024. Built with R, flexdashboard, and
USDA NASS public data.

## Counties
Fresno · Tulare · Kings · Merced · San Joaquin · Stanislaus · Madera

## Crops
Grapes · Almonds · Tomatoes (Processing) · Walnuts · Dairy/Milk · Cotton

## Dashboard Pages
| Page | Content |
|------|---------|
| Overview | Value of production by county and crop — latest year snapshot |
| Crop Trends | Time series of value and acreage 2010–2024 |
| Price & Yield | Price received over time + value per acre |
| County Comparison | Faceted comparison of all 7 counties per crop |
| COVID & Climate | YoY % change with COVID window + yield index (2015=100) |
| Key Findings | Written analysis — drought, commodity cycles, SGMA, COVID supply chain |

## Setup

**1. Get a free USDA NASS API key**
Register at: https://quickstats.nass.usda.gov/api

**2. Configure your key**
```bash
cp .env.example .env
# Add your key to .env: NASS_API_KEY=your_key_here
```

**3. Install R packages**
```r
install.packages(c("rnassqs", "flexdashboard", "plotly",
                   "tidyverse", "scales", "dotenv", "RColorBrewer",
                   "here", "knitr"))
```

**4. Fetch data (run once)**
```r
source("R/fetch_data.R")
```

**5. Clean data**
```r
source("R/clean_data.R")
```

**6. Knit the dashboard**
Open `CV_Ag_Economics.Rmd` in RStudio and click **Knit**, or:
```r
rmarkdown::render("CV_Ag_Economics.Rmd")
```

## Data Source
[USDA NASS Quick Stats](https://quickstats.nass.usda.gov/) — public domain, no license restrictions.

## Author
**Jorge Reyes-Ornelas** — M.S. Data Analytics (in progress), Eastern University
[GitHub](https://github.com/jorgecreyesm)
