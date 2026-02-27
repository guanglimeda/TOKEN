import pandas as pd
import sys

files = [
    "/root/openclaw/kimi/downloads/19c9c6f6-5632-8706-8000-00000364fe4f_杭州医佳医生刊例-5月-带价格.xlsx",
    "/root/openclaw/kimi/downloads/19c9c6f5-e022-8b34-8000-00009df88a41_医佳医疗APP医生账号价格参考1203.xlsx",
    "/root/openclaw/kimi/downloads/19c9c6f8-5b52-8ba6-8000-0000bf656053_杭州医佳X维翠美达人合作LIST.xlsx",
    "/root/openclaw/kimi/downloads/19c9c6f5-e092-83a2-8000-000019d517a5_千问-微博-医生账号需求-0212.xlsx",
    "/root/openclaw/kimi/downloads/19c9c6f6-fec2-8570-8000-00005f0d94ca_跨境奥泰灵-骨科医生合作需求BF211-0225.xlsx",
    "/root/openclaw/kimi/downloads/19c9c6f6-7692-8f5a-8000-00006c19ed1d_杭州医佳医生专业内容及自媒体名单-2025_副本.xlsx"
]

for f in files:
    print(f"\n{'='*60}")
    print(f"文件: {f.split('/')[-1]}")
    print('='*60)
    try:
        # 读取所有sheet
        xl = pd.ExcelFile(f)
        print(f"Sheets: {xl.sheet_names}")
        
        for sheet in xl.sheet_names[:2]:  # 只读前2个sheet
            print(f"\n--- Sheet: {sheet} ---")
            df = pd.read_excel(f, sheet_name=sheet, nrows=20)  # 只读前20行
            print(f"列名: {list(df.columns)}")
            print(df.head(10).to_string())
            print(f"... 共 {len(df)} 行")
    except Exception as e:
        print(f"错误: {e}")
