# Mutual Fund Analytics - Data Dictionary

## 1. dim_fund

Stores descriptive attributes of the mutual fund schemes.

* **amfi_code** (INTEGER, Primary Key): Unique identifier for the mutual fund scheme provided by AMFI.
* **scheme_name** (TEXT): Full name of the mutual fund scheme.
* **category** (TEXT): Broad asset class (e.g., Equity, Debt, Hybrid).
* **sub_category** (TEXT): Specific category within the asset class (e.g., Large Cap, Liquid).

## 2. fact_nav

Stores the historical Net Asset Value (NAV) daily records.

* **id** (INTEGER, Primary Key): Auto-incrementing unique row identifier.
* **amfi_code** (INTEGER, Foreign Key): References `dim_fund(amfi_code)`.
* **date** (DATE): Date of the NAV record.
* **nav** (REAL): Net Asset Value of the fund on the given date (validated > 0).

## 3. fact_transactions

Stores individual investor transactions (SIPs, Lumpsums, Redemptions).

* **transaction_id** (TEXT, Primary Key): Unique identifier for the transaction.
* **amfi_code** (INTEGER, Foreign Key): References `dim_fund(amfi_code)`.
* **investor_id** (TEXT): Unique identifier for the investor.
* **date** (DATE): Date the transaction was executed.
* **transaction_type** (TEXT): Standardised to 'SIP', 'Lumpsum', or 'Redemption'.
* **amount** (REAL): Transaction amount in INR (validated > 0).
* **KYC_status** (TEXT): Investor's KYC status ('Verified', 'Pending', 'Rejected').

## 4. fact_performance

Stores annual performance metrics and risk flags for the funds.

* **amfi_code** (INTEGER, Primary Key/Foreign Key): References `dim_fund(amfi_code)`.
* **expense_ratio** (REAL): Annual fee charged by the fund (validated between 0.1% and 2.5%).
* **anomaly_flag** (BOOLEAN): True if returns are highly anomalous (e.g., > 100% or < -50%).

## 5. fact_aum & dim_date

*(Note: Included in schema design for extended analytical queries).*

* **fact_aum**: Tracks total Assets Under Management (`aum_value`) per fund.
* **dim_date**: Standard calendar dimension table for time-series aggregation.
