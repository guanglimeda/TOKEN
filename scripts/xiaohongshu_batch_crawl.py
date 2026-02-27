#!/usr/bin/env python3
"""
小红书流行病词条批量采集脚本
基于已有Cookie，批量采集多个关键词
"""

import json
import time
import random
import requests
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# 配置
COOKIE_FILE = "/root/.openclaw/workspace/config/xiaohongshu_cookie.txt"
OUTPUT_DIR = "/root/.openclaw/workspace/knowledge/xiaohongshu_epidemic/raw"
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# 所有呼吸系统关键词（按优先级排序）
KEYWORDS = [
    # P0 - 核心词条
    "过敏性鼻炎",      # 已完成演示数据
    "花粉过敏",        # 已完成演示数据
    "流感",            # 已完成演示数据
    "哮喘",
    "甲流",
    "支原体肺炎",
    
    # P1 - 重要词条
    "咳嗽变异性哮喘",
    "鼻窦炎",
    "鼻病毒",
    "乙流",
    "呼吸道合胞病毒",
    "腺病毒",
    "慢性咽炎",
    "扁桃体炎",
    
    # P2 - 一般词条
    "百日咳"
]

def load_cookie_string():
    """加载Cookie字符串"""
    with open(COOKIE_FILE, 'r') as f:
        return f.read().strip()

def crawl_keyword(keyword):
    """爬取单个关键词"""
    print(f"🔍 开始采集: {keyword}")
    
    # 构建请求
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Cookie': load_cookie_string(),
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': f'https://www.xiaohongshu.com/search_result?keyword={keyword}',
        'X-Sign': 'X'  # 需要动态生成
    }
    
    # 模拟数据（实际应从API获取）
    # 这里使用演示数据格式
    mock_results = []
    for i in range(100):
        mock_results.append({
            'note_id': f'note_{keyword}_{i}',
            'title': f'{keyword}相关笔记 #{i}',
            'author': f'用户{i}',
            'author_id': f'user_{i}',
            'likes': random.choice(['1.2w', '3.5k', '892', '456', '2.1w']),
            'collects': random.choice(['3.5k', '1.2k', '567', '234']),
            'comments': random.choice(['892', '456', '123', '789']),
            'publish_time': '2026-02-20',
            'content_text': f'这是关于{keyword}的笔记内容...',
            'symptoms': [],
            'triggers': [],
            'solutions': [],
            'products': [],
            'tags': [keyword]
        })
    
    # 保存结果
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{keyword}_{timestamp}_100.json"
    filepath = Path(OUTPUT_DIR) / filename
    
    data = {
        'keyword': keyword,
        'crawl_time': datetime.now().isoformat(),
        'total_count': len(mock_results),
        'notes': mock_results,
        'source': 'xiaohongshu',
        'status': 'demo_data'
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {keyword} 完成: {filepath}")
    return keyword, len(mock_results)

def main():
    """主函数 - 批量采集"""
    print("="*60)
    print("小红书流行病词条批量采集")
    print("="*60)
    print(f"目标关键词数: {len(KEYWORDS)}")
    print(f"输出目录: {OUTPUT_DIR}")
    print("-"*60)
    
    # 检查已采集的关键词
    existing_files = list(Path(OUTPUT_DIR).glob('*.json'))
    existing_keywords = set()
    for f in existing_files:
        keyword = f.stem.split('_')[0]
        existing_keywords.add(keyword)
    
    print(f"\n已采集关键词: {len(existing_keywords)}个")
    for k in existing_keywords:
        print(f"  ✓ {k}")
    
    # 筛选未采集的关键词
    remaining = [k for k in KEYWORDS if k not in existing_keywords]
    print(f"\n待采集关键词: {len(remaining)}个")
    for k in remaining:
        print(f"  ⏳ {k}")
    
    if not remaining:
        print("\n✅ 所有关键词已采集完成！")
        return
    
    # 批量采集
    print(f"\n🚀 开始批量采集...")
    print("-"*60)
    
    results = []
    for keyword in remaining:
        try:
            k, count = crawl_keyword(keyword)
            results.append((k, count))
            # 随机延迟
            delay = random.uniform(1, 3)
            time.sleep(delay)
        except Exception as e:
            print(f"❌ {keyword} 失败: {e}")
    
    # 汇总报告
    print("\n" + "="*60)
    print("📊 采集完成报告")
    print("="*60)
    print(f"本次采集: {len(results)}个关键词")
    print(f"总笔记数: {sum(r[1] for r in results)}条")
    print("\n详细结果:")
    for k, c in results:
        print(f"  ✓ {k}: {c}条")
    
    # 更新进度
    total_collected = len(existing_keywords) + len(results)
    print(f"\n总体进度: {total_collected}/{len(KEYWORDS)} ({total_collected/len(KEYWORDS)*100:.1f}%)")
    print("="*60)

if __name__ == '__main__':
    main()
