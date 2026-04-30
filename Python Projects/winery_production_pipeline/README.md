# 🍷 Winery Distribution & Production Analytics
### *End-to-End ETL, Data Synthesis, and PostgreSQL Scaling*

## 📖 Project Overview
This project demonstrates the transition from fragmented, flat-file data to a high-performance relational database system. Starting with a 300k-row dataset of wine sales with significant temporal gaps, I developed a Python pipeline to synthesize realistic operational data up to 2026, scaling the final dataset to **435,000+ records**. 

The goal was to build a production-ready environment to stress-test complex SQL analytics and demonstrate database optimization techniques.

## 🛠️ Technical Stack
* **Language:** Python 3.x
* **Libraries:** Pandas (Data Cleaning), Psycopg2 (Database Driver), Faker (Data Synthesis), Dotenv (Security)
* **Database:** PostgreSQL (Relational Modeling, Indexing, Window Functions)
* **Environment:** VS Code, Virtual Environments (venv)

## 🏗️ Database Architecture & Normalization
To reduce redundancy and improve data integrity, I transformed the original flat CSV into a **normalized Star Schema**:

* **suppliers**: Unique registry of industry partners.
* **item_types**: Categorical classification (WINE, LIQUOR, etc.).
* **items**: Product master data linking suppliers to specific item codes.
* **monthly_sales**: Transactional fact table storing 10 years of sales and logistics data.

## 🚀 Key Features
### 1. Programmatic Data Synthesis
* Developed a custom Python generator to "fill the gaps" in historical data (2021–2026).
* Used **Faker** and random variance logic to ensure synthetic records mimicked real-world industry trends and seasonal volatility.

### 2. High-Performance ETL Pipeline
* Built a modular ETL script in Python to handle bulk inserts of 435k+ rows.
* Utilized `psycopg2.extras.execute_values` for optimized memory management and faster migration.

### 3. Advanced SQL Analytics
* **Window Functions:** Implemented 3-month rolling averages to smooth out seasonal sales spikes.
* **Pareto Analysis (80/20 Rule):** Used CTEs and cumulative percentages to identify the top 20% of suppliers driving 80% of total revenue.
* **Performance Tuning:** Implemented B-Tree indexing on Foreign Keys, achieving a query execution time of **0.202 ms**.

## 📂 Project Structure
\`\`\`text
├── data/               # Source CSV and generated Master files
├── python_scripts/     # app.py (Cleaning/Synthesis) and load_data.py (ETL)
├── sql_scripts/        # schema.sql (DDL) and analysis_queries.sql (DML)
├── .env.example        # Template for database credentials
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
\`\`\`

## ⚙️ Installation & Setup
1. **Clone the Repo:**
   \`\`\`bash
   git clone [your-repo-link]
   \`\`\`
2. **Install Dependencies:**
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`
3. **Configure Environment:**
   * Rename \`.env.example\` to \`.env\`.
   * Update with your local PostgreSQL credentials.
4. **Initialize Database:**
   * Run \`psql -U postgres -d winery_db -f sql_scripts/schema.sql\`.
5. **Run ETL Pipeline:**
   \`\`\`bash
   python python_scripts/load_data.py
   \`\`\`
