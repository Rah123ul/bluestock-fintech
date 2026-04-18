import pandas as pd
import numpy as np
import os
import re

RAW_DIR = "data/raw"
CLEAN_DIR = "data/clean"
os.makedirs(CLEAN_DIR, exist_ok=True)

# ── Year standardization ──────────────────────────────────────
def standardize_year(val):
    if pd.isna(val):
        return None, None, None
    val = str(val).strip()
    if val == "TTM":
        return "TTM", None, 9999
    # Mar-24 → Mar 2024
    m = re.match(r"([A-Za-z]{3})-(\d{2})$", val)
    if m:
        month, yr = m.group(1), int(m.group(2))
        year = 2000 + yr if yr < 50 else 1900 + yr
        label = f"{month.capitalize()} {year}"
        return label, year, year * 10
    # Mar 2024
    m = re.match(r"([A-Za-z]{3})\s(\d{4})$", val)
    if m:
        month, year = m.group(1), int(m.group(2))
        label = f"{month.capitalize()} {year}"
        return label, year, year * 10
    return val, None, None

# ── Helper: replace string NULLs ─────────────────────────────
def clean_nulls(df):
    return df.replace(["NULL", "Null", "null", "None", ""], np.nan)

# ── 1. COMPANIES ─────────────────────────────────────────────
print("Cleaning companies...")
df = pd.read_csv(f"{RAW_DIR}/companies.csv")
df = clean_nulls(df)
df["company_name"] = df["company_name"].str.strip()
df.to_csv(f"{CLEAN_DIR}/companies.csv", index=False)
print(f"   ✅ {len(df)} rows saved")

# ── 2. BALANCE SHEET ─────────────────────────────────────────
print("Cleaning balancesheet...")
df = pd.read_csv(f"{RAW_DIR}/balancesheet.csv")
df = clean_nulls(df)
result = df["year"].apply(lambda x: pd.Series(standardize_year(x), index=["year_label","fiscal_year","sort_order"]))
df[["year_label","fiscal_year","sort_order"]] = result
df["debt_to_equity"] = pd.to_numeric(df["borrowings"], errors="coerce") / (
    pd.to_numeric(df["equity_capital"], errors="coerce") +
    pd.to_numeric(df["reserves"], errors="coerce"))
df.to_csv(f"{CLEAN_DIR}/balancesheet.csv", index=False)
print(f"   ✅ {len(df)} rows saved")

# ── 3. PROFIT & LOSS ─────────────────────────────────────────
print("Cleaning profitandloss...")
df = pd.read_csv(f"{RAW_DIR}/profitandloss.csv")
df = clean_nulls(df)
result = df["year"].apply(lambda x: pd.Series(standardize_year(x), index=["year_label","fiscal_year","sort_order"]))
df[["year_label","fiscal_year","sort_order"]] = result
sales = pd.to_numeric(df["sales"], errors="coerce")
df["net_profit_margin_pct"] = (pd.to_numeric(df["net_profit"], errors="coerce") / sales) * 100
df["expense_ratio_pct"] = (pd.to_numeric(df["expenses"], errors="coerce") / sales) * 100
df["interest_coverage"] = pd.to_numeric(df["operating_profit"], errors="coerce") / pd.to_numeric(df["interest"], errors="coerce")
df.to_csv(f"{CLEAN_DIR}/profitandloss.csv", index=False)
print(f"   ✅ {len(df)} rows saved")

# ── 4. CASH FLOW ─────────────────────────────────────────────
print("Cleaning cashflow...")
df = pd.read_csv(f"{RAW_DIR}/cashflow.csv")
df = clean_nulls(df)
result = df["year"].apply(lambda x: pd.Series(standardize_year(x), index=["year_label","fiscal_year","sort_order"]))
df[["year_label","fiscal_year","sort_order"]] = result
df["free_cash_flow"] = (
    pd.to_numeric(df["operating_activity"], errors="coerce") +
    pd.to_numeric(df["investing_activity"], errors="coerce"))
df.to_csv(f"{CLEAN_DIR}/cashflow.csv", index=False)
print(f"   ✅ {len(df)} rows saved")

# ── 5. ANALYSIS ──────────────────────────────────────────────
print("Cleaning analysis...")
df = pd.read_csv(f"{RAW_DIR}/analysis.csv")
df = clean_nulls(df)
df.to_csv(f"{CLEAN_DIR}/analysis.csv", index=False)
print(f"   ✅ {len(df)} rows saved")

# ── 6. PROS & CONS ───────────────────────────────────────────
print("Cleaning prosandcons...")
df = pd.read_csv(f"{RAW_DIR}/prosandcons.csv")
df = clean_nulls(df)
df.to_csv(f"{CLEAN_DIR}/prosandcons.csv", index=False)
print(f"   ✅ {len(df)} rows saved")

# ── 7. DOCUMENTS ─────────────────────────────────────────────
print("Cleaning documents...")
df = pd.read_csv(f"{RAW_DIR}/documents.csv")
df = clean_nulls(df)
df.columns = [c.lower() for c in df.columns]
df.to_csv(f"{CLEAN_DIR}/documents.csv", index=False)
print(f"   ✅ {len(df)} rows saved")

print("\n✅ ALL TABLES CLEANED AND SAVED TO data/clean/")
