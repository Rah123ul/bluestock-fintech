import pandas as pd
import numpy as np
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

print("=" * 50)
print("ML HEALTH SCORING ENGINE")
print("=" * 50)

# ── Load data from warehouse ──────────────────────────────────
pl = pd.read_sql("SELECT * FROM fact_profit_loss", engine)
bs = pd.read_sql("SELECT * FROM fact_balance_sheet", engine)
cf = pd.read_sql("SELECT * FROM fact_cash_flow", engine)
companies = pd.read_sql("SELECT company_id, company_name FROM dim_company", engine)

# ── Get latest year data per company ─────────────────────────
def get_latest(df):
    df = df.copy()
    df["sort_order"] = pd.to_numeric(df["sort_order"], errors="coerce")
    df = df[df["year_label"] != "TTM"]
    return df.sort_values("sort_order", ascending=False).groupby("company_id").first().reset_index()

pl_latest = get_latest(pl)
bs_latest = get_latest(bs)
cf_latest = get_latest(cf)

# ── Merge all into one scoring DataFrame ─────────────────────
df = companies.copy()
df = df.merge(pl_latest[["company_id","opm_percentage","net_profit_margin_pct",
                           "net_profit","sales","interest_coverage","dividend_payout"]],
              on="company_id", how="left")
df = df.merge(bs_latest[["company_id","debt_to_equity","total_assets"]],
              on="company_id", how="left")
df = df.merge(cf_latest[["company_id","free_cash_flow","operating_activity"]],
              on="company_id", how="left")

# ── Percentile rank helper (higher = better) ─────────────────
def percentile_rank(series, higher_is_better=True):
    ranked = series.rank(pct=True, na_option="bottom")
    return ranked if higher_is_better else 1 - ranked

# ── Compute 6 sub-scores ─────────────────────────────────────

# 1. Profitability (25%) — OPM% + net margin
df["p_opm"]    = percentile_rank(pd.to_numeric(df["opm_percentage"], errors="coerce"))
df["p_margin"] = percentile_rank(pd.to_numeric(df["net_profit_margin_pct"], errors="coerce"))
df["score_profitability"] = ((df["p_opm"] + df["p_margin"]) / 2 * 100).round(2)

# 2. Revenue Growth (20%) — sales as proxy
df["score_growth"] = (percentile_rank(pd.to_numeric(df["sales"], errors="coerce")) * 100).round(2)

# 3. Leverage (20%) — lower D/E is better
df["score_leverage"] = (percentile_rank(pd.to_numeric(df["debt_to_equity"], errors="coerce"),
                                         higher_is_better=False) * 100).round(2)

# 4. Cash Flow Quality (15%) — free cash flow > 0
df["score_cashflow"] = (percentile_rank(pd.to_numeric(df["free_cash_flow"], errors="coerce")) * 100).round(2)

# 5. Dividend (10%) — dividend payout
df["score_dividend"] = (percentile_rank(pd.to_numeric(df["dividend_payout"], errors="coerce")) * 100).round(2)

# 6. Interest Coverage (10%) — higher is better
df["score_coverage"] = (percentile_rank(pd.to_numeric(df["interest_coverage"], errors="coerce")) * 100).round(2)

# ── Weighted final score ──────────────────────────────────────
df["overall_score"] = (
    df["score_profitability"] * 0.25 +
    df["score_growth"]        * 0.20 +
    df["score_leverage"]      * 0.20 +
    df["score_cashflow"]      * 0.15 +
    df["score_dividend"]      * 0.10 +
    df["score_coverage"]      * 0.10
).round(2)

# ── Assign health label ───────────────────────────────────────
def get_label(score):
    if score >= 85: return "EXCELLENT"
    elif score >= 70: return "GOOD"
    elif score >= 50: return "AVERAGE"
    elif score >= 35: return "WEAK"
    else: return "POOR"

df["health_label"] = df["overall_score"].apply(get_label)
df["computed_at"] = datetime.now()

# ── Save to PostgreSQL ────────────────────────────────────────
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS fact_ml_scores (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(50),
    company_name VARCHAR(200),
    overall_score NUMERIC,
    score_profitability NUMERIC,
    score_growth NUMERIC,
    score_leverage NUMERIC,
    score_cashflow NUMERIC,
    score_dividend NUMERIC,
    score_coverage NUMERIC,
    health_label VARCHAR(20),
    computed_at TIMESTAMP
);
""")
cur.execute("DELETE FROM fact_ml_scores")
conn.commit()

for _, row in df.iterrows():
    cur.execute("""
        INSERT INTO fact_ml_scores
        (company_id, company_name, overall_score, score_profitability,
         score_growth, score_leverage, score_cashflow, score_dividend,
         score_coverage, health_label, computed_at)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        row["company_id"], row["company_name"],
        row["overall_score"], row["score_profitability"],
        row["score_growth"], row["score_leverage"],
        row["score_cashflow"], row["score_dividend"],
        row["score_coverage"], row["health_label"], row["computed_at"]
    ))
conn.commit()

# ── Print results ─────────────────────────────────────────────
results = df[["company_name","overall_score","health_label"]].sort_values(
    "overall_score", ascending=False).reset_index(drop=True)

print("\n🏆 TOP 10 COMPANIES")
print(results.head(10).to_string(index=False))

print("\n⚠️  BOTTOM 10 COMPANIES")
print(results.tail(10).to_string(index=False))

print("\n📊 LABEL DISTRIBUTION")
print(df["health_label"].value_counts().to_string())

print("\n✅ SCORES SAVED TO fact_ml_scores TABLE")
cur.close()
conn.close()
