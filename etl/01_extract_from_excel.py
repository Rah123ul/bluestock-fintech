import pandas as pd
import os

RAW_DIR = "data/raw"

FILES = {
    "companies":     "companies.xlsx",
    "analysis":      "analysis.xlsx",
    "balancesheet":  "balancesheet.xlsx",
    "profitandloss": "profitandloss.xlsx",
    "cashflow":      "cashflow.xlsx",
    "prosandcons":   "prosandcons.xlsx",
    "documents":     "documents.xlsx",
}

print("=" * 50)
print("EXTRACTING EXCEL FILES")
print("=" * 50)

for table_name, filename in FILES.items():
    filepath = os.path.join(RAW_DIR, filename)
    try:
        # skiprows=1 skips the title row, real headers are on row 2
        df = pd.read_excel(filepath, skiprows=1)
        print(f"\n✅ {table_name}")
        print(f"   Rows: {len(df)}")
        print(f"   Columns: {list(df.columns)}")
        csv_path = os.path.join(RAW_DIR, f"{table_name}.csv")
        df.to_csv(csv_path, index=False)
        print(f"   Saved: {csv_path}")
    except Exception as e:
        print(f"\n❌ {table_name} FAILED: {e}")

print("\n" + "=" * 50)
print("EXTRACTION COMPLETE")
print("=" * 50)
