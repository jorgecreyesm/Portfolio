import pandas as pd
import numpy as np
import os
import random

def clean_data(df):
    print("\n--- PHASE 3: CLEANING (FIXED) ---")
    
    # .copy() prevents the SettingWithCopyWarning
    df = df.copy()
    
    df['SUPPLIER'] = df['SUPPLIER'].fillna('Unknown')
    df = df.dropna(subset=['RETAIL SALES', 'ITEM TYPE'])
    
    # Using .loc is the professional way to modify columns
    df.loc[:, 'SUPPLIER'] = df['SUPPLIER'].str.upper().str.strip()
    df.loc[:, 'ITEM DESCRIPTION'] = df['ITEM DESCRIPTION'].str.upper().str.strip()
    df.loc[:, 'ITEM TYPE'] = df['ITEM TYPE'].str.upper().str.strip()

    df = df.drop_duplicates()
    return df

def synthesize_data(original_df):
    print("\n--- PHASE 4: SYNTHESIZING (2021-2026) ---")
    
    # 1. Create Seeds
    suppliers = original_df['SUPPLIER'].unique()
    item_types = original_df['ITEM TYPE'].unique()
    items = original_df[['ITEM CODE', 'ITEM DESCRIPTION', 'ITEM TYPE', 'SUPPLIER']].drop_duplicates()
    
    # 2. Define the Gap
    target_years = [2021, 2022, 2023, 2024, 2025, 2026]
    new_records = []
    
    print(f"Generating data for {len(target_years)} years...")
    
    # To keep the file size manageable for now, we'll generate 
    # a representative sample for each year/month
    for year in target_years:
        # If 2026, only go up to April
        max_month = 4 if year == 2026 else 12
        
        for month in range(1, max_month + 1):
            # Sample 2,000 random items from our "seeds" for each month
            sample_items = items.sample(n=2000, replace=True)
            
            for _, row in sample_items.iterrows():
                new_records.append({
                    'YEAR': year,
                    'MONTH': month,
                    'SUPPLIER': row['SUPPLIER'],
                    'ITEM CODE': row['ITEM CODE'],
                    'ITEM DESCRIPTION': row['ITEM DESCRIPTION'],
                    'ITEM TYPE': row['ITEM TYPE'],
                    'RETAIL SALES': round(random.uniform(0, 50), 2),
                    'RETAIL TRANSFERS': round(random.uniform(0, 20), 2),
                    'WAREHOUSE SALES': round(random.uniform(0, 100), 2)
                })
                
    synth_df = pd.DataFrame(new_records)
    
    # Combine original and synthetic
    final_df = pd.concat([original_df, synth_df], ignore_index=True)
    print(f"Synthesis complete. New total rows: {len(final_df)}")
    
    return final_df

if __name__ == "__main__":
    raw_df = pd.read_csv('wine_data.csv')
    cleaned_df = clean_data(raw_df)
    
    # Move to synthesis
    final_master_df = synthesize_data(cleaned_df)
    
    # Save the master file
    final_master_df.to_csv('master_wine_data.csv', index=False)
    print("\nMaster data saved to 'master_wine_data.csv'")