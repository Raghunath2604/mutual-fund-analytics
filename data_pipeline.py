import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text

# Setup SQLite Engine
engine = create_engine('sqlite:///bluestock_mf.db')

print("Starting Data Pipeline...")

# ---------------------------------------------------------
# 1. Clean investor_transactions.csv
# ---------------------------------------------------------
print("1. Cleaning investor_transactions.csv...")
df_tx = pd.read_csv('data/raw/investor_transactions.csv')

# Strip leading/trailing spaces from column names and lowercase them
df_tx.columns = df_tx.columns.str.strip().str.lower()

# Identify the date column dynamically
date_col = next((col for col in df_tx.columns if 'date' in col), None)
if date_col:
    df_tx['date'] = pd.to_datetime(df_tx[date_col])
else:
    raise KeyError("Could not find a date column in investor_transactions.csv")

# Standardize transaction types
type_col = next((col for col in df_tx.columns if 'type' in col), 'transaction_type')
tx_mapping = {'sip': 'SIP', 's.i.p': 'SIP', 'lumpsum': 'Lumpsum', 'lump sum': 'Lumpsum', 'redemption': 'Redemption', 'redeem': 'Redemption'}
df_tx['transaction_type'] = df_tx[type_col].astype(str).str.strip().str.lower().replace(tx_mapping)
df_tx = df_tx[df_tx['transaction_type'].isin(['SIP', 'Lumpsum', 'Redemption'])]

# Validate amount > 0
amt_col = next((col for col in df_tx.columns if 'amount' in col or 'amt' in col), 'amount')
df_tx['amount'] = pd.to_numeric(df_tx[amt_col], errors='coerce')
df_tx = df_tx[df_tx['amount'] > 0]

# Standardize KYC status
kyc_col = next((col for col in df_tx.columns if 'kyc' in col), None)
if kyc_col:
    df_tx['KYC_status'] = df_tx[kyc_col].astype(str).str.strip().str.title()
    df_tx = df_tx[df_tx['KYC_status'].isin(['Verified', 'Pending', 'Rejected'])]

# Keep standard schema columns
df_tx = df_tx[['date', 'transaction_type', 'amount', 'KYC_status']]
df_tx.to_csv('data/processed/clean_investor_transactions.csv', index=False)

# ---------------------------------------------------------
# 2. Clean nav_history.csv
# ---------------------------------------------------------
print("2. Cleaning nav_history.csv...")
df_nav = pd.read_csv('data/raw/nav_history.csv')
df_nav.columns = df_nav.columns.str.strip().str.lower()

nav_date = next((col for col in df_nav.columns if 'date' in col), 'date')
df_nav['date'] = pd.to_datetime(df_nav[nav_date])

amfi_col = next((col for col in df_nav.columns if 'amfi' in col or 'code' in col), 'amfi_code')
nav_val_col = next((col for col in df_nav.columns if 'nav' in col), 'nav')

df_nav = df_nav.sort_values(by=[amfi_col, 'date'])
df_nav = df_nav.drop_duplicates(subset=[amfi_col, 'date'])
df_nav['nav'] = pd.to_numeric(df_nav[nav_val_col], errors='coerce')
df_nav['nav'] = df_nav.groupby(amfi_col)['nav'].ffill()
df_nav = df_nav[df_nav['nav'] > 0]

df_nav.to_csv('data/processed/clean_nav_history.csv', index=False)

# ---------------------------------------------------------
# 3. Clean scheme_performance.csv
# ---------------------------------------------------------
print("3. Cleaning scheme_performance.csv...")
df_perf = pd.read_csv('data/raw/scheme_performance.csv')
df_perf.columns = df_perf.columns.str.strip().str.lower()

return_cols = [col for col in df_perf.columns if 'return' in col]
for col in return_cols:
    df_perf[col] = pd.to_numeric(df_perf[col], errors='coerce')

df_perf['anomaly_flag'] = False
if '1y_return' in df_perf.columns:
    df_perf.loc[(df_perf['1y_return'] > 100) | (df_perf['1y_return'] < -50), 'anomaly_flag'] = True

if 'expense_ratio' in df_perf.columns:
    df_perf['expense_ratio'] = pd.to_numeric(df_perf['expense_ratio'], errors='coerce')
    df_perf = df_perf[(df_perf['expense_ratio'] >= 0.1) & (df_perf['expense_ratio'] <= 2.5)]

df_perf.to_csv('data/processed/clean_scheme_performance.csv', index=False)

# ---------------------------------------------------------
# 4 & 5. Create Star Schema & Load Data into SQLite
# ---------------------------------------------------------
print("Creating Star Schema and Loading data into SQLite...")

with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS dim_fund (
            amfi_code INTEGER PRIMARY KEY,
            scheme_name TEXT,
            category TEXT,
            sub_category TEXT
        );
    """))
    
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS fact_nav (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amfi_code INTEGER,
            date DATE,
            nav REAL,
            FOREIGN KEY(amfi_code) REFERENCES dim_fund(amfi_code)
        );
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS fact_transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE,
            transaction_type TEXT,
            amount REAL,
            KYC_status TEXT
        );
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS fact_performance (
            amfi_code INTEGER PRIMARY KEY,
            expense_ratio REAL,
            anomaly_flag BOOLEAN,
            FOREIGN KEY(amfi_code) REFERENCES dim_fund(amfi_code)
        );
    """))

df_nav.to_sql('fact_nav', con=engine, if_exists='append', index=False)
df_tx.to_sql('fact_transactions', con=engine, if_exists='append', index=False)
df_perf.to_sql('fact_performance', con=engine, if_exists='append', index=False)

print("Pipeline executed successfully! Database 'bluestock_mf.db' created.")