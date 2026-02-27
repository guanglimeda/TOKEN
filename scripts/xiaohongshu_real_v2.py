#!/usr/bin/env python3
"""
小红书真实数据爬取 - 优化版
使用Cookie登录，爬取真实数据
"""

import json
import time
import random
from datetime import datetime
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ Playwright未安装")
    exit(1)

COOKIE_FILE = "/root/.openclaw/workspace/config/xiaohongshu_cookie.txt"
OUTPUT_DIR = Path("/root/.openclaw/workspace/knowledge/xiaohongshu_epidemic/raw_real")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 所有关键词
KEYWORDS = [
    "减肥药", "GLP-1", "减肥针", "司美格鲁肽", "替尔泊肽", "玛仕度肽", "利拉鲁肽",
    "节后减肥", "换季瘦身", "快速变瘦",
    "减肥", "减脂", "变瘦", "瘦身", "减重", "脂肪", "BMI", "小基数", "大基数",
    "生酮饮食", "高蛋白饮食", "断碳"
]

def load_cookies():
    """加载Cookie"""
    with open(COOKIE_FILE, 'r') as f:
        cookie_str = f.read().strip()
    
    cookies = []
    for item in cookie_str.split(';'):
        item = item.strip()
        if '=' in item:
            name, value = item.split('=', 1)
            cookies.append({
                'name': name,
                'value': value,
                'domain': '.xiaohongshu.com',
                'path': '/'
            })
    return cookies

def crawl_real_data(keyword, max_notes=30):
    """真实爬取"""
    print(f"\n🔍 {keyword}")
    
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        
        cookies = load_cookies()
        context.add_cookies(cookies)
        
        page = context.new_page()
        
        try:
            search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}"
            print(f"  访问中...")
            page.goto(search_url, wait_until='networkidle', timeout=60000)
            time.sleep(5)
            
            # 提取数据 - 优化选择器
            notes = page.evaluate('''() => {
                const items = document.querySelectorAll('section.note-item, .feeds-page .note-item');
                const data = [];
                items.forEach((item, index) => {
                    if (index >= 30) return;
                    
                    // 尝试多种选择器
                    const titleEl = item.querySelector('.title, .note-title, a span');
                    const authorEl = item.querySelector('.author, .user-name');
                    const likeEl = item.querySelector('.like-wrapper span, .count, .interaction span');
                    const linkEl = item.querySelector('a');
                    
                    const title = titleEl ? titleEl.textContent.trim() : '';
                    const author = authorEl ? authorEl.textContent.trim() : '';
                    const likes = likeEl ? likeEl.textContent.trim() : '';
                    const href = linkEl ? linkEl.getAttribute('href') : '';
                    const link = href ? (href.startsWith('http') ? href : 'https://www.xiaohongshu.com' + href) : '';
                    
                    if (title && title.length > 5) {
                        data.push({ title, author, likes, url: link });
                    }
                });
                return data;
            }''')
            
            results = notes[:max_notes]
            print(f"  ✅ 获取 {len(results)} 条")
            
        except Exception as e:
            print(f"  ❌ 错误: {str(e)[:50]}")
        finally:
            browser.close()
    
    return results

def main():
    print("="*60)
    print("小红书真实数据爬取")
    print("="*60)
    print(f"目标: {len(KEYWORDS)}个关键词\n")
    
    total = 0
    for keyword in KEYWORDS:
        results = crawl_real_data(keyword, max_notes=30)
        
        if results:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = OUTPUT_DIR / f"{keyword}_{timestamp}_real.json"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    'keyword': keyword,
                    'crawl_time': datetime.now().isoformat(),
                    'total_count': len(results),
                    'notes': results,
                    'source': 'xiaohongshu',
                    'status': 'real_data'
                }, f, ensure_ascii=False, indent=2)
            
            print(f"  💾 保存 {len(results)}条")
            total += len(results)
        
        time.sleep(random.uniform(2, 4))
    
    print(f"\n{'='*60}")
    print(f"✅ 完成！共 {total} 条真实数据")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
