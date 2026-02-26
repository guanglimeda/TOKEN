#!/usr/bin/env python3
"""
微博热搜医药监测脚本
每小时执行，筛选医药/医美相关内容并发送
"""
import json
import requests
from datetime import datetime

def fetch_weibo():
    """Fetch weibo hot search"""
    try:
        # 使用 kimi_fetch 获取的数据格式
        url = "https://weibo.com/ajax/side/hotSearch"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=30)
        data = resp.json()
        return data.get('data', {}).get('realtime', [])
    except Exception as e:
        print(f"Fetch error: {e}")
        return []

def filter_topics(items):
    """Filter medical topics"""
    medical_keywords = ["药", "医药", "医疗", "医院", "医生", "病", "治疗", "疫苗", "健康", "医保", "新冠", "流感", "发烧", "感冒"]
    dental_keywords = ["牙", "口腔", "牙科", "牙齿", "矫正", "种植"]
    eye_keywords = ["眼", "眼科", "视力", "近视", "激光", "眼镜"]
    aesthetic_keywords = ["医美", "整形", "美容", "玻尿酸", "隆鼻", "双眼皮", "抽脂", "抗衰", "皮肤", "喷雾"]
    
    results = []
    for item in items:
        title = item.get('word', '')
        rank = item.get('realpos', 999)
        hot = item.get('num', 0)
        
        # 医美/皮肤类 (rank <= 20)
        if rank <= 20 and any(kw in title for kw in aesthetic_keywords):
            results.append({"rank": rank, "title": title, "hot": hot, "category": "医美/皮肤"})
            continue
        
        # 眼科 (rank <= 20)
        if rank <= 20 and any(kw in title for kw in eye_keywords):
            results.append({"rank": rank, "title": title, "hot": hot, "category": "眼科"})
            continue
        
        # 口腔牙科 (rank <= 20)
        if rank <= 20 and any(kw in title for kw in dental_keywords):
            results.append({"rank": rank, "title": title, "hot": hot, "category": "口腔牙科"})
            continue
        
        # 医药类 (rank <= 13)
        if rank <= 13 and any(kw in title for kw in medical_keywords):
            results.append({"rank": rank, "title": title, "hot": hot, "category": "医药"})
            continue
    
    return results

def format_message(results):
    """Format message for DingTalk"""
    now = datetime.now().strftime("%H:%M")
    
    if results:
        lines = [f"微博 - 【微博热搜医药监测 - {now}】\n"]
        current_cat = None
        for r in results:
            if r['category'] != current_cat:
                current_cat = r['category']
                lines.append(f"\n【{current_cat}】")
            lines.append(f"  排位{r['rank']}. {r['title']} (热度: {r['hot']})")
        return "\n".join(lines)
    else:
        return f"微博 - 【微博热搜医药监测 - {now}】\n\n本次暂无符合筛选条件的热搜话题。\n\n筛选规则：\n- 医药话题：排位13名以内\n- 口腔/眼科/医美：排位20名以内"

def main():
    items = fetch_weibo()
    if not items:
        print("Failed to fetch weibo data")
        return
    
    results = filter_topics(items)
    message = format_message(results)
    print(message)

if __name__ == "__main__":
    main()
