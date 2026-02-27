#!/usr/bin/env python3
"""
小红书真实数据爬取 - 使用Cookie登录
"""

import json
import time
import random
from datetime import datetime
from pathlib import Path

# 尝试导入playwright
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("❌ Playwright未安装")
    exit(1)

COOKIE_FILE = "/root/.openclaw/workspace/config/xiaohongshu_cookie.txt"
OUTPUT_DIR = Path("/root/.openclaw/workspace/knowledge/xiaohongshu_epidemic/raw_real")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

KEYWORDS = ["减肥药", "司美格鲁肽", "减肥"]

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
    """使用Playwright真实爬取"""
    print(f"\n🔍 真实爬取: {keyword}")
    
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        
        # 添加Cookie
        cookies = load_cookies()
        context.add_cookies(cookies)
        
        page = context.new_page()
        
        try:
            # 访问搜索页面
            search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}"
            print(f"  访问: {search_url}")
            page.goto(search_url, wait_until='networkidle', timeout=60000)
            
            # 等待内容加载
            time.sleep(5)
            
            # 提取笔记数据
            notes = page.evaluate('''() => {
                const items = document.querySelectorAll('section.note-item');
                const data = [];
                items.forEach((item, index) => {
                    if (index >= 30) return;
                    
                    const titleEl = item.querySelector('.title');
                    const authorEl = item.querySelector('.author');
                    const likeEl = item.querySelector('.like-wrapper span');
                    const linkEl = item.querySelector('a');
                    
                    const title = titleEl ? titleEl.textContent.trim() : '';
                    const author = authorEl ? authorEl.textContent.trim() : '';
                    const likes = likeEl ? likeEl.textContent.trim() : '0';
                    const link = linkEl ? 'https://www.xiaohongshu.com' + linkEl.getAttribute('href') : '';
                    
                    if (title) {
                        data.push({
                            title: title,
                            author: author,
                            likes: likes,
                            url: link
                        });
                    }
                });
                return data;
            }''')
            
            results = notes[:max_notes]
            print(f"  ✅ 获取 {len(results)} 条真实数据")
            
        except Exception as e:
            print(f"  ❌ 爬取失败: {e}")
        finally:
            browser.close()
    
    return results

def main():
    print("="*60)
    print("小红书真实数据爬取")
    print("="*60)
    
    for keyword in KEYWORDS:
        results = crawl_real_data(keyword, max_notes=30)
        
        if results:
            # 保存
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
            
            print(f"  💾 已保存: {filepath}")
        
        time.sleep(random.uniform(3, 5))
    
    print("\n" + "="*60)
    print("爬取完成")
    print("="*60)

if __name__ == '__main__':
    main()
