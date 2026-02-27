#!/usr/bin/env python3
"""
将减肥关键词JSON数据导出为Excel
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime

RAW_DIR = Path("/root/.openclaw/workspace/knowledge/xiaohongshu_epidemic/raw")
OUTPUT_DIR = Path("/root/.openclaw/workspace/knowledge/xiaohongshu_epidemic")

# 关键词列表
KEYWORDS = [
    "减肥药", "GLP-1", "减肥针", "司美格鲁肽", "替尔泊肽", "玛仕度肽", "利拉鲁肽",
    "节后减肥", "换季瘦身", "快速变瘦",
    "减肥", "减脂", "变瘦", "瘦身", "减重", "脂肪", "BMI", "小基数", "大基数",
    "生酮饮食", "高蛋白饮食", "断碳"
]

def load_notes(keyword):
    """加载关键词的所有笔记"""
    files = list(RAW_DIR.glob(f"{keyword}_*.json"))
    if not files:
        return []
    
    # 取最新的文件
    latest_file = max(files, key=lambda p: p.stat().st_mtime)
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    notes = data.get('notes', []) if isinstance(data, dict) else data
    return notes

def export_to_excel():
    """导出为Excel"""
    print("="*60)
    print("导出减肥关键词数据到Excel")
    print("="*60)
    
    all_data = []
    
    for keyword in KEYWORDS:
        print(f"📂 加载: {keyword}")
        notes = load_notes(keyword)
        
        for note in notes:
            row = {
                '关键词': keyword,
                '笔记ID': note.get('note_id', ''),
                '标题': note.get('title', ''),
                '链接': note.get('url', ''),
                '作者': note.get('author', ''),
                '作者ID': note.get('author_id', ''),
                '点赞数': note.get('likes', ''),
                '收藏数': note.get('collects', ''),
                '评论数': note.get('comments', ''),
                '发布时间': note.get('publish_time', ''),
                '内容类型': note.get('content_type', ''),
                '目标人群': note.get('target_audience', ''),
                '症状/需求': ', '.join(note.get('symptoms', [])),
                '触发因素': ', '.join(note.get('triggers', [])),
                '解决方案': ', '.join(note.get('solutions', [])),
                '产品提及': ', '.join(note.get('products', [])),
                '标签': ', '.join(note.get('tags', [])),
                '正文内容': note.get('content_text', '')
            }
            all_data.append(row)
    
    # 创建DataFrame
    df = pd.DataFrame(all_data)
    
    # 导出Excel
    output_file = OUTPUT_DIR / f"小红书减肥关键词数据_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='减肥数据', index=False)
        
        # 调整列宽
        worksheet = writer.sheets['减肥数据']
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
    print(f"{'='*60}")
    print(f"文件: {output_file}")
    print(f"总记录: {len(df)}条")
    print(f"关键词: {df['关键词'].nunique()}个")
    print(f"{'='*60}")
    
    return output_file

if __name__ == '__main__':
    export_to_excel()
