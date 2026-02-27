import pandas as pd

file = "/root/openclaw/kimi/downloads/19c9c7a8-4092-8b51-8000-0000dc3f3cd6_output.xlsx"

print("=== 飞书文档成稿汇总 ===")
df1 = pd.read_excel(file, sheet_name='飞书文档成稿汇总')
print(f"总行数: {len(df1)}")
print(f"\n内容方向分布:")
print(df1['内容方向'].value_counts())
print(f"\n前10行内容方向:")
print(df1[['序号', '内容方向']].head(10))

print("\n\n=== 三版本内容对比 ===")
df2 = pd.read_excel(file, sheet_name='三版本内容对比')
print(f"总行数: {len(df2)}")
print(f"\n内容方向分布:")
print(df2['内容方向'].value_counts())
