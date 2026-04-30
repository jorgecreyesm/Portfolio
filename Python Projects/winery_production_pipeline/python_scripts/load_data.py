import os
import pandas as pd
import psycopg2
from psycopg2 import extras
from dotenv import load_dotenv

# 1. Force load and check
load_dotenv()

db_name = os.getenv("DB_NAME")
if db_name is None:
    print("❌ ERROR: .env file not found or DB_NAME is empty!")
    print(f"Current Working Directory: {os.getcwd()}")
else:
    print(f"✅ Success! Connected to environment for database: {db_name}")

def load_to_postgres():
    # 1. Connect to Postgres
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    cur = conn.cursor()
    print("Connected to PostgreSQL...")

    # 2. Load the Master CSV
    df = pd.read_csv('master_wine_data.csv')
    print(f"Loading {len(df)} rows from CSV...")

    try:
        # --- STEP A: POPULATE SUPPLIERS ---
        unique_suppliers = df[['SUPPLIER']].drop_duplicates()
        supplier_data = [tuple(x) for x in unique_suppliers.values]
        extras.execute_values(cur, "INSERT INTO suppliers (supplier_name) VALUES %s ON CONFLICT (supplier_name) DO NOTHING", supplier_data)
        print("Suppliers loaded.")

        # --- STEP B: POPULATE ITEM TYPES ---
        unique_types = df[['ITEM TYPE']].drop_duplicates()
        type_data = [tuple(x) for x in unique_types.values]
        extras.execute_values(cur, "INSERT INTO item_types (type_name) VALUES %s ON CONFLICT (type_name) DO NOTHING", type_data)
        print("Item Types loaded.")

        # --- STEP C: POPULATE ITEMS ---
        # Get IDs from DB to map them
        cur.execute("SELECT supplier_id, supplier_name FROM suppliers")
        sup_map = {name: id for id, name in cur.fetchall()}
        
        cur.execute("SELECT type_id, type_name FROM item_types")
        type_map = {name: id for id, name in cur.fetchall()}

        # Prepare Item Data
        unique_items = df[['ITEM CODE', 'ITEM DESCRIPTION', 'ITEM TYPE', 'SUPPLIER']].drop_duplicates(subset=['ITEM CODE'])
        item_rows = []
        for _, row in unique_items.iterrows():
            item_rows.append((
                row['ITEM CODE'], 
                row['ITEM DESCRIPTION'], 
                type_map.get(row['ITEM TYPE']), 
                sup_map.get(row['SUPPLIER'])
            ))
        
        extras.execute_values(cur, "INSERT INTO items (item_code, item_description, type_id, supplier_id) VALUES %s ON CONFLICT DO NOTHING", item_rows)
        print("Items loaded.")

        # --- STEP D: POPULATE MONTHLY SALES (The big one!) ---
        sales_data = []
        for _, row in df.iterrows():
            sales_data.append((
                row['ITEM CODE'], 
                row['YEAR'], 
                row['MONTH'], 
                row['RETAIL SALES'], 
                row['RETAIL TRANSFERS'], 
                row['WAREHOUSE SALES']
            ))

        # We use a smaller page size for the 400k rows to avoid memory issues
        print("Starting bulk load of sales data (this may take a minute)...")
        extras.execute_values(cur, 
            "INSERT INTO monthly_sales (item_code, year, month, retail_sales, retail_transfers, warehouse_sales) VALUES %s", 
            sales_data, page_size=1000)
        
        conn.commit()
        print("SUCCESS: All data migrated to PostgreSQL.")

    except Exception as e:
        print(f"ERROR: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    load_to_postgres()