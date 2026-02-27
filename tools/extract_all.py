import pandas as pd

file = "/root/openclaw/kimi/downloads/19c9c7a8-4092-8b51-8000-0000dc3f3cd6_output.xlsx"

# 读取飞书文档成稿汇总
df = pd.read_excel(file, sheet_name='飞书文档成稿汇总')

# 按内容方向分组输出
for category in df['内容方向'].unique():
    if pd.isna(category):
        continue
    print(f"\n{'='*60}")
    print(f"【{category}】")
    print('='*60)
    subset = df[df['内容方向'] == category]
    for idx, row in subset.iterrows():
        print(f"\n--- 序号 {row['序号']} ---")
        print(f"成稿内容:\n{row['成稿'][:500]}...")
        print("-"*40)
