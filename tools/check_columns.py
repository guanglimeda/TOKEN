import pandas as pd

# 输入文件路径
input_file = "/root/openclaw/kimi/downloads/19c9c7a8-4092-8b51-8000-0000dc3f3cd6_output.xlsx"

# 读取三版本内容对比
df = pd.read_excel(input_file, sheet_name='三版本内容对比')

print(f"总行数: {len(df)}")
print(f"\n列名: {df.columns.tolist()}")
print(f"\n前3行数据:")
print(df.head(3))
