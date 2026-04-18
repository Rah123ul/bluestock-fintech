import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cur = conn.cursor()
CLEAN_DIR = "data/clean"

print("=" * 50)
print("CREATING TABLES & LOADING DATA")
print("=" * 50)

# ── CREATE TABLES ─────────────────────────────────────────────
cur.execute("""
CREATE TABLE IF NOT EXISTS dim_company (
    id SERIAL,
    company_id VARCHAR(50) PRIMARY KEY,
    company_name VARCHAR(200),
    company_logo TEXT,
    chart_link TEXT,
    about_company TEXT,
    website TEXT,
    nse_profile TEXT,
    bse_profile TEXT,
    face_value NUMERIC,
    book_value NUMERIC,
    roce_percentage NUMERIC,
    roe_percentage NUMERIC
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS fact_balance_sheet (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(50),
    year VARCHAR(20),
    year_label VARCHAR(20),
    fiscal_year INTEGER,
    sort_order INTEGER,
    equity_capital NUMERIC,
    reserves NUMERIC,
    borrowings NUMERIC,
    other_liabilities NUMERIC,
    total_liabilities NUMERIC,
    fixed_assets NUMERIC,
    cwip NUMERIC,
    investments NUMERIC,
    other_asset NUMERIC,
    total_assets NUMERIC,
    debt_to_equity NUMERIC
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS fact_profit_loss (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(50),
    year VARCHAR(20),
    year_label VARCHAR(20),
    fiscal_year INTEGER,
    sort_order INTEGER,
    sales NUMERIC,
    expenses NUMERIC,
    operating_profit NUMERIC,
    opm_percentage NUMERIC,
    other_income NUMERIC,
    interest NUMERIC,
    depreciation NUMERIC,
    profit_before_tax NUMERIC,
    tax_percentage NUMERIC,
    net_profit NUMERIC,
    eps NUMERIC,
    dividend_payout NUMERIC,
    net_profit_margin_pct NUMERIC,
    expense_ratio_pct NUMERIC,
    interest_coverage NUMERIC
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS fact_cash_flow (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(50),
    year VARCHAR(20),
    year_label VARCHAR(20),
    fiscal_year INTEGER,
    sort_order INTEGER,
    operating_activity NUMERIC,
    investing_activity NUMERIC,
    financing_activity NUMERIC,
    net_cash_flow NUMERIC,
    free_cash_flow NUMERIC
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS fact_analysis (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(50),
    compounded_sales_growth TEXT,
    compounded_profit_growth TEXT,
    stock_price_cagr TEXT,
    roe TEXT
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS fact_pros_cons (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(50),
    pros TEXT,
    cons TEXT
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS fact_documents (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(50),
    year VARCHAR(20),
    annual_report TEXT
);
""")

conn.commit()
print("✅ All tables created")

# ── LOAD DATA ─────────────────────────────────────────────────
def load_table(df, table, conflict_col="id"):
    count = 0
    for _, row in df.iterrows():
        cols = list(row.index)
        vals = [None if pd.isna(v) else v for v in row.values]
        placeholders = ",".join(["%s"] * len(cols))
        col_str = ",".join(cols)
        sql = f"INSERT INTO {table} ({col_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
        cur.execute(sql, vals)
        count += 1
    conn.commit()
    print(f"   ✅ {count} rows loaded into {table}")

# Companies
print("\nLoading companies...")
df = pd.read_csv(f"{CLEAN_DIR}/companies.csv")
df = df.rename(columns={"id": "company_id"})
load_table(df, "dim_company", "company_id")

# Balance Sheet
print("Loading balancesheet...")
df = pd.read_csv(f"{CLEAN_DIR}/balancesheet.csv")
load_table(df, "fact_balance_sheet")

# Profit & Loss
print("Loading profitandloss...")
df = pd.read_csv(f"{CLEAN_DIR}/profitandloss.csv")
load_table(df, "fact_profit_loss")

# Cash Flow
print("Loading cashflow...")
df = pd.read_csv(f"{CLEAN_DIR}/cashflow.csv")
load_table(df, "fact_cash_flow")

# Analysis
print("Loading analysis...")
df = pd.read_csv(f"{CLEAN_DIR}/analysis.csv")
load_table(df, "fact_analysis")

# Pros & Cons
print("Loading prosandcons...")
df = pd.read_csv(f"{CLEAN_DIR}/prosandcons.csv")
load_table(df, "fact_pros_cons")

# Documents
print("Loading documents...")
df = pd.read_csv(f"{CLEAN_DIR}/documents.csv")
load_table(df, "fact_documents")

# ── VERIFY ────────────────────────────────────────────────────
print("\n" + "=" * 50)
print("DATA QUALITY CHECKS")
print("=" * 50)
tables = ["dim_company","fact_balance_sheet","fact_profit_loss",
          "fact_cash_flow","fact_analysis","fact_pros_cons","fact_documents"]
for t in tables:
    cur.execute(f"SELECT COUNT(*) FROM {t}")
    count = cur.fetchone()[0]
    status = "✅" if count > 0 else "❌"
    print(f"   {status} {t}: {count} rows")

cur.close()
conn.close()
print("\n✅ WAREHOUSE LOAD COMPLETE")
