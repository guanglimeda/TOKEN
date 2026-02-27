import pandas as pd
import os

# 输入文件路径
input_file = "/root/openclaw/kimi/downloads/19c9c7a8-4092-8b51-8000-0000dc3f3cd6_output.xlsx"

# 输出目录
output_dir = "/root/.openclaw/workspace/extracted_content"
os.makedirs(output_dir, exist_ok=True)

# 读取飞书文档成稿汇总
df = pd.read_excel(input_file, sheet_name='飞书文档成稿汇总')

# 按内容方向分组保存
for category in df['内容方向'].unique():
    if pd.isna(category):
        continue
    
    # 创建文件名
    filename = f"{category.replace('/', '_').replace(' ', '_')}.txt"
    filepath = os.path.join(output_dir, filename)
    
    # 提取该分类下的所有内容
    subset = df[df['内容方向'] == category]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# {category}\n")
        f.write(f"# 共 {len(subset)} 篇\n")
        f.write("="*60 + "\n\n")
        
        for idx, row in subset.iterrows():
            f.write(f"## 序号 {row['序号']}\n")
            f.write(f"交付时间: {row['交付时间']}\n")
            f.write("-"*40 + "\n")
            f.write(f"{row['成稿']}\n")
            f.write("\n" + "="*60 + "\n\n")
    
    print(f"✓ 已保存: {filename} ({len(subset)} 篇)")

print(f"\n所有内容已提取到: {output_dir}")
print(f"\n文件列表:")
for f in sorted(os.listdir(output_dir)):
    print(f"  - {f}")
