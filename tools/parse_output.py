import pandas as pd

file = "/root/openclaw/kimi/downloads/19c9c7a8-4092-8b51-8000-0000dc3f3cd6_output.xlsx"

print(f"{'='*60}")
print(f"文件: output.xlsx")
print('='*60)

try:
    xl = pd.ExcelFile(file)
    print(f"Sheets: {xl.sheet_names}")
    
    for sheet in xl.sheet_names:
        print(f"\n--- Sheet: {sheet} ---")
        df = pd.read_excel(file, sheet_name=sheet)
        print(f"列名: {list(df.columns)}")
        print(f"总行数: {len(df)}")
        print(df.head(20).to_string())
        print("\n" + "-"*40)
except Exception as e:
    print(f"错误: {e}")
