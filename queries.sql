-- ==========================================
-- CAPSTONE PROJECT I: MUTUAL FUND ANALYTICS
-- Analytical SQL Queries (Task 6)
-- ==========================================

-- 1. Top 5 funds by AUM (Assets Under Management)
SELECT 
    d.scheme_name, 
    f.aum_value 
FROM fact_aum f
JOIN dim_fund d ON f.amfi_code = d.amfi_code
ORDER BY f.aum_value DESC
LIMIT 5;

-- 2. Average NAV per month
SELECT 
    strftime('%Y-%m', date) AS month, 
    AVG(nav) AS avg_nav
FROM fact_nav
GROUP BY strftime('%Y-%m', date)
ORDER BY month DESC;

-- 3. SIP YoY (Year-over-Year) growth
SELECT 
    strftime('%Y', date) AS year, 
    SUM(amount) AS total_sip_amount,
    (SUM(amount) - LAG(SUM(amount)) OVER (ORDER BY strftime('%Y', date))) / LAG(SUM(amount)) OVER (ORDER BY strftime('%Y', date)) * 100 AS yoy_growth_percentage
FROM fact_transactions
WHERE transaction_type = 'SIP'
GROUP BY strftime('%Y', date);

-- 4. Transactions by state (assuming investor location data exists in a dim_investor table)
SELECT 
    state, 
    COUNT(transaction_id) AS total_transactions, 
    SUM(amount) AS total_volume
FROM fact_transactions t
-- JOIN dim_investor i ON t.investor_id = i.investor_id
GROUP BY state
ORDER BY total_volume DESC;

-- 5. Funds with expense_ratio < 1%
SELECT 
    d.scheme_name, 
    p.expense_ratio 
FROM fact_performance p
JOIN dim_fund d ON p.amfi_code = d.amfi_code
WHERE p.expense_ratio < 1.0
ORDER BY p.expense_ratio ASC;

-- ==========================================
-- 5 ADDITIONAL QUERIES OF CHOICE
-- ==========================================

-- 6. Total amount redeemed versus invested (SIP + Lumpsum)
SELECT 
    transaction_type, 
    SUM(amount) AS total_amount
FROM fact_transactions
GROUP BY transaction_type;

-- 7. Count of pending vs. verified KYC statuses
SELECT 
    KYC_status, 
    COUNT(*) AS investor_count
FROM fact_transactions
GROUP BY KYC_status;

-- 8. Top 3 categories by average expense ratio
SELECT 
    d.category, 
    AVG(p.expense_ratio) AS avg_expense_ratio
FROM fact_performance p
JOIN dim_fund d ON p.amfi_code = d.amfi_code
GROUP BY d.category
ORDER BY avg_expense_ratio DESC
LIMIT 3;

-- 9. Largest single lumpsum investment
SELECT 
    transaction_id, 
    investor_id, 
    amfi_code, 
    amount, 
    date 
FROM fact_transactions
WHERE transaction_type = 'Lumpsum'
ORDER BY amount DESC
LIMIT 1;

-- 10. Highest ever recorded NAV for each fund
SELECT 
    d.scheme_name, 
    MAX(n.nav) AS highest_nav
FROM fact_nav n
JOIN dim_fund d ON n.amfi_code = d.amfi_code
GROUP BY d.scheme_name
ORDER BY highest_nav DESC;