#!/usr/bin/env python3
"""
导出低互动版本Excel
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime

RAW_DIR = Path("/root/.openclaw/workspace/knowledge/xiaohongshu_epidemic/raw_low_interaction")
OUTPUT_DIR = Path("/root/.openclaw/workspace/knowledge/xiaohongshu_epidemic")

KEYWORDS = [
    "减肥药", "GLP-1", "减肥针", "司美格鲁肽", "替尔泊肽", "玛仕度肽", "利拉鲁肽",
    "节后减肥", "换季瘦身", "快速变瘦",
    "减肥", "减脂", "变瘦", "瘦身", "减重", "脂肪", "BMI", "小基数", "大基数",
    "生酮饮食", "高蛋白饮食", "断碳"
]

def load_notes(keyword):
    files = list(RAW_DIR.glob(f"{keyword}_*.json"))
    if not files:
        return []
    latest_file = max(files, key=lambda p: p.stat().st_mtime)
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('notes', []) if isinstance(data, dict) else data

def export_to_excel():
    print("="*60)
    print("导出低互动版本Excel (评论<100)")
    print("="*60)
    
    all_data = []
    for keyword in KEYWORDS:
        print(f"📂 {keyword}")
        notes = load_notes(keyword)
        for note in notes:
            row = {
                '关键词': keyword,
                '笔记ID': note.get('note_id', ''),
                '标题': note.get('title', ''),
                '链接': note.get('url', ''),
                '作者': note.get('author', ''),
                '点赞数': note.get('likes', ''),
                '收藏数': note.get('collects', ''),
                '评论数': note.get('comments', ''),
                '发布时间': note.get('publish_time', ''),
                '内容类型': note.get('content_type', ''),
                '症状/需求': ', '.join(note.get('symptoms', [])),
                '解决方案': ', '.join(note.get('solutions', [])),
                '产品提及': ', '.join(note.get('products', [])),
                '标签': ', '.join(note.get('tags', []))
            }
            all_data.append(row)
    
    df = pd.DataFrame(all_data)
    
    # 验证筛选规则
    comments_check = df['评论数'].astype(int) < 100
    print(f"\n筛选验证: {comments_check.sum()}/{len(df)} 条评论<100")
    
    output_file = OUTPUT_DIR / f"小红书减肥关键词数据_低互动版_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='低互动数据', index=False)
        worksheet = writer.sheets['低互动数据']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    print(f"\n{'='*60}")
    print(f"✅ Excel导出完成")
    print(f"文件: {output_file.name}")
    print(f"总记录: {len(df)}条")
    print(f"{'='*60}")
    
    return output_file

if __name__ == '__main__':
    export_to_excel()
