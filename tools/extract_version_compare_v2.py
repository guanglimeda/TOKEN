import pandas as pd
import os

# 输入文件路径
input_file = "/root/openclaw/kimi/downloads/19c9c7a8-4092-8b51-8000-0000dc3f3cd6_output.xlsx"

# 输出目录
output_dir = "/root/.openclaw/workspace/extracted_content"
os.makedirs(output_dir, exist_ok=True)

# 读取三版本内容对比
df = pd.read_excel(input_file, sheet_name='三版本内容对比')

print(f"总行数: {len(df)}")
print(f"\n内容方向分布:")
print(df['内容方向'].value_counts())

# 保存所有内容到一个文件
output_file = os.path.join(output_dir, "三版本内容对比.txt")

with open(output_file, 'w', encoding='utf-8') as f:
    f.write("# 三版本内容对比\n")
    f.write(f"# 共 {len(df)} 篇\n")
    f.write("="*60 + "\n\n")
    
    for idx, row in df.iterrows():
        f.write(f"## 序号 {row['序号']}\n")
        f.write(f"内容方向: {row['内容方向']}\n")
        f.write("-"*40 + "\n")
        f.write(f"{row['成稿']}\n")
        f.write("\n" + "="*60 + "\n\n")

print(f"\n✓ 已保存: 三版本内容对比.txt ({len(df)} 篇)")

# 同时追加到完整版知识库
full_version_file = "/root/.openclaw/workspace/knowledge/【小红书】美团买药内容成稿库_完整版.md"

with open(full_version_file, 'a', encoding='utf-8') as f:
    f.write("\n\n")
    f.write("# 附录：三版本内容对比（50篇）\n")
    f.write("="*60 + "\n\n")
    
    for idx, row in df.iterrows():
        f.write(f"## 序号 {row['序号']}\n")
        f.write(f"内容方向: {row['内容方向']}\n")
        f.write("-"*40 + "\n")
        f.write(f"{row['成稿']}\n")
        f.write("\n" + "="*60 + "\n\n")

print(f"✓ 已追加到完整版知识库")
