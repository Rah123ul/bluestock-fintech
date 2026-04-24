"""
etl/04_health_scoring.py
─────────────────────────────────────────────────────────────────────────────
Reads warehouse tables from Railway PostgreSQL, computes ML health scores
for each company, and writes results to fact_ml_scores.

Requirements:  pandas  sqlalchemy  python-dotenv  numpy
Usage:
    python etl/04_health_scoring.py
─────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# ── 0. Load env & connect ─────────────────────────────────────────────────────
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌  DATABASE_URL is not set. Add it to .env or export it.")
    sys.exit(1)

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, echo=False)

print("=" * 50)
print("ML HEALTH SCORING ENGINE")
print("=" * 50)
print(f"DB: {DATABASE_URL[:45]}...")

# ── 1. Load data from Railway warehouse ───────────────────────────────────────
print("\n📥  Reading warehouse tables...")
with engine.connect() as conn:
    pl        = pd.read_sql("SELECT * FROM fact_profit_loss",  conn)
    bs        = pd.read_sql("SELECT * FROM fact_balance_sheet", conn)
    cf        = pd.read_sql("SELECT * FROM fact_cash_flow",     conn)
    companies = pd.read_sql("SELECT company_id, company_name FROM dim_company", conn)

print(f"   fact_profit_loss    : {len(pl)} rows")
print(f"   fact_balance_sheet  : {len(bs)} rows")
print(f"   fact_cash_flow      : {len(cf)} rows")
print(f"   dim_company         : {len(companies)} rows")

# ── 2. Get latest year data per company ───────────────────────────────────────
def get_latest(df):
    df = df.copy()
    df["sort_order"] = pd.to_numeric(df["sort_order"], errors="coerce")
    df = df[df["year_label"] != "TTM"]
    return (df.sort_values("sort_order", ascending=False)
              .groupby("company_id")
              .first()
              .reset_index())

pl_latest = get_latest(pl)
bs_latest = get_latest(bs)
cf_latest = get_latest(cf)

# ── 3. Merge all into one scoring DataFrame ───────────────────────────────────
df = companies.copy()
df = df.merge(
    pl_latest[["company_id", "opm_percentage", "net_profit_margin_pct",
               "net_profit", "sales", "interest_coverage", "dividend_payout"]],
    on="company_id", how="left"
)
df = df.merge(
    bs_latest[["company_id", "debt_to_equity", "total_assets"]],
    on="company_id", how="left"
)
df = df.merge(
    cf_latest[["company_id", "free_cash_flow", "operating_activity"]],
    on="company_id", how="left"
)

# ── 4. Percentile rank helper ─────────────────────────────────────────────────
def percentile_rank(series, higher_is_better=True):
    ranked = series.rank(pct=True, na_option="bottom")
    return ranked if higher_is_better else 1 - ranked

# ── 5. Compute 6 sub-scores ───────────────────────────────────────────────────

# 1. Profitability (25%) — OPM% + net margin
df["p_opm"]    = percentile_rank(pd.to_numeric(df["opm_percentage"],        errors="coerce"))
df["p_margin"] = percentile_rank(pd.to_numeric(df["net_profit_margin_pct"], errors="coerce"))
df["score_profitability"] = ((df["p_opm"] + df["p_margin"]) / 2 * 100).round(2)

# 2. Revenue Growth (20%) — sales as proxy
df["score_growth"] = (
    percentile_rank(pd.to_numeric(df["sales"], errors="coerce")) * 100
).round(2)

# 3. Leverage (20%) — lower D/E is better
df["score_leverage"] = (
    percentile_rank(pd.to_numeric(df["debt_to_equity"], errors="coerce"),
                    higher_is_better=False) * 100
).round(2)

# 4. Cash Flow Quality (15%) — free cash flow
df["score_cashflow"] = (
    percentile_rank(pd.to_numeric(df["free_cash_flow"], errors="coerce")) * 100
).round(2)

# 5. Dividend (10%) — dividend payout
df["score_dividend"] = (
    percentile_rank(pd.to_numeric(df["dividend_payout"], errors="coerce")) * 100
).round(2)

# 6. Interest Coverage (10%) — higher is better
df["score_coverage"] = (
    percentile_rank(pd.to_numeric(df["interest_coverage"], errors="coerce")) * 100
).round(2)

# ── 6. Weighted final score ───────────────────────────────────────────────────
df["overall_score"] = (
    df["score_profitability"] * 0.25 +
    df["score_growth"]        * 0.20 +
    df["score_leverage"]      * 0.20 +
    df["score_cashflow"]      * 0.15 +
    df["score_dividend"]      * 0.10 +
    df["score_coverage"]      * 0.10
).round(2)

# ── 7. Health label ───────────────────────────────────────────────────────────
def get_label(score):
    if score >= 85:  return "EXCELLENT"
    elif score >= 70: return "GOOD"
    elif score >= 50: return "AVERAGE"
    elif score >= 35: return "WEAK"
    else:             return "POOR"

df["health_label"] = df["overall_score"].apply(get_label)
df["computed_at"]  = datetime.now()

# ── 8. Create table & upsert results ─────────────────────────────────────────
print("\n📐  Creating fact_ml_scores table (if not exist)...")
with engine.begin() as conn:
    conn.execute(text("""
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
        )
    """))

print("🔄  Replacing ML scores (DELETE + INSERT)...")
score_cols = [
    "company_id", "company_name", "overall_score",
    "score_profitability", "score_growth", "score_leverage",
    "score_cashflow", "score_dividend", "score_coverage",
    "health_label", "computed_at"
]
scores_df = df[score_cols].copy()

# Replace NaN with None for clean SQL inserts
scores_df = scores_df.where(pd.notnull(scores_df), None)

with engine.begin() as conn:
    conn.execute(text("DELETE FROM fact_ml_scores"))
    scores_df.to_sql("fact_ml_scores", conn,
                     if_exists="append", index=False, method="multi")

print(f"✅  {len(scores_df)} rows written to fact_ml_scores")

# ── 9. Print results ──────────────────────────────────────────────────────────
results = (df[["company_name", "overall_score", "health_label"]]
           .sort_values("overall_score", ascending=False)
           .reset_index(drop=True))

print("\n🏆  TOP 10 COMPANIES")
print(results.head(10).to_string(index=False))

print("\n⚠️   BOTTOM 10 COMPANIES")
print(results.tail(10).to_string(index=False))

print("\n📊  LABEL DISTRIBUTION")
print(df["health_label"].value_counts().to_string())

print("\n✅  SCORES SAVED TO fact_ml_scores TABLE")
