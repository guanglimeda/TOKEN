#!/usr/bin/env python3
"""
Weibo Hot Search Crawler
抓取微博热搜并筛选医药/医美相关内容
"""
import requests
import json
import re
from datetime import datetime

def fetch_weibo_hot():
    """Fetch Weibo hot search list"""
    
    # Try multiple sources
    sources = [
        {
            "name": "vvhan",
            "url": "https://api.vvhan.com/api/hotlist/wb",
            "headers": {"User-Agent": "Mozilla/5.0"}
        },
        {
            "name": "tophub",
            "url": "https://www.tophub.today/c/weibo",
            "headers": {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
        }
    ]
    
    for source in sources:
        try:
            resp = requests.get(source["url"], headers=source["headers"], timeout=30)
            resp.raise_for_status()
            return parse_weibo_data(resp.text, source["name"])
        except Exception as e:
            print(f"Source {source['name']} failed: {e}")
            continue
    
    return None

def parse_weibo_data(html_or_json, source_name):
    """Parse weibo data from different sources"""
    
    if source_name == "vvhan":
        try:
            data = json.loads(html_or_json)
            if data.get("success") and "data" in data:
                items = []
                for i, item in enumerate(data["data"], 1):
                    items.append({
                        "rank": i,
                        "title": item.get("title", ""),
                        "hot": item.get("hot", ""),
                        "url": item.get("url", "")
                    })
                return items
        except:
            pass
    
    elif source_name == "tophub":
        # Parse HTML
        items = []
        # Look for title patterns
        pattern = r'"title":"([^"]+)".*?"rank":(\d+)'
        matches = re.findall(pattern, html_or_json)
        for title, rank in matches[:50]:
            items.append({
                "rank": int(rank),
                "title": title,
                "hot": "",
                "url": ""
            })
        return items
    
    return None

def filter_medical_topics(items):
    """Filter medical and aesthetic topics"""
    
    # Keywords for classification
    medical_keywords = ["药", "医药", "医疗", "医院", "医生", "病", "治疗", "疫苗", "健康", "医保", "新冠", "流感", "发烧", "感冒"]
    dental_keywords = ["牙", "口腔", "牙科", "牙齿", "矫正", "种植"]
    eye_keywords = ["眼", "眼科", "视力", "近视", "激光", "眼镜"]
    aesthetic_keywords = ["医美", "整形", "美容", "玻尿酸", "隆鼻", "双眼皮", "抽脂", "抗衰", "皮肤", "激光"]
    
    medical_items = []
    dental_items = []
    eye_items = []
    aesthetic_items = []
    
    for item in items:
        title = item.get("title", "")
        rank = item.get("rank", 999)
        
        # Check dental (rank <= 20)
        if rank <= 20 and any(kw in title for kw in dental_keywords):
            dental_items.append({**item, "category": "口腔牙科"})
            continue
        
        # Check eye (rank <= 20)
        if rank <= 20 and any(kw in title for kw in eye_keywords):
            eye_items.append({**item, "category": "眼科"})
            continue
        
        # Check aesthetic (rank <= 20)
        if rank <= 20 and any(kw in title for kw in aesthetic_keywords):
            aesthetic_items.append({**item, "category": "医美"})
            continue
        
        # Check medical (rank <= 13)
        if rank <= 13 and any(kw in title for kw in medical_keywords):
            medical_items.append({**item, "category": "医药"})
            continue
    
    return {
        "medical": medical_items,
        "dental": dental_items,
        "eye": eye_items,
        "aesthetic": aesthetic_items
    }

def format_message(results):
    """Format results for DingTalk"""
    
    now = datetime.now().strftime("%H:%M")
    lines = [f"微博 - 【微博热搜医药监测 - {now}】\n"]
    
    has_content = False
    
    for category, items in results.items():
        if items:
            has_content = True
            cat_name = items[0]["category"]
            lines.append(f"\n【{cat_name}】")
            for item in items:
                rank = item["rank"]
                title = item["title"]
                hot = item.get("hot", "")
                hot_str = f" ({hot})" if hot else ""
                lines.append(f"  {rank}. {title}{hot_str}")
    
    if not has_content:
        lines.append("\n本次暂无符合筛选条件的热搜话题。")
    
    return "\n".join(lines)

def send_to_dingtalk(message, webhook_url):
    """Send message to DingTalk"""
    
    payload = {
        "msgtype": "text",
        "text": {
            "content": message
        }
    }
    
    try:
        resp = requests.post(webhook_url, json=payload, timeout=30)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def main():
    # Fetch data
    items = fetch_weibo_hot()
    if not items:
        print("Failed to fetch weibo hot search")
        return
    
    print(f"Fetched {len(items)} items")
    
    # Filter
    results = filter_medical_topics(items)
    
    # Format
    message = format_message(results)
    print(message)
    
    # Send (optional, for testing)
    webhook = "https://oapi.dingtalk.com/robot/send?access_token=3db7259b8553e2bc2b61d16481c998a6443f3f223196412381d2a7f8d9bfe2ef"
    result = send_to_dingtalk(message, webhook)
    print(f"Send result: {result}")

if __name__ == "__main__":
    main()
