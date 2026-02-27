#!/usr/bin/env python3
"""
小红书笔记爬取脚本 - 简化版
使用模拟数据演示数据结构，后续接入真实API
"""

import json
import os
import random
from datetime import datetime

def generate_demo_data(keyword, count=100):
    """生成演示数据，展示数据结构"""
    notes = []
    
    # 基于关键词生成模拟数据
    templates = {
        '过敏性鼻炎': {
            'titles': [
                '春季鼻炎自救指南，亲测有效！',
                '过敏性鼻炎10年，终于找到方法',
                '鼻炎患者的日常护理心得',
                '花粉季来临，鼻炎患者如何防护',
                '洗鼻器使用教程，鼻炎福音',
                '过敏性鼻炎用药经验分享',
                '鼻炎康片真的有用吗？实测',
                '空调房里的鼻炎患者生存指南',
                '尘螨过敏引起的鼻炎怎么办',
                '鼻炎喷雾测评，哪款最有效'
            ],
            'symptoms': ['连续喷嚏', '鼻痒', '清水鼻涕', '鼻塞', '嗅觉减退'],
            'triggers': ['花粉', '尘螨', '冷空气', '空调', '宠物'],
            'solutions': ['鼻腔冲洗', '抗组胺药', '鼻用激素', '避免接触过敏原'],
            'products': ['雷诺考特', '辅舒良', '洗鼻器', '生理盐水', '氯雷他定']
        },
        '花粉过敏': {
            'titles': [
                '花粉季生存指南，过敏星人必看',
                '春季花粉过敏防护全攻略',
                '花粉过敏怎么办？医生教你',
                '我的花粉过敏治疗经历',
                '花粉过敏用药推荐',
                '出门必备！花粉过敏防护装备',
                '花粉过敏可以根治吗？',
                '花粉季眼睛痒怎么办',
                '花粉过敏和感冒的区别',
                '花粉过敏患者的春天'
            ],
            'symptoms': ['打喷嚏', '流鼻涕', '眼睛痒', '流泪', '鼻塞'],
            'triggers': ['花粉', '春天', '户外', '风天', '花园'],
            'solutions': ['戴口罩', '护目镜', '抗组胺药', '鼻腔冲洗', '避免外出'],
            'products': ['N95口罩', '护目镜', '氯雷他定', '洗鼻器', '空气净化器']
        },
        '流感': {
            'titles': [
                '流感高发季，如何科学预防',
                '甲流乙流区别，一文看懂',
                '流感疫苗要不要打？',
                '得了流感怎么办？居家护理',
                '流感症状识别，别当普通感冒',
                '儿童流感护理经验分享',
                '流感用药指南，奥司他韦怎么用',
                '流感后咳嗽不止怎么办',
                '预防流感的10个方法',
                '流感康复期注意事项'
            ],
            'symptoms': ['发烧', '头痛', '肌肉酸痛', '乏力', '咳嗽'],
            'triggers': ['季节交替', '人群密集', '免疫力低', '接触患者'],
            'solutions': ['多休息', '多喝水', '退烧药', '抗病毒药', '隔离'],
            'products': ['奥司他韦', '布洛芬', '对乙酰氨基酚', '体温计', '口罩']
        }
    }
    
    template = templates.get(keyword, templates['过敏性鼻炎'])
    
    for i in range(count):
        title = template['titles'][i % len(template['titles'])]
        
        # 模拟互动数据
        likes = random_interaction(100, 50000)
        collects = int(likes * 0.3)
        comments = int(likes * 0.1)
        
        note = {
            'keyword': keyword,
            'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'note_id': f'demo_{keyword}_{i:04d}',
            'title': f"{title} #{i+1}",
            'desc': f'这是关于{keyword}的笔记内容描述，包含症状、治疗方案和个人经验分享...',
            'url': f'https://www.xiaohongshu.com/explore/demo_{keyword}_{i:04d}',
            'author': f'用户{10000 + i}',
            'author_id': f'user_{10000 + i}',
            'likes': format_count(likes),
            'collects': format_count(collects),
            'comments': format_count(comments),
            'publish_time': f'2026-02-{20 + (i % 7):02d}',
            'tags': [keyword, '健康', '经验分享'],
            'symptoms': template['symptoms'][:random.randint(2, 5)],
            'triggers': template['triggers'][:random.randint(2, 5)],
            'solutions': template['solutions'][:random.randint(2, 4)],
            'products': template['products'][:random.randint(1, 4)],
            'content_type': ['经验分享', '科普知识', '种草推荐'][i % 3],
            'target_audience': ['患者', '家属', '健康人群'][i % 3]
        }
        notes.append(note)
    
    return notes

def random_interaction(min_val, max_val):
    """生成随机互动数"""
    import random
    return random.randint(min_val, max_val)

def format_count(count):
    """格式化数字"""
    if count >= 10000:
        return f"{count/10000:.1f}w"
    elif count >= 1000:
        return f"{count/1000:.1f}k"
    return str(count)

def generate_summary(notes, keyword):
    """生成汇总报告"""
    if not notes:
        return None
    
    total = len(notes)
    
    # 统计症状
    symptom_count = {}
    for note in notes:
        for s in note.get('symptoms', []):
            symptom_count[s] = symptom_count.get(s, 0) + 1
    top_symptoms = sorted(symptom_count.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # 统计解决方案
    solution_count = {}
    for note in notes:
        for s in note.get('solutions', []):
            solution_count[s] = solution_count.get(s, 0) + 1
    top_solutions = sorted(solution_count.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # 统计产品
    product_count = {}
    for note in notes:
        for p in note.get('products', []):
            product_count[p] = product_count.get(p, 0) + 1
    top_products = sorted(product_count.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # 生成Markdown
    lines = [f"# {keyword} - 数据报告"]
    lines.append(f"**采集时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**样本数量**: {total}条笔记\n")
    lines.append("> ⚠️ 注意：当前为演示数据，展示数据结构。真实数据需要通过浏览器自动化或API获取。\n")
    
    lines.append("## 热门症状提及")
    lines.append("| 症状 | 提及次数 | 占比 |")
    lines.append("|------|----------|------|")
    for symptom, count in top_symptoms:
        pct = count / total * 100
        lines.append(f"| {symptom} | {count} | {pct:.1f}% |")
    lines.append("")
    
    lines.append("## 热门解决方案")
    lines.append("| 方案 | 提及次数 | 占比 |")
    lines.append("|------|----------|------|")
    for solution, count in top_solutions:
        pct = count / total * 100
        lines.append(f"| {solution} | {count} | {pct:.1f}% |")
    lines.append("")
    
    lines.append("## 热门产品提及")
    lines.append("| 产品 | 提及次数 | 占比 |")
    lines.append("|------|----------|------|")
    for product, count in top_products:
        pct = count / total * 100
        lines.append(f"| {product} | {count} | {pct:.1f}% |")
    lines.append("")
    
    lines.append("## 高互动笔记TOP5")
    sorted_notes = sorted(notes, key=lambda x: parse_count(x['likes']), reverse=True)[:5]
    for i, note in enumerate(sorted_notes, 1):
        lines.append(f"{i}. {note['title']}")
        lines.append(f"   - 作者: {note['author']}")
        lines.append(f"   - 点赞: {note['likes']} | 收藏: {note['collects']} | 评论: {note['comments']}")
        lines.append(f"   - 症状: {', '.join(note['symptoms'])}")
        lines.append(f"   - 方案: {', '.join(note['solutions'])}")
        lines.append("")
    
    return '\n'.join(lines)

def parse_count(count_str):
    """解析数字"""
    if not count_str:
        return 0
    count_str = str(count_str).lower()
    if 'w' in count_str:
        return int(float(count_str.replace('w', '')) * 10000)
    elif 'k' in count_str:
        return int(float(count_str.replace('k', '')) * 1000)
    try:
        return int(count_str)
    except:
        return 0

def save_data(notes, keyword):
    """保存数据"""
    if not notes:
        return None
    
    # 确保目录存在
    raw_dir = '/root/.openclaw/workspace/knowledge/xiaohongshu_epidemic/raw'
    processed_dir = '/root/.openclaw/workspace/knowledge/xiaohongshu_epidemic/processed'
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)
    
    # 保存原始数据
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    raw_file = os.path.join(raw_dir, f"{keyword}_{timestamp}_{len(notes)}.json")
    with open(raw_file, 'w', encoding='utf-8') as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)
    
    # 生成并保存报告
    summary = generate_summary(notes, keyword)
    summary_file = os.path.join(processed_dir, f"{keyword}_summary.md")
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    return raw_file, summary_file

def main():
    random.seed(42)  # 保证可重复性
    
    keywords = ['过敏性鼻炎', '花粉过敏', '流感']
    
    print("="*60)
    print("小红书流行病词条爬取任务 (演示模式)")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    print("\n⚠️ 当前为演示数据，展示数据结构和分析维度")
    print("真实数据需要通过浏览器自动化或API获取\n")
    
    for keyword in keywords:
        print(f"\n正在生成 [{keyword}] 的演示数据...")
        notes = generate_demo_data(keyword, count=100)
        raw_file, summary_file = save_data(notes, keyword)
        print(f"✅ 原始数据: {raw_file}")
        print(f"✅ 分析报告: {summary_file}")
    
    print("\n" + "="*60)
    print("✅ 演示数据生成完成")
    print("="*60)
    print("\n文件位置:")
    print(f"  - 原始数据: /root/.openclaw/workspace/knowledge/xiaohongshu_epidemic/raw/")
    print(f"  - 分析报告: /root/.openclaw/workspace/knowledge/xiaohongshu_epidemic/processed/")

if __name__ == '__main__':
    main()
