import pandas as pd

file = r"E:\60-Day Python AI Portfolio Roadmap\Sales Analytics Dashboard\AggregateAnalytics_Sumair Ahmed Dero_2026-06-12_2026-06-18.xlsx"

excel = pd.ExcelFile(file)

print("Sheet Names:")
print(excel.sheet_names)

for sheet in excel.sheet_names:
    print("\n" + "=" * 50)
    print(f"Sheet: {sheet}")
    print("=" * 50)

    df = pd.read_excel(file, sheet_name=sheet)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nFirst 5 Rows:")
    print(df.head())