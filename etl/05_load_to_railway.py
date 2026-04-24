"""
etl/05_load_to_railway.py
─────────────────────────────────────────────────────────────────────────────
Loads data from data/clean/ CSV files into Railway PostgreSQL.

Requirements:  pandas  sqlalchemy  python-dotenv
Usage:
    export DATABASE_URL="postgresql://user:pass@host:port/dbname"
    python etl/05_load_to_railway.py
─────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# ── 0. Load env & resolve DATABASE_URL ───────────────────────────────────────
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌  DATABASE_URL is not set. Add it to your .env or export it.")
    sys.exit(1)

# Railway sometimes returns "postgres://" — SQLAlchemy needs "postgresql://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

CLEAN_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "clean")

print("=" * 60)
print("  BLUESTOCK → RAILWAY  |  ETL LOADER")
print("=" * 60)
print(f"  DB  : {DATABASE_URL[:40]}...")
print(f"  Data: {CLEAN_DIR}")
print("=" * 60)

# ── 1. Create SQLAlchemy engine ───────────────────────────────────────────────
engine = create_engine(DATABASE_URL, echo=False)

# ── 2. DDL — Create tables if they don't exist ────────────────────────────────
DDL = """
-- dim_company
CREATE TABLE IF NOT EXISTS dim_company (
    company_id      VARCHAR(50)  PRIMARY KEY,
    company_logo    TEXT,
    company_name    VARCHAR(200),
    chart_link      TEXT,
    about_company   TEXT,
    website         TEXT,
    nse_profile     TEXT,
    bse_profile     TEXT,
    face_value      NUMERIC,
    book_value      NUMERIC,
    roce_percentage NUMERIC,
    roe_percentage  NUMERIC
);

-- fact_profit_loss
CREATE TABLE IF NOT EXISTS fact_profit_loss (
    id                    SERIAL PRIMARY KEY,
    company_id            VARCHAR(50),
    year                  VARCHAR(20),
    year_label            VARCHAR(20),
    fiscal_year           INTEGER,
    sort_order            INTEGER,
    sales                 NUMERIC,
    expenses              NUMERIC,
    operating_profit      NUMERIC,
    opm_percentage        NUMERIC,
    other_income          NUMERIC,
    interest              NUMERIC,
    depreciation          NUMERIC,
    profit_before_tax     NUMERIC,
    tax_percentage        NUMERIC,
    net_profit            NUMERIC,
    eps                   NUMERIC,
    dividend_payout       NUMERIC,
    net_profit_margin_pct NUMERIC,
    expense_ratio_pct     NUMERIC,
    interest_coverage     NUMERIC
);

-- fact_balance_sheet
CREATE TABLE IF NOT EXISTS fact_balance_sheet (
    id               SERIAL PRIMARY KEY,
    company_id       VARCHAR(50),
    year             VARCHAR(20),
    year_label       VARCHAR(20),
    fiscal_year      INTEGER,
    sort_order       INTEGER,
    equity_capital   NUMERIC,
    reserves         NUMERIC,
    borrowings       NUMERIC,
    other_liabilities NUMERIC,
    total_liabilities NUMERIC,
    fixed_assets     NUMERIC,
    cwip             NUMERIC,
    investments      NUMERIC,
    other_asset      NUMERIC,
    total_assets     NUMERIC,
    debt_to_equity   NUMERIC
);

-- fact_cash_flow
CREATE TABLE IF NOT EXISTS fact_cash_flow (
    id                  SERIAL PRIMARY KEY,
    company_id          VARCHAR(50),
    year                VARCHAR(20),
    year_label          VARCHAR(20),
    fiscal_year         INTEGER,
    sort_order          INTEGER,
    operating_activity  NUMERIC,
    investing_activity  NUMERIC,
    financing_activity  NUMERIC,
    net_cash_flow       NUMERIC,
    free_cash_flow      NUMERIC
);

-- fact_analysis
CREATE TABLE IF NOT EXISTS fact_analysis (
    id                      SERIAL PRIMARY KEY,
    company_id              VARCHAR(50),
    compounded_sales_growth TEXT,
    compounded_profit_growth TEXT,
    stock_price_cagr        TEXT,
    roe                     TEXT
);

-- fact_pros_cons
CREATE TABLE IF NOT EXISTS fact_pros_cons (
    id         SERIAL PRIMARY KEY,
    company_id VARCHAR(50),
    pros       TEXT,
    cons       TEXT
);

-- fact_documents
CREATE TABLE IF NOT EXISTS fact_documents (
    id            SERIAL PRIMARY KEY,
    company_id    VARCHAR(50),
    year          VARCHAR(20),
    annual_report TEXT
);

-- fact_ml_scores
CREATE TABLE IF NOT EXISTS fact_ml_scores (
    id                  SERIAL PRIMARY KEY,
    company_id          VARCHAR(50),
    company_name        VARCHAR(200),
    overall_score       NUMERIC,
    score_profitability NUMERIC,
    score_growth        NUMERIC,
    score_leverage      NUMERIC,
    score_cashflow      NUMERIC,
    score_dividend      NUMERIC,
    score_coverage      NUMERIC,
    health_label        VARCHAR(20),
    computed_at         TIMESTAMP
);
"""

print("\n📐  Creating tables (if not exist)...")
with engine.begin() as conn:
    for stmt in DDL.strip().split(";"):
        stmt = stmt.strip()
        if stmt:
            conn.execute(text(stmt))
print("✅  All 8 tables ready.\n")


# ── 3. Generic upsert helper ──────────────────────────────────────────────────
def upsert_df(df: pd.DataFrame, table: str, conflict_col: str | None = None) -> int:
    """
    Insert rows with ON CONFLICT DO NOTHING.
    Uses a temp table + INSERT ... SELECT approach so we stay within
    pure SQLAlchemy / pandas — no psycopg2 required.

    Returns the number of rows in the DataFrame (attempted inserts).
    """
    if df.empty:
        print(f"   ⚠️  {table}: CSV is empty — skipping.")
        return 0

    tmp = f"_tmp_{table}"
    with engine.begin() as conn:
        # Write to a temporary staging table (replace each run)
        df.to_sql(tmp, conn, if_exists="replace", index=False, method="multi")

        cols = ", ".join(f'"{c}"' for c in df.columns)

        if conflict_col:
            sql = text(
                f'INSERT INTO "{table}" ({cols}) '
                f'SELECT {cols} FROM "{tmp}" '
                f'ON CONFLICT ("{conflict_col}") DO NOTHING'
            )
        else:
            sql = text(
                f'INSERT INTO "{table}" ({cols}) '
                f'SELECT {cols} FROM "{tmp}" '
                f'ON CONFLICT DO NOTHING'
            )
        conn.execute(sql)
        conn.execute(text(f'DROP TABLE IF EXISTS "{tmp}"'))

    return len(df)


# ── 4. Load each CSV ──────────────────────────────────────────────────────────
def csv_path(name: str) -> str:
    return os.path.join(CLEAN_DIR, name)


loaders = [
    # (csv_file,          table_name,          conflict_col,   col_renames)
    ("companies.csv",    "dim_company",        "company_id",   {"id": "company_id"}),
    ("profitandloss.csv","fact_profit_loss",   None,           {}),
    ("balancesheet.csv", "fact_balance_sheet", None,           {}),
    ("cashflow.csv",     "fact_cash_flow",     None,           {}),
    ("analysis.csv",     "fact_analysis",      None,           {"id": None}),   # drop surrogate id
    ("prosandcons.csv",  "fact_pros_cons",     None,           {"id": None}),
    ("documents.csv",    "fact_documents",     None,           {"id": None}),
]

results = {}
print("📦  Loading CSV files into Railway PostgreSQL...\n")

for csv_file, table, conflict_col, renames in loaders:
    fpath = csv_path(csv_file)
    if not os.path.exists(fpath):
        print(f"   ⚠️  {csv_file} not found — skipping {table}")
        continue

    df = pd.read_csv(fpath)

    # apply renames / drops
    for old_col, new_col in renames.items():
        if old_col in df.columns:
            if new_col is None:
                df = df.drop(columns=[old_col])
            else:
                df = df.rename(columns={old_col: new_col})

    count = upsert_df(df, table, conflict_col)
    results[table] = count
    print(f"   ✅  {table:<25}  {count:>5} rows attempted")

# fact_ml_scores has no source CSV (computed by 04_health_scoring.py) — skip if absent
ml_csv = csv_path("ml_scores.csv")
if os.path.exists(ml_csv):
    df = pd.read_csv(ml_csv)
    if "id" in df.columns:
        df = df.drop(columns=["id"])
    count = upsert_df(df, "fact_ml_scores", None)
    results["fact_ml_scores"] = count
    print(f"   ✅  fact_ml_scores           {count:>5} rows attempted")
else:
    print("   ℹ️   fact_ml_scores: no ml_scores.csv found (run 04_health_scoring.py first).")
    results["fact_ml_scores"] = 0

# ── 5. Final row-count verification ──────────────────────────────────────────
print("\n" + "=" * 60)
print("  POST-LOAD ROW COUNTS")
print("=" * 60)

all_tables = [
    "dim_company", "fact_profit_loss", "fact_balance_sheet",
    "fact_cash_flow", "fact_analysis", "fact_pros_cons",
    "fact_documents", "fact_ml_scores",
]

with engine.connect() as conn:
    for tbl in all_tables:
        row = conn.execute(text(f'SELECT COUNT(*) FROM "{tbl}"')).fetchone()
        count = row[0] if row else 0
        status = "✅" if count > 0 else "⚠️ "
        print(f"   {status}  {tbl:<25}  {count:>6} rows")

print("=" * 60)
print("  ✅  RAILWAY LOAD COMPLETE")
print("=" * 60)
