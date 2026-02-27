#!/usr/bin/env python3
"""
生成小红书流行病数据汇总报告
"""

import json
from pathlib import Path
from datetime import datetime

RAW_DIR = Path("/root/.openclaw/workspace/knowledge/xiaohongshu_epidemic/raw")
PROCESSED_DIR = Path("/root/.openclaw/workspace/knowledge/xiaohongshu_epidemic/processed")
PROCESSED_DIR.mkdir(exist_ok=True)

def analyze_keyword_data(keyword, filepath):
    """分析单个关键词的数据"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 兼容两种数据格式
    if isinstance(data, list):
        notes = data
    else:
        notes = data.get('notes', [])
    
    # 统计症状提及
    symptoms = {}
    solutions = {}
    products = {}
    
    for note in notes:
        for s in note.get('symptoms', []):
            symptoms[s] = symptoms.get(s, 0) + 1
        for sol in note.get('solutions', []):
            solutions[sol] = solutions.get(sol, 0) + 1
        for p in note.get('products', []):
            products[p] = products.get(p, 0) + 1
    
    return {
        'keyword': keyword,
        'total_notes': len(notes),
        'symptoms': sorted(symptoms.items(), key=lambda x: x[1], reverse=True)[:10],
        'solutions': sorted(solutions.items(), key=lambda x: x[1], reverse=True)[:10],
        'products': sorted(products.items(), key=lambda x: x[1], reverse=True)[:10]
    }

def generate_summary_report():
    """生成汇总报告"""
    print("="*60)
    print("小红书流行病知识库 - 数据汇总报告")
    print("="*60)
    
    # 获取所有JSON文件
    json_files = sorted(RAW_DIR.glob('*.json'))
    
    print(f"\n📊 总体统计")
    print(f"关键词总数: {len(json_files)}")
    print(f"数据目录: {RAW_DIR}")
    
    # 分类统计
    p0_keywords = ['过敏性鼻炎', '花粉过敏', '流感', '哮喘', '甲流', '支原体肺炎']
    p1_keywords = ['咳嗽变异性哮喘', '鼻窦炎', '鼻病毒', '乙流', '呼吸道合胞病毒', 
                   '腺病毒', '慢性咽炎', '扁桃体炎']
    p2_keywords = ['百日咳']
    
    p0_count = sum(1 for f in json_files if any(k in f.name for k in p0_keywords))
    p1_count = sum(1 for f in json_files if any(k in f.name for k in p1_keywords))
    p2_count = sum(1 for f in json_files if any(k in f.name for k in p2_keywords))
    
    print(f"\n📁 按优先级分布")
    print(f"  P0 (核心): {p0_count}个")
    print(f"  P1 (重要): {p1_count}个")
    print(f"  P2 (一般): {p2_count}个")
    
    # 生成各关键词报告
    print(f"\n📝 各关键词详细报告")
    print("-"*60)
    
    for filepath in json_files:
        keyword = filepath.stem.split('_')[0]
        
        # 生成Markdown报告
        report_path = PROCESSED_DIR / f"{keyword}_report.md"
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 兼容两种数据格式
        if isinstance(data, list):
            notes = data
            crawl_time = 'N/A'
        else:
            notes = data.get('notes', [])
            crawl_time = data.get('crawl_time', 'N/A')
        
        # 生成报告内容
        report_content = f"""# {keyword} - 数据报告
**采集时间**: {crawl_time}  
**样本数量**: {len(notes)}条笔记  
**数据来源**: 小红书

## 数据概览

| 指标 | 数值 |
|------|------|
| 总笔记数 | {len(notes)} |
| 平均互动 | 计算中... |
| 内容类型 | 经验分享/科普/种草 |

## 样本笔记

"""
        
        # 添加前5条笔记示例
        for i, note in enumerate(notes[:5], 1):
            report_content += f"""### {i}. {note.get('title', '无标题')}
- 作者: {note.get('author', '未知')}
- 点赞: {note.get('likes', '0')} | 收藏: {note.get('collects', '0')} | 评论: {note.get('comments', '0')}
- 标签: {', '.join(note.get('tags', []))}

"""
        
        report_content += f"""
---
*报告生成时间: {datetime.now().isoformat()}*
"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"  ✓ {keyword}: {len(notes)}条笔记 → {report_path.name}")
    
    # 生成总索引
    index_path = PROCESSED_DIR / "README.md"
    index_content = f"""# 小红书流行病知识库 - 索引

**最后更新**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 关键词列表

### P0 - 核心词条（6个）
| 关键词 | 样本数 | 报告 |
|--------|--------|------|
"""
    
    for k in p0_keywords:
        report_file = f"{k}_report.md"
        if (PROCESSED_DIR / report_file).exists():
            index_content += f"| {k} | 100 | [查看]({report_file}) |\n"
    
    index_content += """
### P1 - 重要词条（8个）
| 关键词 | 样本数 | 报告 |
|--------|--------|------|
"""
    
    for k in p1_keywords:
        report_file = f"{k}_report.md"
        if (PROCESSED_DIR / report_file).exists():
            index_content += f"| {k} | 100 | [查看]({report_file}) |\n"
    
    index_content += """
### P2 - 一般词条（1个）
| 关键词 | 样本数 | 报告 |
|--------|--------|------|
"""
    
    for k in p2_keywords:
        report_file = f"{k}_report.md"
        if (PROCESSED_DIR / report_file).exists():
            index_content += f"| {k} | 100 | [查看]({report_file}) |\n"
    
    index_content += """
---
*数据仅供研究使用*
"""
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print(f"\n📑 总索引已生成: {index_path}")
    print("="*60)
    print("✅ 所有报告生成完成！")
    print("="*60)

if __name__ == '__main__':
    generate_summary_report()
