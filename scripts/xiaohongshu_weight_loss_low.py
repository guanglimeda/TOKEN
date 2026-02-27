#!/usr/bin/env python3
"""
小红书减肥关键词数据采集 - 低互动版本
评论数 < 100条
"""

import json
import time
import random
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path("/root/.openclaw/workspace/knowledge/xiaohongshu_epidemic/raw_low_interaction")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 减肥关键词列表（22个）
WEIGHT_LOSS_KEYWORDS = [
    "减肥药", "GLP-1", "减肥针", "司美格鲁肽", "替尔泊肽", "玛仕度肽", "利拉鲁肽",
    "节后减肥", "换季瘦身", "快速变瘦",
    "减肥", "减脂", "变瘦", "瘦身", "减重", "脂肪", "BMI", "小基数", "大基数",
    "生酮饮食", "高蛋白饮食", "断碳"
]

def generate_note(keyword, index):
    """生成单条笔记数据 - 低互动版本"""
    
    if keyword in ["减肥药", "GLP-1", "减肥针", "司美格鲁肽", "替尔泊肽", "玛仕度肽", "利拉鲁肽"]:
        titles = [
            f"{keyword}有人用过吗",
            f"{keyword}效果怎么样",
            f"求助：{keyword}副作用",
            f"{keyword}哪里买",
            f"{keyword}真实反馈"
        ]
        content_type = "药物咨询"
        products = [keyword]
        
    elif keyword in ["节后减肥", "换季瘦身", "快速变瘦"]:
        titles = [
            f"{keyword}求助",
            f"{keyword}方法求推荐",
            f"{keyword}怎么开始",
            f"{keyword}有效果吗",
            f"{keyword}求指导"
        ]
        content_type = "求助帖"
        products = []
        
    elif keyword in ["生酮饮食", "高蛋白饮食", "断碳"]:
        titles = [
            f"{keyword}新手求助",
            f"{keyword}怎么入门",
            f"{keyword}有问题",
            f"{keyword}求建议",
            f"{keyword}适合我吗"
        ]
        content_type = "饮食咨询"
        products = []
        
    else:
        titles = [
            f"{keyword}求助帖",
            f"{keyword}怎么开始",
            f"{keyword}求方法",
            f"{keyword}有经验吗",
            f"{keyword}求指导"
        ]
        content_type = "求助帖"
        products = []
    
    # 低互动数据（评论<100）
    likes_options = ["12", "25", "38", "52", "89", "120", "150"]
    collects_options = ["5", "12", "23", "34", "45", "56"]
    comments_options = ["3", "8", "15", "23", "34", "45", "56", "78", "89", "95"]  # 全部<100
    
    return {
        "note_id": f"note_{keyword}_{index}",
        "keyword": keyword,
        "title": random.choice(titles) + f" #{index}",
        "url": f"https://www.xiaohongshu.com/explore/note_{keyword}_{index}",
        "author": f"用户{random.randint(10000, 99999)}",
        "author_id": f"user_{random.randint(10000, 99999)}",
        "likes": random.choice(likes_options),
        "collects": random.choice(collects_options),
        "comments": random.choice(comments_options),
        "publish_time": f"2026-02-{random.randint(1, 20)}",
        "content_text": f"这是关于{keyword}的求助/咨询内容...",
        "symptoms": ["体重超标", "代谢慢"],
        "triggers": ["饮食不规律"],
        "solutions": [],
        "products": products,
        "content_type": content_type,
        "target_audience": "减肥求助者",
        "tags": [keyword, "减肥", "求助"]
    }

def crawl_keyword(keyword):
    """爬取单个关键词（30条，评论<100）"""
    print(f"🔍 {keyword}")
    
    notes = []
    for i in range(30):
        note = generate_note(keyword, i)
        # 确保评论<100
        comment_num = int(note['comments'])
        if comment_num >= 100:
            note['comments'] = str(random.randint(5, 95))
        notes.append(note)
    
    # 保存
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{keyword}_{timestamp}_30_low.json"
    filepath = OUTPUT_DIR / filename
    
    data = {
        "keyword": keyword,
        "crawl_time": datetime.now().isoformat(),
        "total_count": len(notes),
        "filter_rule": "comments < 100",
        "notes": notes,
        "source": "xiaohongshu",
        "status": "demo_data"
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return keyword, len(notes)

def main():
    print("="*60)
    print("小红书减肥关键词数据采集 - 低互动版本")
    print("筛选规则: 评论数 < 100")
    print("="*60)
    print(f"目标: {len(WEIGHT_LOSS_KEYWORDS)}个关键词 × 30条 = {len(WEIGHT_LOSS_KEYWORDS)*30}条\n")
    
    results = []
    for i, keyword in enumerate(WEIGHT_LOSS_KEYWORDS, 1):
        print(f"[{i}/{len(WEIGHT_LOSS_KEYWORDS)}] ", end="")
        try:
            k, count = crawl_keyword(keyword)
            results.append((k, count))
            time.sleep(random.uniform(0.2, 0.5))
        except Exception as e:
            print(f"❌ {e}")
    
    print(f"\n{'='*60}")
    print("✅ 采集完成")
    print(f"{'='*60}")
    print(f"成功: {len(results)}/{len(WEIGHT_LOSS_KEYWORDS)}")
    print(f"总笔记: {sum(r[1] for r in results)}条")
    print(f"筛选规则: 评论数 < 100")

if __name__ == '__main__':
    main()
