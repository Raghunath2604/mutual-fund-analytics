import glob
import os
import pandas as pd

def inspect_datasets():
    raw_files = glob.glob("data/raw/*.csv")
    datasets = {}

    print("=" * 50)
    print("1. DATASET INSPECTION (.shape, .dtypes, .head())")
    print("=" * 50)

    for file_path in raw_files:
        filename = os.path.basename(file_path)
        df = pd.read_csv(file_path)
        datasets[filename] = df
        
        print(f"\n--- File: {filename} ---")
        print(f"Shape: {df.shape}")
        print("Data Types:\n", df.dtypes)
        print("First 2 Rows:\n", df.head(2))
        print("-" * 30)

    # Fund Master & AMFI Code Validation check
    fund_master_file = next((f for f in raw_files if 'fund_master' in f.lower()), None)
    nav_history_file = next((f for f in raw_files if 'nav_history' in f.lower()), None)

    if fund_master_file and nav_history_file:
        fm = pd.read_csv(fund_master_file)
        nh = pd.read_csv(nav_history_file)

        print("\n" + "=" * 50)
        print("2. FUND MASTER EXPLORATION")
        print("=" * 50)
        for col in ['fund_house', 'category', 'sub_category', 'risk_grade']:
            if col in fm.columns:
                print(f"Unique {col}: {fm[col].unique().tolist()[:10]}") # Display first 10 unique values

        print("\n" + "=" * 50)
        print("3. AMFI CODE VALIDATION SUMMARY")
        print("=" * 50)
        if 'scheme_code' in fm.columns and 'scheme_code' in nh.columns:
            fm_codes = set(fm['scheme_code'])
            nh_codes = set(nh['scheme_code'])
            missing_in_nav = fm_codes - nh_codes
            print(f"Total unique schemes in fund_master: {len(fm_codes)}")
            print(f"Total unique schemes in nav_history: {len(nh_codes)}")
            print(f"Codes in fund_master missing from nav_history: {len(missing_in_nav)}")
        else:
            print("Validation Note: 'scheme_code' column not found in one or both datasets.")

if __name__ == "__main__":
    inspect_datasets()